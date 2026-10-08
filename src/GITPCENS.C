/* M172: generalized native PACK structural census. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int gitcapi(unsigned long *);

#define PACKMAX (16UL*1024UL*1024UL)
#define OBJMAX 100000UL

static unsigned long api[6];

static int nib(int c) {
 if(c>='0'&&c<='9') return c-'0';
 if(c>='A'&&c<='F') return c-'A'+10;
 if(c>='a'&&c<='f') return c-'a'+10;
 return -1;
}

static int scan_size(FILE *f,unsigned long *bytes) {
 char line[256];
 unsigned long n=0;
 int i,hi,lo;
 while(fgets(line,sizeof line,f)) {
  for(i=0;line[i];) {
   if(line[i]==' '||line[i]=='\n'||line[i]=='\r'||
      line[i]=='\t') {
    i++;
    continue;
   }
   hi=nib((unsigned char)line[i++]);
   if(hi<0||!line[i]) return 0;
   lo=nib((unsigned char)line[i++]);
   if(lo<0) return 0;
   if(n>=PACKMAX) return 0;
   n++;
  }
 }
 if(ferror(f)||n<32) return 0;
 *bytes=n;
 return 1;
}

static int load_pack(FILE *f,unsigned char *pack,unsigned long expect) {
 char line[256];
 unsigned long n=0;
 int i,hi,lo;
 while(fgets(line,sizeof line,f)) {
  for(i=0;line[i];) {
   if(line[i]==' '||line[i]=='\n'||line[i]=='\r'||
      line[i]=='\t') {
    i++;
    continue;
   }
   hi=nib((unsigned char)line[i++]);
   if(hi<0||!line[i]) return 0;
   lo=nib((unsigned char)line[i++]);
   if(lo<0||n>=expect) return 0;
   pack[n++]=(unsigned char)((hi<<4)|lo);
  }
 }
 return !ferror(f)&&n==expect;
}

static unsigned long be32(const unsigned char *p) {
 return ((unsigned long)p[0]<<24)|
        ((unsigned long)p[1]<<16)|
        ((unsigned long)p[2]<<8)|
        (unsigned long)p[3];
}

int main(void) {
 FILE *f;
 unsigned char *pack=0,*out=0;
 unsigned long bytes,count,version,pos,end,entry,start,size;
 unsigned long shift,dist,ordinary=0,ofs=0,ref=0,maxout=0;
 unsigned long maxused=0,used,outn;
 int b,type,rc;

 f=fopen("dd:PACKIN","r");
 if(!f) {
  perror("PACKIN");
  return 8;
 }
 if(!scan_size(f,&bytes)) {
  puts("CENSUS PACK SIZE/HEX FAIL");
  fclose(f);
  return 8;
 }
 if(fclose(f)!=0) return 8;

 pack=(unsigned char *)malloc((size_t)bytes);
 if(!pack) {
  puts("CENSUS PACK ALLOC FAIL");
  return 8;
 }
 f=fopen("dd:PACKIN","r");
 if(!f) {
  perror("PACKIN");
  free(pack);
  return 8;
 }
 if(!load_pack(f,pack,bytes)) {
  puts("CENSUS PACK LOAD FAIL");
  fclose(f);
  free(pack);
  return 8;
 }
 if(fclose(f)!=0) {
  free(pack);
  return 8;
 }

 if(pack[0]!=0x50||pack[1]!=0x41||
    pack[2]!=0x43||pack[3]!=0x4b) {
  puts("CENSUS PACK SIGNATURE FAIL");
  free(pack);
  return 8;
 }
 version=be32(pack+4);
 count=be32(pack+8);
 if((version!=2&&version!=3)||count<1||count>OBJMAX) {
  puts("CENSUS PACK HEADER FAIL");
  free(pack);
  return 8;
 }

 pos=12;
 end=bytes-20;
 for(entry=1;entry<=count;entry++) {
  if(pos>=end) {
   printf("CENSUS SHORT HEADER OBJ %lu\n",entry);
   free(pack);
   return 8;
  }
  start=pos;
  b=pack[pos++];
  type=(b>>4)&7;
  size=(unsigned long)(b&15);
  shift=4;
  while(b&128) {
   if(pos>=end||shift>28) {
    puts("CENSUS SIZE OVERFLOW");
    free(pack);
    return 8;
   }
   b=pack[pos++];
   size|=((unsigned long)(b&127))<<shift;
   shift+=7;
  }
  if(size>PACKMAX) {
   printf("CENSUS OBJECT CAP OBJ %lu SIZE %lu\n",entry,size);
   free(pack);
   return 8;
  }

  if(type>=1&&type<=4) {
   ordinary++;
  } else if(type==6) {
   if(pos>=end) {
    free(pack);
    return 8;
   }
   b=pack[pos++];
   dist=(unsigned long)(b&127);
   while(b&128) {
    if(pos>=end||dist>(PACKMAX>>7)) {
     free(pack);
     return 8;
    }
    b=pack[pos++];
    dist=((dist+1)<<7)|(unsigned long)(b&127);
   }
   if(dist==0||dist>start) {
    puts("CENSUS BAD OFS BASE");
    free(pack);
    return 8;
   }
   ofs++;
  } else if(type==7) {
   if(pos+20>end) {
    puts("CENSUS SHORT REF BASE");
    free(pack);
    return 8;
   }
   pos+=20;
   ref++;
  } else {
   printf("CENSUS BAD TYPE OBJ %lu TYPE %d\n",entry,type);
   free(pack);
   return 8;
  }

  if(pos>=end) {
   puts("CENSUS MISSING ZLIB");
   free(pack);
   return 8;
  }
  out=(unsigned char *)malloc((size_t)(size?size:1));
  if(!out) {
   puts("CENSUS OUTPUT ALLOC FAIL");
   free(pack);
   return 8;
  }
  api[0]=(unsigned long)(pack+pos);
  api[1]=end-pos;
  api[2]=(unsigned long)out;
  api[3]=size?size:1;
  api[4]=api[5]=0;
  rc=gitcapi(api);
  outn=api[4];
  used=api[5];
  free(out);
  out=0;
  if(rc!=0||outn!=size||used<1||used>end-pos) {
   printf("CENSUS INFLATE FAIL OBJ %lu RC %d OUT %lu USED %lu\n",
          entry,rc,outn,used);
   free(pack);
   return 8;
  }
  if(size>maxout) maxout=size;
  if(used>maxused) maxused=used;
  pos+=used;
  if(entry==1||entry==count||entry%1000==0)
   printf("CENSUS PROGRESS %lu OF %lu OFFSET %lu\n",
          entry,count,pos);
 }

 if(pos!=end) {
  printf("CENSUS END MISMATCH %lu EXPECT %lu\n",pos,end);
  free(pack);
  return 8;
 }
 printf("CENSUS PACK BYTES %lu VERSION %lu OBJECTS %lu\n",
        bytes,version,count);
 printf("CENSUS ORDINARY %lu OFS %lu REF %lu\n",
        ordinary,ofs,ref);
 printf("CENSUS MAX INFLATED %lu MAX COMPRESSED %lu\n",
        maxout,maxused);
 puts("M172 PACK CENSUS PASS");
 free(pack);
 return 0;
}
