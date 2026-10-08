/* M173: generalized OFS PACK importer to CMS text stage. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int gitcapi(unsigned long *);

#define PACKMAX (16UL*1024UL*1024UL)
#define OBJMAX 100000UL
#define OBJMAXSZ (16UL*1024UL*1024UL)
#define RESMAX (64UL*1024UL*1024UL)
#define W32 0xffffffffUL

struct entry {
 unsigned long pos;
 unsigned long zoff;
 unsigned long repr;
 unsigned long used;
 unsigned long result;
 unsigned long deps;
 long base;
 int type;
 int rtype;
 unsigned char *live;
};

static unsigned long api[6];
static unsigned long sh[5];

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
   if(lo<0||n>=PACKMAX) return 0;
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

static unsigned long rol(unsigned long x,unsigned int n) {
 x&=W32;
 return ((x<<n)|(x>>(32-n)))&W32;
}

static unsigned long sxor(unsigned long a,unsigned long b) {
 return ((a|b)&(~(a&b)))&W32;
}

static void sha_block(const unsigned char *p) {
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

static void sha_init(void) {
 sh[0]=0x67452301UL;sh[1]=0xefcdab89UL;
 sh[2]=0x98badcfeUL;sh[3]=0x10325476UL;
 sh[4]=0xc3d2e1f0UL;
}

static void sha_parts(const unsigned char *head,unsigned long hlen,
                      const unsigned char *body,unsigned long blen,
                      unsigned char digest[20]) {
 unsigned char block[64],tail[128];
 unsigned long total=hlen+blen,done=0,at,rem,bits;
 unsigned int i,j;
 sha_init();
 while(total-done>=64) {
  for(i=0;i<64;i++) {
   at=done+(unsigned long)i;
   block[i]=at<hlen?head[at]:body[at-hlen];
  }
  sha_block(block);
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
 sha_block(tail);
 if(rem>=56) sha_block(tail+64);
 for(i=0;i<5;i++) for(j=0;j<4;j++)
  digest[i*4+j]=(unsigned char)(sh[i]>>(24-j*8));
}

static void sha_bytes(const unsigned char *p,unsigned long n,
                      unsigned char digest[20]) {
 static const unsigned char empty[1]={0};
 sha_parts(empty,0,p,n,digest);
}

static const unsigned char typascii[5][7]={
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
 while(typascii[type][i]) {
  head[i]=typascii[type][i];
  i++;
 }
 head[i++]=0x20;
 do {
  digits[j++]=(unsigned char)(0x30+rem%10);
  rem/=10;
 } while(rem);
 while(j) head[i++]=digits[--j];
 head[i++]=0;
 sha_parts(head,(unsigned long)i,body,n,oid);
 return 1;
}

static int dvar(const unsigned char *p,unsigned long n,
                unsigned long *at,unsigned long *v) {
 unsigned long x=0,shift=0;
 int b;
 do {
  if(*at>=n||shift>28) return 0;
  b=p[(*at)++];
  x|=((unsigned long)(b&127))<<shift;
  shift+=7;
 } while(b&128);
 *v=x;
 return 1;
}

static int delta_result(const unsigned char *p,unsigned long n,
                        unsigned long *base,unsigned long *result) {
 unsigned long at=0;
 return dvar(p,n,&at,base)&&dvar(p,n,&at,result);
}

static int dapply(const unsigned char *p,unsigned long n,
                  const unsigned char *base,unsigned long blen,
                  unsigned char *dst,unsigned long cap,
                  unsigned long *outlen) {
 unsigned long at=0,bs,rs,off,sz,w=0;
 int op,j;
 if(!dvar(p,n,&at,&bs)||!dvar(p,n,&at,&rs)) return 0;
 if(bs!=blen||rs>cap) return 0;
 while(at<n) {
  op=p[at++];
  if(op&128) {
   off=0;sz=0;
   for(j=0;j<4;j++) if(op&(1<<j)) {
    if(at>=n) return 0;
    off|=((unsigned long)p[at++])<<(j*8);
   }
   for(j=0;j<3;j++) if(op&(16<<j)) {
    if(at>=n) return 0;
    sz|=((unsigned long)p[at++])<<(j*8);
   }
   if(sz==0) sz=65536UL;
   if(off>blen||sz>blen-off||sz>rs-w) return 0;
   memcpy(dst+w,base+off,(size_t)sz);
   w+=sz;
  } else if(op) {
   if((unsigned long)op>n-at||
      (unsigned long)op>rs-w) return 0;
   memcpy(dst+w,p+at,(size_t)op);
   at+=(unsigned long)op;
   w+=(unsigned long)op;
  } else {
   return 0;
  }
 }
 if(w!=rs) return 0;
 *outlen=w;
 return 1;
}

static long find_pos(struct entry *e,unsigned long prior,
                     unsigned long pos) {
 unsigned long lo=0,hi=prior,mid;
 while(lo<hi) {
  mid=lo+(hi-lo)/2;
  if(e[mid].pos<pos) lo=mid+1;
  else hi=mid;
 }
 if(lo>=prior||e[lo].pos!=pos) return -1;
 return (long)lo;
}

static int inflate_one(const unsigned char *pack,unsigned long end,
                       unsigned long zoff,unsigned long size,
                       unsigned char **out,unsigned long *used) {
 unsigned char *p;
 int rc;
 if(zoff>=end||size>OBJMAXSZ) return 0;
 p=(unsigned char *)malloc((size_t)(size?size:1));
 if(!p) return 0;
 api[0]=(unsigned long)(pack+zoff);
 api[1]=end-zoff;
 api[2]=(unsigned long)p;
 api[3]=size?size:1;
 api[4]=api[5]=0;
 rc=gitcapi(api);
 if(rc!=0||api[4]!=size||api[5]<1||api[5]>end-zoff) {
  free(p);
  return 0;
 }
 *out=p;
 *used=api[5];
 return 1;
}

static int write_object(FILE *out,unsigned long idx,int type,
                        const unsigned char *body,unsigned long n,
                        const unsigned char oid[20]) {
 static const char hex[]="0123456789ABCDEF";
 char line[65];
 unsigned long k,m,take;
 if(fprintf(out,"OBJ %lu %d %lu ",idx,type,n)<0) return 0;
 for(k=0;k<20;k++) {
  line[k*2]=hex[oid[k]>>4];
  line[k*2+1]=hex[oid[k]&15];
 }
 line[40]=0;
 if(fputs(line,out)==EOF||fputc('\n',out)==EOF) return 0;
 for(k=0;k<n;k+=take) {
  take=n-k;
  if(take>32) take=32;
  for(m=0;m<take;m++) {
   line[m*2]=hex[body[k+m]>>4];
   line[m*2+1]=hex[body[k+m]&15];
  }
  line[take*2]=0;
  if(fputs(line,out)==EOF||fputc('\n',out)==EOF) return 0;
 }
 if(n==0&&fputc('\n',out)==EOF) return 0;
 return 1;
}

static int prepass(unsigned char *pack,unsigned long bytes,
                   struct entry *e,unsigned long count,
                   unsigned long *ordinary,unsigned long *ofs,
                   unsigned long *refs,unsigned long *maxrepr,
                   unsigned long *maxcomp) {
 unsigned long pos=12,end=bytes-20,idx,start,size,shift,dist,base;
 unsigned long used;
 unsigned char *repr;
 int b,type;
 long bi;
 for(idx=0;idx<count;idx++) {
  if(pos>=end) return 0;
  start=pos;
  b=pack[pos++];
  type=(b>>4)&7;
  size=(unsigned long)(b&15);
  shift=4;
  while(b&128) {
   if(pos>=end||shift>28) return 0;
   b=pack[pos++];
   size|=((unsigned long)(b&127))<<shift;
   shift+=7;
  }
  if(size>OBJMAXSZ) return 0;
  e[idx].pos=start;
  e[idx].repr=size;
  e[idx].type=type;
  e[idx].base=-1;
  if(type>=1&&type<=4) {
   (*ordinary)++;
  } else if(type==6) {
   if(pos>=end) return 0;
   b=pack[pos++];
   dist=(unsigned long)(b&127);
   while(b&128) {
    if(pos>=end||dist>(PACKMAX>>7)) return 0;
    b=pack[pos++];
    dist=((dist+1)<<7)|(unsigned long)(b&127);
   }
   if(dist==0||dist>start) return 0;
   base=start-dist;
   bi=find_pos(e,idx,base);
   if(bi<0) return 0;
   e[idx].base=bi;
   e[bi].deps++;
   (*ofs)++;
  } else if(type==7) {
   (*refs)++;
   printf("IMPORT REF DELTA UNSUPPORTED OBJ %lu\n",idx+1);
   return 0;
  } else {
   return 0;
  }
  e[idx].zoff=pos;
  if(!inflate_one(pack,end,pos,size,&repr,&used)) return 0;
  free(repr);
  e[idx].used=used;
  if(size>*maxrepr) *maxrepr=size;
  if(used>*maxcomp) *maxcomp=used;
  pos+=used;
  if(idx==0||idx+1==count||(idx+1)%1000==0)
   printf("IMPORT PREPASS %lu OF %lu OFFSET %lu\n",
          idx+1,count,pos);
 }
 return pos==end;
}

static void cleanup_live(struct entry *e,unsigned long count) {
 unsigned long i;
 if(!e) return;
 for(i=0;i<count;i++) {
  free(e[i].live);
  e[i].live=0;
 }
}

static int import_pack(int prechecked) {
 FILE *f,*out,*probe;
 unsigned char *pack=0,*repr=0,*body=0,digest[20],trailer[20];
 struct entry *e=0;
 unsigned long bytes,count=0,version,end,idx,used,bs,rs;
 unsigned long ordinary=0,ofs=0,refs=0,maxrepr=0,maxcomp=0;
 unsigned long maxresult=0,resident=0,peak=0;
 long bi;
 int rtype,ok=0;

 f=fopen("dd:PACKIN","r");
 if(!f) {
  perror("PACKIN");
  return 8;
 }
 if(!scan_size(f,&bytes)) {
  puts("IMPORT PACK SIZE/HEX FAIL");
  fclose(f);
  return 8;
 }
 if(fclose(f)!=0) return 8;
 pack=(unsigned char *)malloc((size_t)bytes);
 if(!pack) {
  puts("IMPORT PACK ALLOC FAIL");
  return 8;
 }
 f=fopen("dd:PACKIN","r");
 if(!f) {
  free(pack);
  return 8;
 }
 if(!load_pack(f,pack,bytes)) {
  puts("IMPORT PACK LOAD FAIL");
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
  puts("IMPORT PACK SIGNATURE FAIL");
  goto done;
 }
 version=be32(pack+4);
 count=be32(pack+8);
 if((version!=2&&version!=3)||count<1||count>OBJMAX) {
  puts("IMPORT PACK HEADER FAIL");
  goto done;
 }
 sha_bytes(pack,bytes-20,digest);
 memcpy(trailer,pack+bytes-20,20);
 if(memcmp(digest,trailer,20)!=0) {
  puts("IMPORT PACK SHA1 FAIL");
  goto done;
 }
 e=(struct entry *)calloc((size_t)count,sizeof *e);
 if(!e) {
  puts("IMPORT ENTRY ALLOC FAIL");
  goto done;
 }
 if(!prepass(pack,bytes,e,count,&ordinary,&ofs,&refs,
             &maxrepr,&maxcomp)) {
  puts("IMPORT PREPASS FAIL");
  goto done;
 }
 if(refs!=0) {
  puts("IMPORT REF COUNT FAIL");
  goto done;
 }

 /* CMS FILEDEF may open an absent DISK output for input.
  * PRECHECKED is allowed only after CMS STATE confirmed absence.
  * Preserve native existence guard for direct/host IMPORT.
  */
 if(!prechecked) {
  probe=fopen("dd:OBJOUT","r");
  if(probe) {
   fclose(probe);
   puts("IMPORT OUTPUT EXISTS");
   goto done;
  }
 }
 out=fopen("dd:OBJOUT","w");
 if(!out) {
  perror("OBJOUT");
  goto done;
 }
 end=bytes-20;
 for(idx=0;idx<count;idx++) {
  repr=0;
  body=0;
  if(!inflate_one(pack,end,e[idx].zoff,e[idx].repr,
                  &repr,&used)||used!=e[idx].used) {
   puts("IMPORT SECOND INFLATE FAIL");
   goto outfail;
  }
  if(e[idx].type>=1&&e[idx].type<=4) {
   body=repr;
   repr=0;
   rs=e[idx].repr;
   rtype=e[idx].type;
  } else {
   bi=e[idx].base;
   if(bi<0||(unsigned long)bi>=idx||!e[bi].live) {
    puts("IMPORT BASE NOT RESIDENT");
    goto outfail;
   }
   if(!delta_result(repr,e[idx].repr,&bs,&rs)||
      bs!=e[bi].result||rs>OBJMAXSZ) {
    puts("IMPORT DELTA HEADER FAIL");
    goto outfail;
   }
   body=(unsigned char *)malloc((size_t)(rs?rs:1));
   if(!body) {
    puts("IMPORT RESULT ALLOC FAIL");
    goto outfail;
   }
   if(!dapply(repr,e[idx].repr,e[bi].live,e[bi].result,
              body,rs,&used)||used!=rs) {
    puts("IMPORT DELTA APPLY FAIL");
    goto outfail;
   }
   free(repr);
   repr=0;
   rtype=e[bi].rtype;
   if(e[bi].deps==0) {
    puts("IMPORT DEPENDENCY UNDERFLOW");
    goto outfail;
   }
   e[bi].deps--;
   if(e[bi].deps==0) {
    resident-=e[bi].result;
    free(e[bi].live);
    e[bi].live=0;
   }
  }
  e[idx].result=rs;
  e[idx].rtype=rtype;
  if(rs>maxresult) maxresult=rs;
  if(!object_oid(rtype,body,rs,digest)) {
   puts("IMPORT OID FAIL");
   goto outfail;
  }
  if(!write_object(out,idx+1,rtype,body,rs,digest)) {
   puts("IMPORT STAGE WRITE FAIL");
   goto outfail;
  }
  if(e[idx].deps) {
   if(resident>RESMAX-rs) {
    puts("IMPORT RESIDENT CAP");
    goto outfail;
   }
   e[idx].live=body;
   body=0;
   resident+=rs;
   if(resident>peak) peak=resident;
  }
  free(body);
  body=0;
  if(idx==0||idx+1==count||(idx+1)%1000==0)
   printf("IMPORT STAGE %lu OF %lu RESIDENT %lu\n",
          idx+1,count,resident);
 }
 if(resident!=0) {
  puts("IMPORT RESIDENT LEAK");
  goto outfail;
 }
 if(fclose(out)!=0) {
  out=0;
  puts("IMPORT STAGE CLOSE FAIL");
  goto done;
 }
 out=0;
 printf("IMPORT PACK BYTES %lu VERSION %lu OBJECTS %lu\n",
        bytes,version,count);
 printf("IMPORT ORDINARY %lu OFS %lu REF %lu\n",
        ordinary,ofs,refs);
 printf("IMPORT MAX REPR %lu MAX COMPRESSED %lu\n",
        maxrepr,maxcomp);
 printf("IMPORT MAX RESULT %lu RESIDENT PEAK %lu\n",
        maxresult,peak);
 printf("IMPORT STAGED %lu\n",count);
 puts("M173 PACK IMPORT PASS");
 ok=1;
 goto done;

outfail:
 free(repr);
 free(body);
 if(out) fclose(out);
done:
 cleanup_live(e,count);
 free(e);
 free(pack);
 return ok?0:8;
}

static int stage_line(FILE *f,char *line,int cap) {
 int n;
 if(!fgets(line,cap,f)) return 0;
 n=(int)strlen(line);
 if(n==cap-1&&line[n-1]!='\n') return 0;
 while(n>0&&(line[n-1]=='\n'||line[n-1]=='\r'||
             line[n-1]==' ')) line[--n]=0;
 return n<=80;
}

static int hex_oid(const char *s,unsigned char oid[20]) {
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

static int verify_stage(unsigned long count) {
 FILE *f;
 char line[128],oidtext[41],extra;
 unsigned char stored[20],got[20],*body=0;
 unsigned long j,num,n,k,take,m;
 int typ,fields,hi,lo;
 f=fopen("dd:STGIN","r");
 if(!f) {
  perror("STGIN");
  return 8;
 }
 for(j=1;j<=count;j++) {
  if(!stage_line(f,line,sizeof line)) goto bad;
  fields=sscanf(line,"OBJ %lu %d %lu %40s %c",
                &num,&typ,&n,oidtext,&extra);
  if(fields!=4||num!=j||typ<1||typ>4||
     n>OBJMAXSZ||!hex_oid(oidtext,stored)) goto bad;
  body=(unsigned char *)malloc((size_t)(n?n:1));
  if(!body) goto bad;
  if(n==0) {
   if(!stage_line(f,line,sizeof line)||line[0]) goto bad;
  }
  for(k=0;k<n;k+=take) {
   take=n-k;
   if(take>32) take=32;
   if(!stage_line(f,line,sizeof line)||
      strlen(line)!=take*2) goto bad;
   for(m=0;m<take;m++) {
    hi=nib((unsigned char)line[m*2]);
    lo=nib((unsigned char)line[m*2+1]);
    if(hi<0||lo<0) goto bad;
    body[k+m]=(unsigned char)((hi<<4)|lo);
   }
  }
  if(!object_oid(typ,body,n,got)||
     memcmp(stored,got,20)!=0) goto bad;
  free(body);
  body=0;
  if(j==1||j==count||j%1000==0)
   printf("IMPORT VERIFY %lu OF %lu\n",j,count);
 }
 if(stage_line(f,line,sizeof line)||ferror(f)) goto bad;
 if(fclose(f)!=0) return 8;
 printf("IMPORT VERIFY OBJECTS %lu\n",count);
 puts("M173 STAGE VERIFY PASS");
 return 0;
bad:
 free(body);
 printf("IMPORT VERIFY FAIL OBJ %lu\n",j);
 fclose(f);
 return 8;
}

int main(int argc,char **argv) {
 unsigned long n;
 char *end;
 if(argc==2&&strcmp(argv[1],"IMPORT")==0)
  return import_pack(0);
 if(argc==3&&strcmp(argv[1],"IMPORT")==0&&
    strcmp(argv[2],"CHECKED")==0)
  return import_pack(1);
 if(argc==3&&strcmp(argv[1],"VERIFY")==0) {
  n=strtoul(argv[2],&end,10);
  if(*end||n<1||n>OBJMAX) {
   puts("VERIFY COUNT OUT OF BOUNDS");
   return 4;
  }
  return verify_stage(n);
 }
 puts("Usage: GITPIMP IMPORT [CHECKED] | VERIFY object-count");
 return 4;
}
