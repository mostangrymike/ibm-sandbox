/* M13 first live PACK object: direct C -> GITNAPI gate. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
extern int gitnapi(unsigned long *);
static unsigned char input[1024];
static unsigned char output[1024];
static unsigned long param[6];
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
 while(fgets(line,sizeof line,f) && count<14+1024UL) {
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
 printf("INPUT %lu PREFIX",remaining);
 for(i=0;i<16;i++) printf(" %02X",(unsigned int)input[i]);
 putchar('\n');
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
