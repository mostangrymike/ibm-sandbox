/* M181: isolated LUT-validated selective stage scanner. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

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
 unsigned char selected;
 unsigned char *cache;
};

static unsigned long stage_lines[3];
static int stagephase;
static unsigned char validhex[256];
static struct idxent *ix;
static unsigned long ixtotal,ixunique;
static unsigned long trees,blobs,gitlinks,entries,verified;
static unsigned long largest,resident,peak;
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
 if(stagephase) stage_lines[stagephase]++;
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


/* Index object numbers let us inspect stage records in file order. */
static struct idxent **bynum;
static unsigned long stage_records,authenticated;

static int mapping(void) {
 unsigned long i,n;
 bynum=(struct idxent **)calloc((size_t)(ixtotal+1),sizeof *bynum);
 if(!bynum) return 0;
 for(i=0;i<ixunique;i++) {
  n=ix[i].num;
  if(n<1||n>ixtotal||bynum[n]) {
   puts("M181 INDEX NUMBER DUPLICATE");
   return 0;
  }
  bynum[n]=ix+i;
 }
 return 1;
}

/* Parse nonselected records without allocating their object bodies. */
/* Native C character codes (ASCII or EBCDIC) index this hex table. */
static void inithex(void) {
 int c;
 for(c='0';c<='9';c++) validhex[(unsigned char)c]=1;
 for(c='A';c<='F';c++) validhex[(unsigned char)c]=1;
 for(c='a';c<='f';c++) validhex[(unsigned char)c]=1;
}

static int skipbody(FILE *f,unsigned long size) {
 char line[128];
 unsigned long k,take,m;
 for(k=0;k<size;k+=take) {
  take=size-k;
  if(take>32) take=32;
  if(!linein(f,line,sizeof line)||strlen(line)!=take*2)
   return 0;
  for(m=0;m<take*2;m++)
   if(!validhex[(unsigned char)line[m]]) return 0;
 }
 if(size==0) {
  if(!linein(f,line,sizeof line)||line[0]) return 0;
 }
 return 1;
}

/* Pass 1 caches authenticated tree bodies; pass 2 verifies reachable
 * blobs only. Both use fopen/fgets and zero random fseek calls. */
static int scan(int pass) {
 FILE *f;
 struct idxent *e;
 char line[128];
 unsigned char oid[20],digest[20],*body=0;
 unsigned long i,num,size;
 long position;
 int type,ok=0,takeit;
 f=fopen("dd:STGIN","r");
 if(!f) {
  perror("STGIN");
  return 0;
 }
 stagephase=pass;
 for(i=1;i<=ixtotal;i++) {
  position=ftell(f);
  if(position<0||!linein(f,line,sizeof line)||
     !parse_header(line,&num,&type,&size,oid)||
     num!=i) goto done;
  stage_records++;
  e=bynum[i];
  if(e&&(e->num!=i||e->type!=type||e->size!=size||
         e->offset!=position||memcmp(e->oid,oid,20)!=0))
   goto done;
  takeit=e&&((pass==1&&type==2)||
             (pass==2&&type==3&&e->state==3));
  if(!takeit) {
   if(!skipbody(f,size)) goto done;
   continue;
  }
  body=0;
  if(!readbody(f,size,&body)) goto done;
  if(!object_oid(type,body,size,digest)||
     memcmp(digest,oid,20)!=0) {
   puts("M181 OBJECT SHA1 FAIL");
   goto done;
  }
  if(pass==1) {
   if(e->cache) goto done;
   e->cache=body;
   e->selected=1;
   body=0;
  } else {
   e->state=4;
   authenticated++;
   freebody(body,size);
   body=0;
  }
 }
 if(linein(f,line,sizeof line)||!feof(f)||ferror(f)) goto done;
 ok=1;
done:
 stagephase=0;
 if(body) freebody(body,size);
 if(fclose(f)!=0) ok=0;
 if(!ok) printf("M181 STAGE SCAN %d FAIL AT %lu\n",pass,i);
 return ok;
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

/* Resolve the graph solely against authenticated cached tree bodies.
 * Blob contents are not accepted until pass 2 verifies their SHA1. */
static int walk(long pos,unsigned long depth) {
 const unsigned char *body;
 unsigned char child[20];
 unsigned long at=0,name,mode;
 struct idxent *e;
 long cp;
 if(depth>DEPTHMAX) {
  puts("TREE CLOSURE DEPTH CAP");
  return 0;
 }
 e=ix+pos;
 if(e->state==2||e->state==3||e->state==4) return 1;
 if(e->state==1) {
  puts("TREE CLOSURE CYCLE");
  return 0;
 }
 if(e->type==3) {
  e->state=3;
  blobs++;verified++;
  if(e->size>largest) largest=e->size;
  return 1;
 }
 if(e->type!=2||!e->cache) {
  puts("TREE CLOSURE CHILD TYPE FAIL");
  return 0;
 }
 e->state=1;
 body=e->cache;
 trees++;verified++;
 if(e->size>largest) largest=e->size;
 while(at<e->size) {
  if(!mode_value(body,e->size,&at,&mode)) {
   puts("TREE CLOSURE MODE FAIL");
   return 0;
  }
  name=at;
  while(at<e->size&&body[at]) {
   if(body[at]==0x2f) {
    puts("TREE CLOSURE NAME SLASH");
    return 0;
   }
   at++;
  }
  if(at==name||at>=e->size) {
   puts("TREE CLOSURE NAME FAIL");
   return 0;
  }
  at++;
  if(e->size-at<20) {
   puts("TREE CLOSURE SHORT OID");
   return 0;
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
   return 0;
  }
  if(mode==40000UL) {
   if(ix[cp].type!=2||!walk(cp,depth+1)) return 0;
  } else if(mode==100644UL||mode==100755UL||
            mode==120000UL) {
   if(ix[cp].type!=3||!walk(cp,depth+1)) return 0;
  } else {
   puts("TREE CLOSURE UNSUPPORTED MODE");
   return 0;
  }
 }
 e->state=2;
 return 1;
}

static void release(void) {
 unsigned long i;
 if(ix) {
  for(i=0;i<ixunique;i++) {
   if(ix[i].cache) {
    freebody(ix[i].cache,ix[i].size);
    ix[i].cache=0;
   }
  }
 }
 free(bynum);bynum=0;
 free(ix);ix=0;
}

static void cpu_phase(const char *name,clock_t first,clock_t last) {
 if(first!=(clock_t)-1&&last!=(clock_t)-1&&last>=first)
  printf("M181 CPU %s %.3f\n",name,
         (double)(last-first)/(double)CLOCKS_PER_SEC);
 else printf("M181 CPU %s UNAVAILABLE\n",name);
}

static int run_walk(const char *text) {
 unsigned char root[20];
 long rp;
 int rc=8;
 unsigned long i,expected;
 clock_t t0,t1,t2,t3,t4;
 if(strlen(text)!=40||!hexoid(text,root)) {
  puts("TREE WALK REQUIRES 40 HEX DIGITS");
  return 4;
 }
 t0=clock();
 inithex();
 if(!read_index()) return 8;
 if(!mapping()) goto done;
 t1=clock();
 rp=locate(root);
 if(rp<0||ix[rp].type!=2) {
  puts("TREE CLOSURE ROOT NOT TREE");
  goto done;
 }
 if(!scan(1)) goto done;
 t2=clock();
 for(i=0;i<ixunique;i++) {
  if(ix[i].type==2&&!ix[i].selected) {
   puts("M181 INDEX TREE NOT FOUND IN STAGE");
   goto done;
  }
 }
 if(!walk(rp,0)) goto done;
 t3=clock();
 expected=blobs;
 if(!scan(2)) goto done;
 t4=clock();
 if(authenticated!=expected) {
  puts("M181 BLOB READBACK COUNT FAIL");
  goto done;
 }
 for(i=0;i<ixunique;i++) {
  if(ix[i].cache) {
   freebody(ix[i].cache,ix[i].size);
   ix[i].cache=0;
  }
 }
 if(resident!=0) {
  puts("TREE CLOSURE RESIDENT LEAK");
  goto done;
 }
 printf("TREE CLOSURE ROOT ");
 printoid(stdout,root);
 putchar('\n');
 printf("TREE CLOSURE TREES %lu BLOBS %lu GITLINKS %lu\n",
        trees,blobs,gitlinks);
 printf("TREE CLOSURE ENTRIES %lu VERIFIED %lu\n",
        entries,verified);
 printf("TREE CLOSURE MAX OBJECT %lu RESIDENT PEAK %lu\n",
        largest,peak);
 printf("TREE CLOSURE INDEX TOTAL %lu UNIQUE %lu\n",
        ixtotal,ixunique);
 printf("M181 FORWARD SCANS 2 RECORDS %lu SEEKS 0\n",stage_records);
 printf("M181 AUTHENTICATED BLOBS %lu\n",authenticated);
 printf("M181 STAGE LINES PASS1 %lu PASS2 %lu\n",
        stage_lines[1],stage_lines[2]);
 cpu_phase("INDEX",t0,t1);
 cpu_phase("TREE_SCAN",t1,t2);
 cpu_phase("GRAPH",t2,t3);
 cpu_phase("BLOB_SCAN",t3,t4);
 puts("M181 HEX LOOKUP VALIDATOR PASS");
 puts("M181 TREE CLOSURE PASS");
 rc=0;
done:
 release();
 return rc;
}

int main(int argc,char **argv) {
 if(argc==3&&strcmp(argv[1],"WALK")==0)
  return run_walk(argv[2]);
 puts("Usage: GITPHX WALK tree-oid");
 return 4;
}
