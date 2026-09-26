/* First-object PACK parser gate. C89, CMS hex-record input. */
#include <stdio.h>
#include <stdlib.h>
static int nib(int c) {
 if(c>='0'&&c<='9') return c-'0';
 if(c>='A'&&c<='F') return c-'A'+10;
 if(c>='a'&&c<='f') return c-'a'+10;
 return -1;
}
int main(void) {
 FILE *f;
 char line[256];
 unsigned char hdr[12];
 unsigned long count=0, size=0, zoff=0;
 int i,hi,lo,b,type=0,shift=4,state=0,ofs=0,ref=0;
 f=fopen("dd:PACKIN","r");
 if(!f) { perror("PACKIN"); return 8; }
 while(fgets(line,sizeof line,f)) {
  for(i=0;line[i];) {
   if(line[i]==' '||line[i]=='\n'||line[i]=='\r') {++i;continue;}
   hi=nib((unsigned char)line[i++]);
   if(hi<0||!line[i]) {puts("BAD HEX");fclose(f);return 8;}
   lo=nib((unsigned char)line[i++]);
   if(lo<0) {puts("BAD HEX");fclose(f);return 8;}
   b=(hi<<4)|lo;
   if(count<12) hdr[count]=(unsigned char)b;
   else if(state==0) {
    type=(b>>4)&7;size=(unsigned long)(b&15);
    state=(b&128)?1:((type==6)?2:((type==7)?3:4));
   } else if(state==1) {
    if(shift>28) {puts("SIZE OVERFLOW");fclose(f);return 8;}
    size|=((unsigned long)(b&127))<<shift;shift+=7;
    if(!(b&128)) state=(type==6)?2:((type==7)?3:4);
   } else if(state==2) {
    if(++ofs>8) {puts("OFS OVERFLOW");fclose(f);return 8;}
    if(!(b&128)) state=4;
   } else if(state==3) {
    if(++ref==20) state=4;
   }
   ++count;
   if(state==4 && zoff==0) zoff=count;
  }
 }
 if(ferror(f)) {puts("READ ERROR");fclose(f);return 8;}
 fclose(f);
 if(count!=340027UL||hdr[0]!=0x50||hdr[1]!=0x41||
    hdr[2]!=0x43||hdr[3]!=0x4b||state!=4) {
  puts("PACK HEADER FAIL");return 8;
 }
 printf("FIRST TYPE %d SIZE %lu ZLIB OFFSET %lu\n",type,size,zoff);
 puts("PASS FIRST OBJECT HEADER");
 return 0;
}
