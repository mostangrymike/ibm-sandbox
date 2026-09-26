/* M13 first live PACK object: direct C -> GITNAPI gate. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
extern int gitnapi(unsigned long *);
static unsigned char input[1024];
static unsigned char output[1024];
static unsigned long param[6];
static unsigned char fixture[11]={0x78,0x9c,0x4b,0x4c,0x4a,0x06,0x00,0x02,0x4d,0x01,0x27};
static int nib(int c) {
 if(c>='0'&&c<='9') return c-'0';
 if(c>='A'&&c<='F') return c-'A'+10;
 if(c>='a'&&c<='f') return c-'a'+10;
 return -1;
}
int main(void) {
 FILE *f;
 char line[256];
 unsigned long count=0,used=0,remaining=0;
 int i,hi,lo,b,rc;
 f=fopen("dd:PACKIN","r");
 if(!f) {perror("PACKIN");return 8;}
 /* Read bounded compressed input starting at verified offset 14.
  * 1024 bytes is sufficient for the first 270-byte object gate.
  */
 while(count<14+1024UL && fgets(line,sizeof line,f)) {
  for(i=0;line[i] && count<14+1024UL;) {
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
 rc=gitnapi(param);
 printf("FIXTURE RC %d OUTPUT %lu USED %lu DATA %02X %02X %02X\\n",
        rc,param[4],param[5],output[0],output[1],output[2]);
 if(rc!=0 || param[4]!=3UL || param[5]!=11UL ||
    output[0]!='a' || output[1]!='b' || output[2]!='c') {
  puts("FAIL NATIVE ABI FIXTURE");return 8;
 }
 param[0]=(unsigned long)input;
 param[1]=remaining;
 param[2]=(unsigned long)output;
 param[3]=sizeof output;
 param[4]=0;
 param[5]=0;
 rc=gitnapi(param);
 printf("GITNAPI RC %d OUTPUT %lu USED %lu\n",
        rc,param[4],param[5]);
 if(rc!=0) return 8;
 used=param[5];
 if(param[4]!=270UL || used<6 || used>remaining) {
  puts("FAIL FIRST OBJECT LENGTH");return 8;
 }
 printf("SECOND OBJECT OFFSET %lu\n",14UL+used);
 puts("PASS FIRST LIVE OBJECT INFLATE");
 return 0;
}
