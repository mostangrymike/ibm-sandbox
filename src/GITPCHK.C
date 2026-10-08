/* M171: streaming verifier for generalized fetched PACK files. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define W32 0xffffffffUL

static unsigned long sh[5];
static unsigned char sbuf[64];
static unsigned int slen;
static unsigned long sbytes;

static unsigned long bxor(unsigned long a,unsigned long b) {
 return ((a|b)&(~(a&b)))&W32;
}

static unsigned long rol(unsigned long x,unsigned int n) {
 x&=W32;
 return ((x<<n)|(x>>(32-n)))&W32;
}

static void sblock(const unsigned char *p) {
 unsigned long w[80],a,b,c,d,e,t,f,k;
 unsigned int i;
 for(i=0;i<16;i++) {
  w[i]=((unsigned long)p[i*4]<<24)|
       ((unsigned long)p[i*4+1]<<16)|
       ((unsigned long)p[i*4+2]<<8)|
       (unsigned long)p[i*4+3];
 }
 for(i=16;i<80;i++)
  w[i]=rol(bxor(bxor(w[i-3],w[i-8]),
                bxor(w[i-14],w[i-16])),1);
 a=sh[0];b=sh[1];c=sh[2];d=sh[3];e=sh[4];
 for(i=0;i<80;i++) {
  if(i<20) {
   f=(b&c)|((~b)&d);k=0x5a827999UL;
  } else if(i<40) {
   f=bxor(bxor(b,c),d);k=0x6ed9eba1UL;
  } else if(i<60) {
   f=(b&c)|(b&d)|(c&d);k=0x8f1bbcdcUL;
  } else {
   f=bxor(bxor(b,c),d);k=0xca62c1d6UL;
  }
  t=(rol(a,5)+f+e+k+w[i])&W32;
  e=d;d=c;c=rol(b,30);b=a;a=t;
 }
 sh[0]=(sh[0]+a)&W32;sh[1]=(sh[1]+b)&W32;
 sh[2]=(sh[2]+c)&W32;sh[3]=(sh[3]+d)&W32;
 sh[4]=(sh[4]+e)&W32;
}

static void sinit(void) {
 sh[0]=0x67452301UL;sh[1]=0xefcdab89UL;
 sh[2]=0x98badcfeUL;sh[3]=0x10325476UL;
 sh[4]=0xc3d2e1f0UL;
 slen=0;sbytes=0;
}

static void supdate(unsigned char b) {
 sbuf[slen++]=b;
 sbytes++;
 if(slen==64) {
  sblock(sbuf);
  slen=0;
 }
}

static void sfinal(unsigned char out[20]) {
 unsigned long hi=(sbytes>>29)&W32;
 unsigned long lo=(sbytes<<3)&W32;
 unsigned int i;
 sbuf[slen++]=0x80;
 if(slen>56) {
  while(slen<64) sbuf[slen++]=0;
  sblock(sbuf);
  slen=0;
 }
 while(slen<56) sbuf[slen++]=0;
 for(i=0;i<4;i++)
  sbuf[slen++]=(unsigned char)(hi>>(24-i*8));
 for(i=0;i<4;i++)
  sbuf[slen++]=(unsigned char)(lo>>(24-i*8));
 sblock(sbuf);
 for(i=0;i<5;i++) {
  out[i*4]=(unsigned char)(sh[i]>>24);
  out[i*4+1]=(unsigned char)(sh[i]>>16);
  out[i*4+2]=(unsigned char)(sh[i]>>8);
  out[i*4+3]=(unsigned char)sh[i];
 }
}

static int nib(int c) {
 if(c>='0'&&c<='9') return c-'0';
 if(c>='A'&&c<='F') return c-'A'+10;
 if(c>='a'&&c<='f') return c-'a'+10;
 return -1;
}

int main(int argc,char **argv) {
 FILE *f;
 char line[256];
 unsigned char head[12],tail[20],trailer[20],digest[20];
 unsigned long total=0,objects,version;
 unsigned int tcount=0,tpos=0,i;
 int hi,lo,c;

 if(argc>2) {
  puts("Usage: GITPCHK [host-file]");
  return 4;
 }
 f=fopen(argc==2?argv[1]:"dd:PACKIN","r");
 if(!f) {
  perror("PACKIN");
  return 8;
 }
 sinit();
 while(fgets(line,sizeof line,f)) {
  for(i=0;line[i];) {
   c=(unsigned char)line[i++];
   if(c==' '||c=='\n'||c=='\r'||c=='\t') continue;
   hi=nib(c);
   if(hi<0||!line[i]) {
    puts("PACK VERIFY BAD HEX");
    fclose(f);
    return 8;
   }
   c=(unsigned char)line[i++];
   lo=nib(c);
   if(lo<0) {
    puts("PACK VERIFY BAD HEX");
    fclose(f);
    return 8;
   }
   c=(hi<<4)|lo;
   if(total<12) head[total]=(unsigned char)c;
   if(tcount<20) {
    tail[tcount++]=(unsigned char)c;
   } else {
    supdate(tail[tpos]);
    tail[tpos]=(unsigned char)c;
    tpos=(tpos+1)%20;
   }
   total++;
  }
 }
 if(ferror(f)) {
  puts("PACK VERIFY READ ERROR");
  fclose(f);
  return 8;
 }
 fclose(f);
 if(total<32||tcount!=20) {
  puts("PACK VERIFY TOO SHORT");
  return 8;
 }
 if(head[0]!=0x50||head[1]!=0x41||
    head[2]!=0x43||head[3]!=0x4b) {
  puts("PACK VERIFY SIGNATURE FAIL");
  return 8;
 }
 version=((unsigned long)head[4]<<24)|
         ((unsigned long)head[5]<<16)|
         ((unsigned long)head[6]<<8)|head[7];
 objects=((unsigned long)head[8]<<24)|
         ((unsigned long)head[9]<<16)|
         ((unsigned long)head[10]<<8)|head[11];
 if((version!=2&&version!=3)||objects<1) {
  puts("PACK VERIFY HEADER FAIL");
  return 8;
 }
 for(i=0;i<20;i++) trailer[i]=tail[(tpos+i)%20];
 sfinal(digest);
 if(memcmp(digest,trailer,20)!=0) {
  puts("PACK VERIFY SHA1 FAIL");
  printf("COMPUTED ");
  for(i=0;i<20;i++) printf("%02X",digest[i]);
  putchar('\n');
  printf("TRAILER ");
  for(i=0;i<20;i++) printf("%02X",trailer[i]);
  putchar('\n');
  return 8;
 }
 printf("PACK VERIFY BYTES %lu\n",total);
 printf("PACK VERIFY VERSION %lu OBJECTS %lu\n",version,objects);
 printf("PACK VERIFY SHA1 ");
 for(i=0;i<20;i++) printf("%02X",digest[i]);
 putchar('\n');
 puts("M171 PACK VERIFY PASS");
 return 0;
}
