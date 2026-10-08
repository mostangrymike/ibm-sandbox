/* M175: verified random access to generalized staged Git objects. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define OBJMAX 100000UL
#define OBJMAXSZ (16UL*1024UL*1024UL)
#define W32 0xffffffffUL

struct pick {
 unsigned char oid[20];
 unsigned long num;
 unsigned long size;
 int type;
 long offset;
};

static unsigned long sh[5];

static int nib(int c) {
 if(c>='0'&&c<='9') return c-'0';
 if(c>='A'&&c<='F') return c-'A'+10;
 if(c>='a'&&c<='f') return c-'a'+10;
 return -1;
}

static int linein(FILE *f,char *line,int cap) {
 int n;
 if(!fgets(line,cap,f)) return 0;
 n=(int)strlen(line);
 if(n==cap-1&&line[n-1]!='\n') return 0;
 while(n>0&&(line[n-1]=='\n'||line[n-1]=='\r'||
             line[n-1]==' ')) line[--n]=0;
 return n<=80;
}

static int hexoid(const char *s,unsigned char oid[20]) {
 int i,hi,lo;
 if(strlen(s)!=40) return 0;
 for(i=0;i<20;i++) {
  hi=nib((unsigned char)s[i*2]);
  lo=nib((unsigned char)s[i*2+1]);
  if(hi<0||lo<0) return 0;
  oid[i]=(unsigned char)((hi<<4)|lo);
 }
 return 1;
}

static void printoid(FILE *f,const unsigned char oid[20]) {
 static const char hex[]="0123456789ABCDEF";
 int i;
 for(i=0;i<20;i++) {
  fputc(hex[oid[i]>>4],f);
  fputc(hex[oid[i]&15],f);
 }
}

static unsigned long rol(unsigned long x,unsigned int n) {
 x&=W32;
 return ((x<<n)|(x>>(32-n)))&W32;
}

static unsigned long sxor(unsigned long a,unsigned long b) {
 return ((a|b)&(~(a&b)))&W32;
}

static void block(const unsigned char *p) {
 unsigned long w[80],a,b,c,d,e,t,fun,k;
 unsigned int i;
 for(i=0;i<16;i++)
  w[i]=((unsigned long)p[i*4]<<24)|
       ((unsigned long)p[i*4+1]<<16)|
       ((unsigned long)p[i*4+2]<<8)|p[i*4+3];
 for(i=16;i<80;i++)
  w[i]=rol(sxor(sxor(w[i-3],w[i-8]),
                sxor(w[i-14],w[i-16])),1);
 a=sh[0];b=sh[1];c=sh[2];d=sh[3];e=sh[4];
 for(i=0;i<80;i++) {
  if(i<20) {
   fun=(b&c)|((~b)&d);k=0x5a827999UL;
  } else if(i<40) {
   fun=sxor(sxor(b,c),d);k=0x6ed9eba1UL;
  } else if(i<60) {
   fun=(b&c)|(b&d)|(c&d);k=0x8f1bbcdcUL;
  } else {
   fun=sxor(sxor(b,c),d);k=0xca62c1d6UL;
  }
  t=(rol(a,5)+fun+e+k+w[i])&W32;
  e=d;d=c;c=rol(b,30);b=a;a=t;
 }
 sh[0]=(sh[0]+a)&W32;sh[1]=(sh[1]+b)&W32;
 sh[2]=(sh[2]+c)&W32;sh[3]=(sh[3]+d)&W32;
 sh[4]=(sh[4]+e)&W32;
}

static void initsha(void) {
 sh[0]=0x67452301UL;sh[1]=0xefcdab89UL;
 sh[2]=0x98badcfeUL;sh[3]=0x10325476UL;
 sh[4]=0xc3d2e1f0UL;
}

static void parts(const unsigned char *head,unsigned long hlen,
                  const unsigned char *body,unsigned long blen,
                  unsigned char digest[20]) {
 unsigned char b[64],tail[128];
 unsigned long total=hlen+blen,done=0,at,rem,bits;
 unsigned int i,j;
 initsha();
 while(total-done>=64) {
  for(i=0;i<64;i++) {
   at=done+(unsigned long)i;
   b[i]=at<hlen?head[at]:body[at-hlen];
  }
  block(b);
  done+=64;
 }
 rem=total-done;
 memset(tail,0,sizeof tail);
 for(i=0;i<rem;i++) {
  at=done+(unsigned long)i;
  tail[i]=at<hlen?head[at]:body[at-hlen];
 }
 tail[rem]=0x80;
 bits=total*8;
 for(i=0;i<8;i++)
  tail[(rem<56?56:120)+i]=
   (unsigned char)(i<4?0:(bits>>(8*(7-i))));
 block(tail);
 if(rem>=56) block(tail+64);
 for(i=0;i<5;i++) for(j=0;j<4;j++)
  digest[i*4+j]=(unsigned char)(sh[i]>>(24-j*8));
}

static const unsigned char types[5][7]={
 {0},
 {0x63,0x6f,0x6d,0x6d,0x69,0x74,0},
 {0x74,0x72,0x65,0x65,0,0,0},
 {0x62,0x6c,0x6f,0x62,0,0,0},
 {0x74,0x61,0x67,0,0,0,0}
};

static int object_oid(int type,const unsigned char *body,
                      unsigned long n,unsigned char oid[20]) {
 unsigned char head[32],digits[16];
 unsigned long rem=n;
 int i=0,j=0;
 if(type<1||type>4||n>OBJMAXSZ) return 0;
 while(types[type][i]) {
  head[i]=types[type][i];
  i++;
 }
 head[i++]=0x20;
 do {
  digits[j++]=(unsigned char)(0x30+rem%10);
  rem/=10;
 } while(rem);
 while(j) head[i++]=digits[--j];
 head[i++]=0;
 parts(head,(unsigned long)i,body,n,oid);
 return 1;
}

static int parse_header(const char *line,unsigned long *num,
                        int *type,unsigned long *size,
                        unsigned char oid[20]) {
 char text[41],extra;
 int fields;
 fields=sscanf(line,"OBJ %lu %d %lu %40s %c",
               num,type,size,text,&extra);
 return fields==4&&*num>=1&&*num<=OBJMAX&&
        *type>=1&&*type<=4&&*size<=OBJMAXSZ&&
        hexoid(text,oid);
}

static int readbody(FILE *f,unsigned long n,unsigned char **body) {
 unsigned char *p;
 char line[128];
 unsigned long k,m,take;
 int hi,lo;
 p=(unsigned char *)malloc((size_t)(n?n:1));
 if(!p) return 0;
 if(n==0) {
  if(!linein(f,line,sizeof line)||line[0]) {
   free(p);
   return 0;
  }
 }
 for(k=0;k<n;k+=take) {
  take=n-k;
  if(take>32) take=32;
  if(!linein(f,line,sizeof line)||strlen(line)!=take*2) {
   free(p);
   return 0;
  }
  for(m=0;m<take;m++) {
   hi=nib((unsigned char)line[m*2]);
   lo=nib((unsigned char)line[m*2+1]);
   if(hi<0||lo<0) {
    free(p);
    return 0;
   }
   p[k+m]=(unsigned char)((hi<<4)|lo);
  }
 }
 *body=p;
 return 1;
}

static int read_index(const unsigned char want[20],struct pick *pick,
                      unsigned long *total,unsigned long *unique) {
 FILE *f;
 char line[128],text[41],extra;
 unsigned char oid[20],prior[20];
 unsigned long i,num,size,endtotal,endunique;
 long offset;
 int type,fields,found=0;
 f=fopen("dd:IDXIN","r");
 if(!f) {
  perror("IDXIN");
  return 0;
 }
 if(!linein(f,line,sizeof line)) goto bad;
 fields=sscanf(line,"PIDX1 %lu %lu %c",total,unique,&extra);
 if(fields!=2||*total<1||*total>OBJMAX||
    *unique<1||*unique>*total) goto bad;
 for(i=0;i<*unique;i++) {
  if(!linein(f,line,sizeof line)) goto bad;
  fields=sscanf(line,"OID %40s %lu %d %lu %ld %c",
                text,&num,&type,&size,&offset,&extra);
  if(fields!=5||num<1||num>*total||
     type<1||type>4||size>OBJMAXSZ||offset<0||
     !hexoid(text,oid)) goto bad;
  if(i&&memcmp(prior,oid,20)>=0) goto bad;
  memcpy(prior,oid,20);
  if(memcmp(oid,want,20)==0) {
   if(found) goto bad;
   found=1;
   memcpy(pick->oid,oid,20);
   pick->num=num;pick->type=type;pick->size=size;
   pick->offset=offset;
  }
 }
 if(!linein(f,line,sizeof line)) goto bad;
 fields=sscanf(line,"PEND1 %lu %lu %c",
               &endtotal,&endunique,&extra);
 if(fields!=2||endtotal!=*total||endunique!=*unique)
  goto bad;
 if(linein(f,line,sizeof line)||ferror(f)) goto bad;
 if(fclose(f)!=0) return 0;
 if(!found) {
  puts("PACKOBJ OID NOT FOUND");
  return 0;
 }
 return 1;
bad:
 puts("PACKOBJ INDEX INVALID");
 fclose(f);
 return 0;
}

static int anib(int c) {
 if(c>=0x30&&c<=0x39) return c-0x30;
 if(c>=0x41&&c<=0x46) return c-0x41+10;
 if(c>=0x61&&c<=0x66) return c-0x61+10;
 return -1;
}

static int commit_oid40(const unsigned char *p,
                        unsigned char oid[20]) {
 int i,hi,lo;
 for(i=0;i<20;i++) {
  hi=anib((unsigned char)p[i*2]);
  lo=anib((unsigned char)p[i*2+1]);
  if(hi<0||lo<0) return 0;
  oid[i]=(unsigned char)((hi<<4)|lo);
 }
 return 1;
}

static int commit_summary(const unsigned char *p,unsigned long n) {
 static const unsigned char treep[5]={
  0x74,0x72,0x65,0x65,0x20
 };
 static const unsigned char parentp[7]={
  0x70,0x61,0x72,0x65,0x6e,0x74,0x20
 };
 unsigned long at=0,start,len,parents=0;
 unsigned char oid[20];
 int first=1;
 while(at<n) {
  start=at;
  while(at<n&&p[at]!=0x0a) at++;
  if(at>=n) return 0;
  len=at-start;
  if(len==0) break;
  if(first) {
   if(len!=45||memcmp(p+start,treep,5)!=0||
      !commit_oid40(p+start+5,oid)) return 0;
   printf("PACKOBJ COMMIT TREE ");
   printoid(stdout,oid);
   putchar('\n');
   first=0;
  } else if(len==47&&memcmp(p+start,parentp,7)==0) {
   if(!commit_oid40(p+start+7,oid)) return 0;
   printf("PACKOBJ COMMIT PARENT ");
   printoid(stdout,oid);
   putchar('\n');
   parents++;
  }
  at++;
 }
 if(first) return 0;
 printf("PACKOBJ COMMIT PARENTS %lu\n",parents);
 return 1;
}

static int read_object(const char *text,int emithex) {
 struct pick pick;
 unsigned char want[20],stored[20],got[20],*body=0;
 unsigned long total=0,unique=0,num,size,k,take,m;
 char line[128];
 int type;
 FILE *f;
 static const char hex[]="0123456789ABCDEF";

 if(strlen(text)!=40||!hexoid(text,want)) {
  puts("PACK-CAT REQUIRES 40 HEX DIGITS");
  return 4;
 }
 if(!read_index(want,&pick,&total,&unique)) return 8;
 f=fopen("dd:STGIN","r");
 if(!f) {
  perror("STGIN");
  return 8;
 }
 if(fseek(f,pick.offset,SEEK_SET)!=0||
    !linein(f,line,sizeof line)||
    !parse_header(line,&num,&type,&size,stored)||
    num!=pick.num||type!=pick.type||size!=pick.size||
    memcmp(stored,pick.oid,20)!=0||
    !readbody(f,size,&body)||
    !object_oid(type,body,size,got)||
    memcmp(got,pick.oid,20)!=0) {
  free(body);
  fclose(f);
  puts("PACKOBJ STAGE VERIFY FAIL");
  return 8;
 }
 if(fclose(f)!=0) {
  free(body);
  return 8;
 }
 printf("PACKOBJ OID ");
 printoid(stdout,pick.oid);
 putchar('\n');
 printf("PACKOBJ OBJ %lu TYPE %d SIZE %lu\n",
        pick.num,pick.type,pick.size);
 if(type==1&&!commit_summary(body,size)) {
  free(body);
  puts("PACKOBJ COMMIT FORMAT FAIL");
  return 8;
 }
 if(emithex) {
  if(size==0) puts("PACKOBJ HEX EMPTY");
  for(k=0;k<size;k+=take) {
   take=size-k;
   if(take>32) take=32;
   fputs("PACKOBJ HEX ",stdout);
   for(m=0;m<take;m++) {
    fputc(hex[body[k+m]>>4],stdout);
    fputc(hex[body[k+m]&15],stdout);
   }
   putchar('\n');
  }
 }
 free(body);
 printf("PACKOBJ INDEX TOTAL %lu UNIQUE %lu\n",total,unique);
 if(emithex) puts("M175 PACK CAT PASS");
 else puts("M175 PACK INFO PASS");
 return 0;
}

int main(int argc,char **argv) {
 if(argc==3&&strcmp(argv[1],"CAT")==0)
  return read_object(argv[2],1);
 if(argc==3&&strcmp(argv[1],"INFO")==0)
  return read_object(argv[2],0);
 puts("Usage: GITPCAT CAT|INFO oid");
 return 4;
}
