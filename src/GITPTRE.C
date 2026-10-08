/* M176: verified recursive tree closure over generalized stage/index. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define OBJMAX 100000UL
#define OBJMAXSZ (16UL*1024UL*1024UL)
#define MEMMAX (64UL*1024UL*1024UL)
#define DEPTHMAX 256UL
#define W32 0xffffffffUL

struct idxent {
 unsigned char oid[20];
 unsigned long num;
 unsigned long size;
 int type;
 long offset;
 unsigned char state;
};

static struct idxent *ix;
static unsigned long ixtotal,ixunique;
static unsigned long trees,blobs,gitlinks,entries,verified;
static unsigned long largest,resident,peak;
static FILE *stage;
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
 if(n>MEMMAX-resident) {
  puts("TREE CLOSURE RESIDENT CAP");
  return 0;
 }
 p=(unsigned char *)malloc((size_t)(n?n:1));
 if(!p) return 0;
 resident+=n;
 if(resident>peak) peak=resident;
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
   resident-=n;
   free(p);
   return 0;
  }
  for(m=0;m<take;m++) {
   hi=nib((unsigned char)line[m*2]);
   lo=nib((unsigned char)line[m*2+1]);
   if(hi<0||lo<0) {
    resident-=n;
    free(p);
    return 0;
   }
   p[k+m]=(unsigned char)((hi<<4)|lo);
  }
 }
 *body=p;
 return 1;
}

static void freebody(unsigned char *p,unsigned long n) {
 if(p) {
  free(p);
  resident-=n;
 }
}

static int read_index(void) {
 FILE *f;
 char line[128],text[41],extra;
 unsigned long i,num,size,endtotal,endunique;
 int type,fields;
 f=fopen("dd:IDXIN","r");
 if(!f) {
  perror("IDXIN");
  return 0;
 }
 if(!linein(f,line,sizeof line)) goto bad;
 fields=sscanf(line,"PIDX1 %lu %lu %c",
               &ixtotal,&ixunique,&extra);
 if(fields!=2||ixtotal<1||ixtotal>OBJMAX||
    ixunique<1||ixunique>ixtotal) goto bad;
 ix=(struct idxent *)calloc((size_t)ixunique,sizeof *ix);
 if(!ix) goto bad;
 for(i=0;i<ixunique;i++) {
  if(!linein(f,line,sizeof line)) goto bad;
  fields=sscanf(line,"OID %40s %lu %d %lu %ld %c",
                text,&num,&type,&size,&ix[i].offset,&extra);
  if(fields!=5||num<1||num>ixtotal||
     type<1||type>4||size>OBJMAXSZ||ix[i].offset<0||
     !hexoid(text,ix[i].oid)) goto bad;
  if(i&&memcmp(ix[i-1].oid,ix[i].oid,20)>=0) goto bad;
  ix[i].num=num;ix[i].type=type;ix[i].size=size;
 }
 if(!linein(f,line,sizeof line)) goto bad;
 fields=sscanf(line,"PEND1 %lu %lu %c",
               &endtotal,&endunique,&extra);
 if(fields!=2||endtotal!=ixtotal||endunique!=ixunique)
  goto bad;
 if(linein(f,line,sizeof line)||ferror(f)) goto bad;
 if(fclose(f)!=0) return 0;
 return 1;
bad:
 puts("TREE CLOSURE INDEX INVALID");
 free(ix);ix=0;
 fclose(f);
 return 0;
}

static long locate(const unsigned char oid[20]) {
 unsigned long lo=0,hi=ixunique,mid;
 int c;
 while(lo<hi) {
  mid=lo+(hi-lo)/2;
  c=memcmp(ix[mid].oid,oid,20);
  if(c<0) lo=mid+1;
  else hi=mid;
 }
 if(lo>=ixunique||memcmp(ix[lo].oid,oid,20)!=0) return -1;
 return (long)lo;
}

static int fetch(long pos,unsigned char **body) {
 char line[128];
 unsigned char stored[20],got[20];
 unsigned long num,size;
 int type;
 if(pos<0||(unsigned long)pos>=ixunique) return 0;
 if(fseek(stage,ix[pos].offset,SEEK_SET)!=0||
    !linein(stage,line,sizeof line)||
    !parse_header(line,&num,&type,&size,stored)||
    num!=ix[pos].num||type!=ix[pos].type||
    size!=ix[pos].size||
    memcmp(stored,ix[pos].oid,20)!=0||
    !readbody(stage,size,body)||
    !object_oid(type,*body,size,got)||
    memcmp(got,stored,20)!=0) {
  if(*body) {
   freebody(*body,size);
   *body=0;
  }
  puts("TREE CLOSURE STAGE VERIFY FAIL");
  return 0;
 }
 if(size>largest) largest=size;
 return 1;
}

static int mode_value(const unsigned char *p,unsigned long n,
                      unsigned long *at,unsigned long *mode) {
 unsigned long v=0,digits=0;
 int c;
 while(*at<n&&p[*at]!=0x20) {
  c=p[*at];
  if(c<0x30||c>0x39||digits>=6) return 0;
  v=v*10+(unsigned long)(c-0x30);
  (*at)++;
  digits++;
 }
 if(digits==0||*at>=n||p[*at]!=0x20) return 0;
 (*at)++;
 *mode=v;
 return 1;
}

static int walk(long pos,unsigned long depth) {
 unsigned char *body=0,child[20];
 unsigned long at=0,name,mode;
 long cp;
 int ok=0;
 if(depth>DEPTHMAX) {
  puts("TREE CLOSURE DEPTH CAP");
  return 0;
 }
 if(ix[pos].state==2) return 1;
 if(ix[pos].state==1) {
  puts("TREE CLOSURE CYCLE");
  return 0;
 }
 if(ix[pos].type==3) {
  if(!fetch(pos,&body)) return 0;
  freebody(body,ix[pos].size);
  ix[pos].state=2;
  blobs++;verified++;
  if(verified%1000==0)
   printf("TREE CLOSURE PROGRESS %lu\n",verified);
  return 1;
 }
 if(ix[pos].type!=2) {
  puts("TREE CLOSURE CHILD TYPE FAIL");
  return 0;
 }
 ix[pos].state=1;
 if(!fetch(pos,&body)) goto done;
 trees++;verified++;
 while(at<ix[pos].size) {
  if(!mode_value(body,ix[pos].size,&at,&mode)) {
   puts("TREE CLOSURE MODE FAIL");
   goto done;
  }
  name=at;
  while(at<ix[pos].size&&body[at]!=0) {
   if(body[at]==0x2f) {
    puts("TREE CLOSURE NAME SLASH");
    goto done;
   }
   at++;
  }
  if(at==name||at>=ix[pos].size) {
   puts("TREE CLOSURE NAME FAIL");
   goto done;
  }
  at++;
  if(ix[pos].size-at<20) {
   puts("TREE CLOSURE SHORT OID");
   goto done;
  }
  memcpy(child,body+at,20);
  at+=20;
  entries++;
  if(mode==160000UL) {
   gitlinks++;
   continue;
  }
  cp=locate(child);
  if(cp<0) {
   puts("TREE CLOSURE CHILD MISSING");
   goto done;
  }
  if(mode==40000UL) {
   if(ix[cp].type!=2||!walk(cp,depth+1)) goto done;
  } else if(mode==100644UL||mode==100755UL||
            mode==120000UL) {
   if(ix[cp].type!=3||!walk(cp,depth+1)) goto done;
  } else {
   puts("TREE CLOSURE UNSUPPORTED MODE");
   goto done;
  }
 }
 ix[pos].state=2;
 ok=1;
done:
 freebody(body,ix[pos].size);
 if(!ok) ix[pos].state=0;
 if(ok&&verified%1000==0)
  printf("TREE CLOSURE PROGRESS %lu\n",verified);
 return ok;
}

static int run_walk(const char *text) {
 unsigned char root[20];
 long rp;
 int rc=8;
 if(strlen(text)!=40||!hexoid(text,root)) {
  puts("TREE WALK REQUIRES 40 HEX DIGITS");
  return 4;
 }
 if(!read_index()) return 8;
 rp=locate(root);
 if(rp<0||ix[rp].type!=2) {
  puts("TREE CLOSURE ROOT NOT TREE");
  goto done;
 }
 stage=fopen("dd:STGIN","r");
 if(!stage) {
  perror("STGIN");
  goto done;
 }
 printf("TREE CLOSURE ROOT ");
 printoid(stdout,root);
 putchar('\n');
 if(!walk(rp,0)) goto closeout;
 if(resident!=0) {
  puts("TREE CLOSURE RESIDENT LEAK");
  goto closeout;
 }
 printf("TREE CLOSURE TREES %lu BLOBS %lu GITLINKS %lu\n",
        trees,blobs,gitlinks);
 printf("TREE CLOSURE ENTRIES %lu VERIFIED %lu\n",
        entries,verified);
 printf("TREE CLOSURE MAX OBJECT %lu RESIDENT PEAK %lu\n",
        largest,peak);
 printf("TREE CLOSURE INDEX TOTAL %lu UNIQUE %lu\n",
        ixtotal,ixunique);
 puts("M176 TREE CLOSURE PASS");
 rc=0;
closeout:
 if(fclose(stage)!=0) rc=8;
 stage=0;
done:
 free(ix);ix=0;
 return rc;
}

int main(int argc,char **argv) {
 if(argc==3&&strcmp(argv[1],"WALK")==0)
  return run_walk(argv[2]);
 puts("Usage: GITPTRE WALK tree-oid");
 return 4;
}
