/* GITCWALK: first 20 live PACK objects, native C + GITCAPI.
 * Reads hex-record GITPBUF PACK through FILEDEF PACKIN.
 * No delta application yet: checks inflated delta instruction lengths.
 */
#include <stdio.h>
#include <stdlib.h>
extern int gitcapi(unsigned long *);
#define PACKCAP 340027UL
#define OUTCAP 65536UL
static unsigned char pack[340027];
static unsigned char output[65536];
static unsigned long api[6];
static int nib(int c) {
 if(c>='0'&&c<='9') return c-'0';
 if(c>='A'&&c<='F') return c-'A'+10;
 if(c>='a'&&c<='f') return c-'a'+10;
 return -1;
}
int main(void) {
 FILE *f;
 char line[256];
 unsigned long n=0,pos,size,used,base;
 unsigned long count,idx,shift;
 int i,hi,lo,b,type,rc;
 f=fopen("dd:PACKIN","r");
 if(!f) {perror("PACKIN");return 8;}
 while(fgets(line,sizeof line,f)) {
  for(i=0;line[i];) {
   if(line[i]==' '||line[i]=='\n'||
      line[i]=='\r') {++i;continue;}
   hi=nib((unsigned char)line[i++]);
   if(hi<0||!line[i]) {
    puts("BAD HEX");fclose(f);return 8;
   }
   lo=nib((unsigned char)line[i++]);
   if(lo<0||n>=PACKCAP) {
    puts("BAD HEX OR CAP");fclose(f);return 8;
   }
   pack[n++]=(unsigned char)((hi<<4)|lo);
  }
 }
 if(ferror(f)) {puts("READ ERROR");fclose(f);return 8;}
 fclose(f);
 if(n!=PACKCAP||pack[0]!='P'||pack[1]!='A'||
    pack[2]!='C'||pack[3]!='K') {
  puts("PACK HEADER FAIL");return 8;
 }
 count=((unsigned long)pack[8]<<24)|
       ((unsigned long)pack[9]<<16)|
       ((unsigned long)pack[10]<<8)|pack[11];
 printf("PACK BYTES %lu OBJECTS %lu\n",n,count);
 pos=12;
 for(idx=0;idx<20 && idx<count;idx++) {
  if(pos>=n-20) {puts("SHORT HEADER");return 8;}
  b=pack[pos++];
  type=(b>>4)&7;
  size=(unsigned long)(b&15);
  shift=4;
  while(b&128) {
   if(pos>=n-20||shift>28) {
    puts("SIZE OVERFLOW");return 8;
   }
   b=pack[pos++];
   size|=((unsigned long)(b&127))<<shift;
   shift+=7;
  }
  if(type==6) {
   /* OFS_DELTA base offset uses Git's offset encoding. */
   if(pos>=n-20) return 8;
   b=pack[pos++];
   base=(unsigned long)(b&127);
   while(b&128) {
    if(pos>=n-20) return 8;
    b=pack[pos++];
    base=((base+1)<<7)|(unsigned long)(b&127);
   }
   if(base>pos) {puts("BAD DELTA BASE");return 8;}
  } else if(type==7) {
   if(pos+20>n-20) return 8;
   pos+=20;
  } else if(type<1||type>4) {
   puts("BAD OBJECT TYPE");return 8;
  }
  if(pos>=n-20) return 8;
  api[0]=(unsigned long)(pack+pos);
  api[1]=n-20-pos;
  api[2]=(unsigned long)output;
  api[3]=OUTCAP;
  api[4]=api[5]=0;
  rc=gitcapi(api);
  printf("OBJ %lu TYPE %d SIZE %lu",
         idx+1,type,size);
  printf(" ZOFF %lu RC %d OUT %lu USED %lu\n",
         pos,rc,api[4],api[5]);
  if(rc!=0||api[5]==0||api[5]>api[1]||
     api[4]!=size) {
   puts("FAIL OBJECT INFLATE");return 8;
  }
  used=api[5];
  pos+=used;
 }
 printf("PASS %lu OBJECTS NEXT OFFSET %lu\n",
        idx,pos);
 return 0;
}
