/* M13 first two live PACK objects: direct C -> GITNAPI gate. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
extern int gitcapi(unsigned long *);
static unsigned char input[65536];
static unsigned char output[65536];
static unsigned long param[6];
static unsigned char fixture[11]={
 0x78,0x9c,0x4b,0x4c,0x4a,0x06,
 0x00,0x02,0x4d,0x01,0x27
};
static int nib(int c) {
 if(c>='0'&&c<='9') return c-'0';
 if(c>='A'&&c<='F') return c-'A'+10;
 if(c>='a'&&c<='f') return c-'a'+10;
 return -1;
}
int main(void) {
 FILE *f;
 char line[256];
 unsigned long count=0,used=0,remaining=0,pos=0,sz=0,zoff=0;
 int type=0,shift=4,ref=0,ofs=0;
 int i,hi,lo,b,rc;
 f=fopen("dd:PACKIN","r");
 if(!f) {perror("PACKIN");return 8;}
 /* Read bounded compressed input starting at verified offset 14.
  * Read ahead up to 64KB for the first two objects.
  */
 while(count<14+65536UL && fgets(line,sizeof line,f)) {
  for(i=0;line[i] && count<14+65536UL;) {
   if(line[i]==' '||line[i]=='\n'||line[i]=='\r') {++i;continue;}
   hi=nib((unsigned char)line[i++]);
   if(hi<0||!line[i]) {puts("BAD HEX");fclose(f);return 8;}
   lo=nib((unsigned char)line[i++]);
   if(lo<0) {puts("BAD HEX");fclose(f);return 8;}
   b=(hi<<4)|lo;
   if(count>=14) input[count-14]=(unsigned char)b;
   ++count;
  }
 }
 if(ferror(f)) {puts("READ ERROR");fclose(f);return 8;}
 fclose(f);
 if(count<=20) {puts("INPUT TOO SHORT");return 8;}
 remaining=count-14;
 if(remaining>sizeof input) {
  puts("FAIL INPUT BOUNDS");return 8;
 }
 printf("INPUT %lu PREFIX",remaining);
 for(i=0;i<16;i++) printf(" %02X",(unsigned int)input[i]);
 putchar('\n');
 param[0]=(unsigned long)fixture;
 param[1]=sizeof fixture;
 param[2]=(unsigned long)output;
 param[3]=sizeof output;
 param[4]=param[5]=0;
 rc=gitcapi(param);
 printf("FIXTURE RC %d OUTPUT %lu USED %lu DATA %02X %02X %02X\n",
        rc,param[4],param[5],output[0],output[1],output[2]);
 if(rc!=0 || param[4]!=3UL || param[5]!=11UL ||
    output[0]!=0x61 || output[1]!=0x62 || output[2]!=0x63) {
  puts("FAIL NATIVE ABI FIXTURE");return 8;
 }
 param[0]=(unsigned long)input;
 param[1]=remaining;
 param[2]=(unsigned long)output;
 param[3]=sizeof output;
 param[4]=0;
 param[5]=0;
 rc=gitcapi(param);
 printf("GITNAPI RC %d OUTPUT %lu USED %lu\n",
        rc,param[4],param[5]);
 if(rc!=0) return 8;
 used=param[5];
 if(param[4]!=270UL || used<6 || used>remaining) {
  puts("FAIL FIRST OBJECT LENGTH");return 8;
 }
 printf("SECOND OBJECT OFFSET %lu\n",14UL+used);
 puts("PASS FIRST LIVE OBJECT INFLATE");
 /* input starts at PACK offset 14; object two starts at 14+used. */
 pos=used;
 if(pos>=remaining) {puts("SECOND HEADER OUT OF RANGE");return 8;}
 b=input[pos++];
 type=(b>>4)&7;
 sz=(unsigned long)(b&15);
 while(b&128) {
  if(pos>=remaining || shift>28) {
   puts("SECOND SIZE HEADER INVALID");return 8;
  }
  b=input[pos++];
  sz|=((unsigned long)(b&127))<<shift;
  shift+=7;
 }
 if(type==6) {
  do {
   if(pos>=remaining || ++ofs>8) {
    puts("SECOND OFS HEADER INVALID");return 8;
   }
   b=input[pos++];
  } while(b&128);
 } else if(type==7) {
  if(remaining-pos<20) {
   puts("SECOND REF HEADER INVALID");return 8;
  }
  pos+=20;
  ref=20;
 }
 zoff=14+pos;
 printf("SECOND TYPE %d SIZE %lu ZLIB OFFSET %lu\\n",
        type,sz,zoff);
 if(type<1 || type>7 || type==5 || sz>sizeof output) {
  puts("SECOND OBJECT UNSUPPORTED");return 8;
 }
 if(pos>=remaining) {puts("SECOND ZLIB OUT OF RANGE");return 8;}
 param[0]=(unsigned long)(input+pos);
 param[1]=remaining-pos;
 param[2]=(unsigned long)output;
 param[3]=sizeof output;
 param[4]=param[5]=0;
 rc=gitcapi(param);
 printf("SECOND INFLATE RC %d OUTPUT %lu USED %lu\\n",
        rc,param[4],param[5]);
 if(rc!=0 || param[4]!=sz || param[5]<6 ||
    param[5]>remaining-pos) {
  puts("FAIL SECOND LIVE OBJECT");return 8;
 }
 printf("THIRD OBJECT OFFSET %lu\\n",zoff+param[5]);
 puts("PASS FIRST TWO LIVE OBJECTS");
 return 0;
}
