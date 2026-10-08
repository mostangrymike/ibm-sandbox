/* M172: generalized live PACK structural walk using native inflater. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int gitcapi(unsigned long *);

#define PACKMAX 16777216UL
#define OBJMAX 8388608UL
#define COUNTMAX 100000UL

static int nib(int c) {
 if(c>='0'&&c<='9') return c-'0';
 if(c>='A'&&c<='F') return c-'A'+10;
 if(c>='a'&&c<='f') return c-'a'+10;
 return -1;
}

int main(void) {
 FILE *f;
 char line[256];
 unsigned char *pack,*out;
 unsigned long api[6];
 unsigned long n=0,pos,start,size,shift,dist,count,idx;
 unsigned long ordinary=0,ofs=0,ref=0,used,totalout=0;
 unsigned long cap;
 int i,hi,lo,b,type,rc;

 pack=(unsigned char *)malloc(PACKMAX);
 if(!pack) {
  puts("GITLWALK: PACK ALLOC FAIL");
  return 8;
 }
 f=fopen("dd:PACKIN","r");
 if(!f) {
  perror("PACKIN");
  free(pack);
  return 8;
 }
 while(fgets(line,sizeof line,f)) {
  for(i=0;line[i];) {
   if(line[i]==' '||line[i]=='\n'||line[i]=='\r'||
      line[i]=='\t') {
    i++;
    continue;
   }
   hi=nib((unsigned char)line[i++]);
   if(hi<0||!line[i]) {
    puts("GITLWALK: BAD HEX");
    fclose(f);
    free(pack);
    return 8;
   }
   lo=nib((unsigned char)line[i++]);
   if(lo<0||n>=PACKMAX) {
    puts("GITLWALK: BAD HEX OR PACK LIMIT");
    fclose(f);
    free(pack);
    return 8;
   }
   pack[n++]=(unsigned char)((hi<<4)|lo);
  }
 }
 if(ferror(f)) {
  puts("GITLWALK: PACK READ ERROR");
  fclose(f);
  free(pack);
  return 8;
 }
 if(fclose(f)!=0) {
  puts("GITLWALK: PACK CLOSE ERROR");
  free(pack);
  return 8;
 }
 if(n<32||pack[0]!=0x50||pack[1]!=0x41||
    pack[2]!=0x43||pack[3]!=0x4b) {
  puts("GITLWALK: PACK HEADER FAIL");
  free(pack);
  return 8;
 }
 if(pack[4]!=0||pack[5]!=0||pack[6]!=0||
    (pack[7]!=2&&pack[7]!=3)) {
  puts("GITLWALK: PACK VERSION FAIL");
  free(pack);
  return 8;
 }
 count=((unsigned long)pack[8]<<24)|
       ((unsigned long)pack[9]<<16)|
       ((unsigned long)pack[10]<<8)|
       (unsigned long)pack[11];
 if(count<1||count>COUNTMAX) {
  puts("GITLWALK: PACK OBJECT COUNT LIMIT");
  free(pack);
  return 8;
 }
 printf("LIVE PACK BYTES %lu OBJECTS %lu\n",n,count);
 pos=12;
 for(idx=0;idx<count;idx++) {
  if(pos>=n-20) {
   puts("GITLWALK: SHORT OBJECT HEADER");
   free(pack);
   return 8;
  }
  start=pos;
  b=pack[pos++];
  type=(b>>4)&7;
  size=(unsigned long)(b&15);
  shift=4;
  while(b&128) {
   if(pos>=n-20||shift>60) {
    puts("GITLWALK: OBJECT SIZE OVERFLOW");
    free(pack);
    return 8;
   }
   b=pack[pos++];
   size|=((unsigned long)(b&127))<<shift;
   shift+=7;
  }
  if(size>OBJMAX) {
   printf("GITLWALK: OBJ %lu REPRESENTATION LIMIT %lu\n",
          idx+1,size);
   free(pack);
   return 8;
  }
  if(type>=1&&type<=4) {
   ordinary++;
  } else if(type==6) {
   if(pos>=n-20) {
    free(pack);
    return 8;
   }
   b=pack[pos++];
   dist=(unsigned long)(b&127);
   while(b&128) {
    if(pos>=n-20||dist>(PACKMAX>>7)) {
     puts("GITLWALK: OFS DISTANCE OVERFLOW");
     free(pack);
     return 8;
    }
    b=pack[pos++];
    dist=((dist+1)<<7)|(unsigned long)(b&127);
   }
   if(dist==0||dist>start) {
    puts("GITLWALK: BAD OFS DISTANCE");
    free(pack);
    return 8;
   }
   ofs++;
  } else if(type==7) {
   if(pos+20>n-20) {
    puts("GITLWALK: SHORT REF BASE");
    free(pack);
    return 8;
   }
   pos+=20;
   ref++;
  } else {
   puts("GITLWALK: BAD OBJECT TYPE");
   free(pack);
   return 8;
  }
  if(pos>=n-20) {
   puts("GITLWALK: MISSING ZLIB DATA");
   free(pack);
   return 8;
  }
  cap=size?size:1;
  out=(unsigned char *)malloc(cap);
  if(!out) {
   puts("GITLWALK: OBJECT ALLOC FAIL");
   free(pack);
   return 8;
  }
  api[0]=(unsigned long)(pack+pos);
  api[1]=n-20-pos;
  api[2]=(unsigned long)out;
  api[3]=cap;
  api[4]=api[5]=0;
  rc=gitcapi(api);
  free(out);
  if(rc!=0||api[5]==0||api[5]>api[1]||api[4]!=size) {
   printf("GITLWALK: INFLATE FAIL OBJ %lu RC %d OUT %lu USED %lu\n",
          idx+1,rc,api[4],api[5]);
   free(pack);
   return 8;
  }
  used=api[5];
  pos+=used;
  totalout+=size;
  if((idx+1)%512==0||idx==0||idx+1==count) {
   printf("LIVE WALK OBJ %lu TYPE %d SIZE %lu NEXT %lu\n",
          idx+1,type,size,pos);
  }
 }
 if(pos!=n-20) {
  printf("GITLWALK: PACK END MISMATCH %lu EXPECT %lu\n",
         pos,n-20);
  free(pack);
  return 8;
 }
 printf("LIVE WALK ORDINARY %lu OFS %lu REF %lu\n",
        ordinary,ofs,ref);
 printf("LIVE WALK INFLATED BYTES %lu\n",totalout);
 printf("M172 LIVE PACK STRUCTURAL WALK PASS %lu OBJECTS\n",count);
 free(pack);
 return 0;
}
