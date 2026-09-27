/* GITCWALK: native live PACK walk, C + GITCAPI.
 * Reads hex-record GITPBUF PACK through FILEDEF PACKIN.
 * No delta application yet: checks inflated delta instruction lengths.
 */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
extern int gitcapi(unsigned long *);
#define PACKCAP 340027UL
#define OUTCAP 65536UL
static unsigned char pack[340027];
static unsigned char output[65536];
static unsigned long api[6];
static unsigned long objpos[1808];
static unsigned char *objdata[1808];
static unsigned long objlen[1808];
static int objtype[1808];
/* Git delta variable integer; all reconstructed objects are bounded. */
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
static int dapply(const unsigned char *p,unsigned long n,
                  const unsigned char *base,unsigned long blen,
                  unsigned char *dst,unsigned long *outlen) {
 unsigned long at=0,bs,rs,off,sz,w=0;
 int op,j;
 if(!dvar(p,n,&at,&bs)||!dvar(p,n,&at,&rs)) return 0;
 if(bs!=blen||rs>OUTCAP) return 0;
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
   for(j=0;j<(int)sz;j++) dst[w+j]=base[off+j];
   w+=sz;
  } else if(op) {
   if((unsigned long)op>n-at||
      (unsigned long)op>rs-w) return 0;
   for(j=0;j<op;j++) dst[w+j]=p[at+j];
   at+=(unsigned long)op;
   w+=(unsigned long)op;
  } else return 0;
 }
 if(w!=rs) return 0;
 *outlen=w;
 return 1;
}
/* SHA-1 uses 32-bit words even when unsigned long is wider. */
#define W32 0xffffffffUL
static unsigned long h[5];
static unsigned long bxor(unsigned long a,unsigned long b) {
 return ((a|b)&(~(a&b)))&W32;
}
static unsigned long rol(unsigned long x,unsigned int n) {
 x &= W32;
 return ((x<<n)|(x>>(32-n)))&W32;
}
static void sha_block(const unsigned char *p) {
 unsigned long w[80],a,b,c,d,e,t,fun,k;
 unsigned int i;
 for(i=0;i<16;i++) {
  w[i]=((unsigned long)p[i*4]<<24)|
       ((unsigned long)p[i*4+1]<<16)|
       ((unsigned long)p[i*4+2]<<8)|p[i*4+3];
 }
 for(i=16;i<80;i++)
  w[i]=rol(bxor(bxor(w[i-3],w[i-8]),bxor(w[i-14],w[i-16])),1);
 a=h[0];b=h[1];c=h[2];d=h[3];e=h[4];
 for(i=0;i<80;i++) {
  if(i<20) {fun=(b&c)|((~b)&d);k=0x5a827999UL;}
  else if(i<40) {fun=bxor(bxor(b,c),d);k=0x6ed9eba1UL;}
  else if(i<60) {
   fun=(b&c)|(b&d)|(c&d);k=0x8f1bbcdcUL;
  } else {fun=bxor(bxor(b,c),d);k=0xca62c1d6UL;}
  t=(rol(a,5)+fun+e+k+w[i])&W32;
  e=d;d=c;c=rol(b,30);b=a;a=t;
 }
 h[0]=(h[0]+a)&W32;h[1]=(h[1]+b)&W32;
 h[2]=(h[2]+c)&W32;h[3]=(h[3]+d)&W32;
 h[4]=(h[4]+e)&W32;
}
#define BX(a,b) (((a)|(b))&(~((a)&(b))))
static void sha_opt_block(const unsigned char *p) {
 unsigned long w[80],a,b,c,d,e,t,fun,k;
 unsigned int i;
 for(i=0;i<16;i++) {
  w[i]=((unsigned long)p[i*4]<<24)|
       ((unsigned long)p[i*4+1]<<16)|
       ((unsigned long)p[i*4+2]<<8)|p[i*4+3];
 }
 for(i=16;i<80;i++)
  w[i]=rol(BX(BX(w[i-3],w[i-8]),BX(w[i-14],w[i-16])),1);
 a=h[0];b=h[1];c=h[2];d=h[3];e=h[4];
 for(i=0;i<80;i++) {
  if(i<20) {fun=(b&c)|((~b)&d);k=0x5a827999UL;}
  else if(i<40) {fun=BX(BX(b,c),d);k=0x6ed9eba1UL;}
  else if(i<60) {
   fun=(b&c)|(b&d)|(c&d);k=0x8f1bbcdcUL;
  } else {fun=BX(BX(b,c),d);k=0xca62c1d6UL;}
  t=(rol(a,5)+fun+e+k+w[i])&W32;
  e=d;d=c;c=rol(b,30);b=a;a=t;
 }
 h[0]=(h[0]+a)&W32;h[1]=(h[1]+b)&W32;
 h[2]=(h[2]+c)&W32;h[3]=(h[3]+d)&W32;
 h[4]=(h[4]+e)&W32;
}
static int use_opt_sha=0;
static void pack_sha(const unsigned char *p,unsigned long len,
                     unsigned char digest[20]) {
 unsigned char tail[128];
 unsigned long full=len/64,rem=len%64,bits=len*8;
 unsigned int i,j;
 h[0]=0x67452301UL;h[1]=0xefcdab89UL;
 h[2]=0x98badcfeUL;h[3]=0x10325476UL;
 h[4]=0xc3d2e1f0UL;
 for(i=0;i<full;i++) (use_opt_sha?sha_opt_block:sha_block)(p+i*64);
 for(i=0;i<128;i++) tail[i]=0;
 for(i=0;i<rem;i++) tail[i]=p[full*64+i];
 tail[rem]=0x80;
 /* The captured PACK is well below 2^29 bytes. */
 for(i=0;i<8;i++) tail[(rem<56?56:120)+i]=
  (unsigned char)(i<4?0:(bits>>(8*(7-i))));
 (use_opt_sha?sha_opt_block:sha_block)(tail);
 if(rem>=56) (use_opt_sha?sha_opt_block:sha_block)(tail+64);
 for(i=0;i<5;i++) for(j=0;j<4;j++)
  digest[i*4+j]=(unsigned char)(h[i]>>(24-j*8));
}
static unsigned char objoid[1808][20];
static unsigned char hashbuf[65568];
/* Git hashes ASCII bytes, not CMS-native/EBCDIC text strings. */
static const unsigned char typascii[5][7]={
 {0},
 {0x63,0x6f,0x6d,0x6d,0x69,0x74,0},
 {0x74,0x72,0x65,0x65,0,0,0},
 {0x62,0x6c,0x6f,0x62,0,0,0},
 {0x74,0x61,0x67,0,0,0,0}
};
static const char *typenames[5]={"","commit","tree","blob","tag"};
/* Return byte count including binary NUL. No sprintf/native charset. */
static int canonical_head(int type,unsigned long n,
                          unsigned char *dst) {
 unsigned char digits[12];
 unsigned long rem=n;
 int i=0,j=0;
 if(type<1||type>4||n>OUTCAP) return 0;
 while(typascii[type][i]) {
  dst[i]=typascii[type][i];i++;
 }
 dst[i++]=0x20;
 do {
  digits[j++]=(unsigned char)(0x30+rem%10);
  rem/=10;
 } while(rem);
 while(j) dst[i++]=digits[--j];
 dst[i++]=0;
 return i;
}
static int object_oid(int type,const unsigned char *p,
                      unsigned long n,unsigned char oid[20]) {
 int k,j;
 if(type<1||type>4||n>OUTCAP) return 0;
 k=canonical_head(type,n,hashbuf);
 if(!k) return 0;
 for(j=0;j<(int)n;j++) hashbuf[k+j]=p[j];
 pack_sha(hashbuf,(unsigned long)k+n,oid);
 return 1;
}


/* Hash canonical header and body without copying the object. */
static int fast_oid(int type,const unsigned char *p,
                    unsigned long n,unsigned char oid[20]) {
 unsigned char head[32],block[64],tail[128];
 unsigned long total,done=0,part,rem,bits;
 int k,i,j;
 if(type<1||type>4||n>OUTCAP) return 0;
 k=canonical_head(type,n,head);
 if(!k) return 0;
 total=(unsigned long)k+n;
 h[0]=0x67452301UL;h[1]=0xefcdab89UL;
 h[2]=0x98badcfeUL;h[3]=0x10325476UL;
 h[4]=0xc3d2e1f0UL;
 while(total-done>=64) {
  for(i=0;i<64;i++) {
   part=done+(unsigned long)i;
   block[i]=part<(unsigned long)k?
            head[part]:p[part-(unsigned long)k];
  }
  (use_opt_sha?sha_opt_block:sha_block)(block);
  done+=64;
 }
 rem=total-done;
 for(i=0;i<128;i++) tail[i]=0;
 for(i=0;i<(int)rem;i++) {
  part=done+(unsigned long)i;
  tail[i]=part<(unsigned long)k?
          head[part]:p[part-(unsigned long)k];
 }
 tail[rem]=0x80;
 bits=total*8;
 for(i=0;i<8;i++) tail[(rem<56?56:120)+i]=
  (unsigned char)(i<4?0:(bits>>(8*(7-i))));
 (use_opt_sha?sha_opt_block:sha_block)(tail);
 if(rem>=56) (use_opt_sha?sha_opt_block:sha_block)(tail+64);
 for(i=0;i<5;i++) for(j=0;j<4;j++)
  oid[i*4+j]=(unsigned char)(h[i]>>(24-j*8));
 return 1;
}


/* Resolve only a reconstructed in-pack base preceding this delta. */
static int find_ref_base(const unsigned char *oid,unsigned long prior) {
 unsigned long j;
 for(j=0;j<prior;j++) {
  if(objdata[j]&&memcmp(objoid[j],oid,20)==0)
   return (int)j;
 }
 return -1;
}
/* No inflater or PACK file needed: isolate REF OID/delta gates. */
/* Compare known Git wire bytes and known Git SHA-1 test vectors. */
static int ref_selftest(void) {
 static unsigned char abc[3]={0x61,0x62,0x63};
 static unsigned char abcd[4]={0x61,0x62,0x63,0x64};
 static unsigned char abcde[5]={0x61,0x62,0x63,0x64,0x65};
 static unsigned char four[8],five[8],hdr[32];
 static const unsigned char head3[7]={
  0x62,0x6c,0x6f,0x62,0x20,0x33,0
 };
 static const unsigned char shaabc[20]={
  0xf2,0xba,0x8f,0x84,0xab,0x5c,0x1b,0xce,
  0x84,0xa7,0xb4,0x41,0xcb,0x19,0x59,0xcf,
  0xc7,0x09,0x3b,0x7f
 };
 static const unsigned char shafive[20]={
  0x6a,0x81,0x65,0x46,0x05,0x70,0x53,0x1a,
  0x12,0x47,0xbd,0x99,0xa7,0x3b,0x53,0xa5,
  0xa6,0xe5,0x00,0xd5
 };
 static const unsigned char d1[]={3,4,0x90,3,1,0x64};
 static const unsigned char d2[]={4,5,0x90,4,1,0x65};
 static const unsigned char bad[]={4,4,0x90,3,1,0x64};
 unsigned char missing[20];
 unsigned long n=0;
 int i;
 if(canonical_head(3,3,hdr)!=7||
    memcmp(hdr,head3,7)!=0) return 8;
 objdata[0]=abc;objlen[0]=3;objtype[0]=3;
 if(!object_oid(3,abc,3,objoid[0])||
    memcmp(objoid[0],shaabc,20)!=0) {
  puts("CANONICAL ASCII ABC HASH FAIL");return 8;
 }
 if(find_ref_base(objoid[0],1)!=0) return 8;
 if(!dapply(d1,sizeof d1,abc,3,four,&n)||n!=4||
    memcmp(four,abcd,4)!=0) return 8;
 objdata[1]=four;objlen[1]=4;objtype[1]=3;
 if(!object_oid(3,four,4,objoid[1])) return 8;
 if(find_ref_base(objoid[1],2)!=1) return 8;
 if(!dapply(d2,sizeof d2,four,4,five,&n)||n!=5||
    memcmp(five,abcde,5)!=0) return 8;
 if(dapply(bad,sizeof bad,abc,3,four,&n)) return 8;
 memcpy(missing,objoid[1],20);
 missing[0]=(unsigned char)(missing[0]+1);
 if(find_ref_base(missing,2)>=0) return 8;
 if(find_ref_base(objoid[1],1)>=0) return 8;
 if(!object_oid(3,five,5,missing)||
    memcmp(missing,shafive,20)!=0) {
  puts("CANONICAL ASCII ABCDE HASH FAIL");return 8;
 }
 printf("CANONICAL ABC OID ");
 for(i=0;i<20;i++) printf("%02X",objoid[0][i]);
 putchar('\n');
 printf("REFTEST OID ");
 for(i=0;i<20;i++) printf("%02x",missing[i]);
 putchar('\n');
 puts("REF BACKWARD CHAIN AND NEGATIVE TESTS PASSED");
 return 0;
}

/* Stage verified objects as CMS text records, not loose Git files. */
static int stage_objects(unsigned long count) {
 FILE *out;
 unsigned long j,k,take,m;
 char line[65];
 static const char hex[]="0123456789ABCDEF";
 out=fopen("dd:OBJOUT","w");
 if(!out) {perror("OBJOUT");return 0;}
 for(j=0;j<count;j++) {
  if(fprintf(out,"OBJ %lu %d %lu ",j+1,objtype[j],
             objlen[j])<0) goto fail;
  for(k=0;k<20;k++) {
   line[k*2]=hex[objoid[j][k]>>4];
   line[k*2+1]=hex[objoid[j][k]&15];
  }
  line[40]=0;
  if(fputs(line,out)==EOF||fputc('\n',out)==EOF) goto fail;
  for(k=0;k<objlen[j];k+=take) {
   take=objlen[j]-k;
   if(take>32) take=32;
   for(m=0;m<take;m++) {
    line[m*2]=hex[objdata[j][k+m]>>4];
    line[m*2+1]=hex[objdata[j][k+m]&15];
   }
   line[take*2]=0;
   if(fputs(line,out)==EOF||fputc('\n',out)==EOF) goto fail;
  }
  if(objlen[j]==0&&fputc('\n',out)==EOF) goto fail;
  if((j+1)%256==0) printf("STAGE WRITTEN %lu\n",j+1);
 }
 if(fclose(out)!=0) return 0;
 return 1;
fail:
 printf("STAGE WRITE STOP OBJ %lu\n",j+1);
 perror("OBJOUT WRITE");
 fclose(out);
 return 0;
}
static int nib(int c) {
 if(c>='0'&&c<='9') return c-'0';
 if(c>='A'&&c<='F') return c-'A'+10;
 if(c>='a'&&c<='f') return c-'a'+10;
 return -1;
}
/* Independently rehash the persisted CMS text staging spool. */
static int stage_line(FILE *f,char *line,int cap) {
 int n;
 if(!fgets(line,cap,f)) return 0;
 for(n=0;line[n];n++)
  if(line[n]=='\n'||line[n]=='\r') {line[n]=0;break;}
 while(n>0&&line[n-1]==' ') line[--n]=0;
 return 1;
}
/* Resolve external REF from bounded staged CMS text by Git OID. */
static unsigned char ext_body[65536];
static unsigned long ext_len;
static int ext_type;
static int ext_lookup(const unsigned char *want) {
 FILE *f;
 char line[256],hexid[41],extra;
 unsigned char oid[20],digest[20];
 unsigned long j=0,num,n,k,take,m;
 int typ,fields,hi,lo,found=0;
 f=fopen("dd:EXTIN","r");
 if(!f) {perror("EXTIN");return 0;}
 while(stage_line(f,line,sizeof line)) {
  j++;
  fields=sscanf(line,"OBJ %lu %d %lu %40s %c",
                &num,&typ,&n,hexid,&extra);
  if(j>1808UL||fields!=4||num!=j||
     typ<1||typ>4||n>OUTCAP) goto bad;
  for(k=0;k<20;k++) {
   hi=nib((unsigned char)hexid[2*k]);
   lo=nib((unsigned char)hexid[2*k+1]);
   if(hi<0||lo<0) goto bad;
   oid[k]=(unsigned char)((hi<<4)|lo);
  }
  if(hexid[40]) goto bad;
  if(n==0) {
   if(!stage_line(f,line,sizeof line)||line[0]) goto bad;
  }
  for(k=0;k<n;k+=take) {
   take=n-k;if(take>32) take=32;
   if(!stage_line(f,line,sizeof line)||
      strlen(line)!=2*take) goto bad;
   for(m=0;m<take;m++) {
    hi=nib((unsigned char)line[2*m]);
    lo=nib((unsigned char)line[2*m+1]);
    if(hi<0||lo<0) goto bad;
    if(memcmp(oid,want,20)==0)
     ext_body[k+m]=(unsigned char)((hi<<4)|lo);
   }
  }
  if(memcmp(oid,want,20)!=0) continue;
  if(found||!object_oid(typ,ext_body,n,digest)||
     memcmp(digest,want,20)!=0) goto bad;
  found=1;ext_len=n;ext_type=typ;
 }
 if(ferror(f)) goto bad;
 if(fclose(f)!=0) return 0;
 if(found) printf("EXTERNAL REF BASE VERIFIED TYPE %d SIZE %lu\n",
                  ext_type,ext_len);
 return found;
bad:
 printf("INVALID EXTERNAL STAGE RECORD %lu\n",j);
 fclose(f);
 return 0;
}

static int verify_stage(int tamper) {
 static unsigned char body[65536];
 unsigned char stored[20],computed[20];
 char line[256],oidtext[41],extra;
 unsigned long j,k,size,index,offset,take,m;
 int type,fields,hi,lo;
 FILE *f=fopen("dd:OBJOUT","r");
 if(!f) {perror("OBJOUT");return 8;}
 for(j=1;j<=1808UL;j++) {
  if(!stage_line(f,line,sizeof line)) goto bad;
  fields=sscanf(line,"OBJ %lu %d %lu %40s %c",
                &index,&type,&size,oidtext,&extra);
  if(fields!=4||index!=j||type<1||type>4||
     size>OUTCAP) goto bad;
  for(k=0;k<40;k++) {
   if(!oidtext[k]) goto bad;
   hi=nib((unsigned char)oidtext[k]);
   if(hi<0) goto bad;
   if(k%2==0) stored[k/2]=(unsigned char)(hi<<4);
   else stored[k/2]|=(unsigned char)hi;
  }
  if(oidtext[40]) goto bad;
  if(size==0) {
   if(!stage_line(f,line,sizeof line)||line[0]) goto bad;
  }
  for(offset=0;offset<size;offset+=take) {
   take=size-offset;
   if(take>32) take=32;
   if(!stage_line(f,line,sizeof line)) goto bad;
   for(m=0;m<take;m++) {
    hi=nib((unsigned char)line[m*2]);
    lo=nib((unsigned char)line[m*2+1]);
    if(hi<0||lo<0) goto bad;
    body[offset+m]=(unsigned char)((hi<<4)|lo);
   }
   if(line[take*2]) goto bad;
  }
  if(tamper&&j==1) body[0]=(unsigned char)(body[0]+1);
  use_opt_sha=1;
  if(!object_oid(type,body,size,computed)) goto bad;
  use_opt_sha=0;
  for(k=0;k<20;k++) if(stored[k]!=computed[k]) {
   if(tamper&&j==1) {
    fclose(f);
    puts("PASS BADSTG: ALTERED BODY REJECTED");
    return 0;
   }
   printf("STAGE OID MISMATCH OBJ %lu\n",j);
   fclose(f);return 8;
  }
  if(j==1||j==1808UL) {
   printf("STAGE OID OBJ %lu TYPE %d SIZE %lu ",
          j,type,size);
   for(k=0;k<20;k++) printf("%02X",computed[k]);
   putchar('\n');
  }
 }
 if(stage_line(f,line,sizeof line)) goto bad;
 if(ferror(f)) goto bad;
 if(fclose(f)!=0) {puts("STAGE CLOSE FAIL");return 8;}
 if(tamper) {puts("FAIL BADSTG: NOT REJECTED");return 8;}
 puts("STAGE VERIFIED OBJECTS 1808");
 return 0;
bad:
 printf("STAGE RECORD FAIL OBJ %lu\n",j);
 fclose(f);
 return 8;
}
int main(int argc,char **argv) {
 FILE *f;
 char line[256];
 unsigned long n=0,pos,size,used,base,start,dist;
 unsigned long ofs_count=0,applied=0,rs=0,ref_count=0;
 unsigned char *tmp;
 int baseidx=-1,doapply=0,dooid=0,profile=0,fastmode=0;
 int fastonly=0,optmode=0,optcheck=0,stage=0,rpack=0,xpack=0;
 unsigned char reference[20],refbase[20];
 clock_t t0,hash_ticks=0,delta_ticks=0;
 unsigned long hash_bytes=0,delta_bytes=0;
 unsigned long count,idx,shift,limit;
 char *end;
 unsigned char digest[20];
 int i,hi,lo,b,type,rc,badsha=0;
 if(argc==2&&!strcmp(argv[1],"RTEST"))
  return ref_selftest();
 if(argc==2&&!strcmp(argv[1],"VERIFY"))
  return verify_stage(0);
 if(argc==2&&!strcmp(argv[1],"BADSTG"))
  return verify_stage(1);
 limit=20;
 if(argc>1) {
  if(argc!=2) {
   puts("Usage: GITCWALK [20|100|ALL|BADSHA]");return 4;
  }
  if(strcmp(argv[1],"XPACK")==0||
     strcmp(argv[1],"XAPPLY")==0) {
   doapply=1;dooid=strcmp(argv[1],"XPACK")==0;
   rpack=1;xpack=1;limit=PACKCAP;
  } else if(strcmp(argv[1],"RPACK")==0||
     strcmp(argv[1],"RAPPLY")==0) {
   doapply=1;
   dooid=strcmp(argv[1],"RPACK")==0;
   rpack=1;limit=PACKCAP;
  } else if(argv[1][0]=='S'&&argv[1][1]=='T'&&
     argv[1][2]=='A'&&argv[1][3]=='G'&&
     argv[1][4]=='E'&&argv[1][5]==0) {
   doapply=1;dooid=1;stage=1;limit=PACKCAP;
  } else if(argv[1][0]=='O'&&argv[1][1]=='P'&&
     argv[1][2]=='T'&&argv[1][3]=='C'&&
     argv[1][4]=='H'&&argv[1][5]=='E'&&
     argv[1][6]=='C'&&argv[1][7]=='K'&&
     argv[1][8]==0) {
   doapply=1;dooid=1;optcheck=1;limit=PACKCAP;
  } else if(argv[1][0]=='O'&&argv[1][1]=='P'&&
     argv[1][2]=='T'&&argv[1][3]=='S'&&
     argv[1][4]=='H'&&argv[1][5]=='A'&&
     argv[1][6]==0) {
   doapply=1;dooid=1;optmode=1;limit=PACKCAP;
  } else if(argv[1][0]=='F'&&argv[1][1]=='A'&&
     argv[1][2]=='S'&&argv[1][3]=='T'&&
     argv[1][4]=='O'&&argv[1][5]=='N'&&
     argv[1][6]=='L'&&argv[1][7]=='Y'&&
     argv[1][8]==0) {
   doapply=1;dooid=1;fastonly=1;limit=PACKCAP;
  } else if(argv[1][0]=='F'&&argv[1][1]=='A'&&
     argv[1][2]=='S'&&argv[1][3]=='T'&&
     argv[1][4]=='O'&&argv[1][5]=='I'&&
     argv[1][6]=='D'&&argv[1][7]==0) {
   doapply=1;dooid=1;fastmode=1;limit=PACKCAP;
  } else if(argv[1][0]=='P'&&argv[1][1]=='R'&&
     argv[1][2]=='O'&&argv[1][3]=='F'&&
     argv[1][4]=='I'&&argv[1][5]=='L'&&
     argv[1][6]=='E'&&argv[1][7]==0) {
   doapply=1;dooid=1;profile=1;limit=PACKCAP;
  } else if(argv[1][0]=='O'&&argv[1][1]=='I'&&
     argv[1][2]=='D'&&argv[1][3]==0) {
   doapply=1;dooid=1;limit=PACKCAP;
  } else if(argv[1][0]=='O'||argv[1][0]=='o') {
   if(argv[1][1]!='F'||argv[1][2]!='S'||
      argv[1][3]!='A'||argv[1][4]!='P'||
      argv[1][5]!='P'||argv[1][6]!='L'||
      argv[1][7]!='Y'||argv[1][8]!=0) return 4;
   doapply=1;limit=PACKCAP;
  } else if(argv[1][0]=='B'||argv[1][0]=='b') {
   if(argv[1][1]!='A'||argv[1][2]!='D'||
      argv[1][3]!='S'||argv[1][4]!='H'||
      argv[1][5]!='A'||argv[1][6]!=0) {
    puts("Usage: GITCWALK [20|100|ALL|BADSHA]");
    return 4;
   }
   badsha=1;
  } else if(argv[1][0]=='A'||argv[1][0]=='a') {
   if(argv[1][1]!='L'||argv[1][2]!='L'||argv[1][3]!=0) {
    puts("Usage: GITCWALK [20|100|ALL]");return 4;
   }
   limit=PACKCAP;
  } else {
   limit=strtoul(argv[1],&end,10);
   if(*end!=0||limit<1||limit>1808UL) {
    puts("Object limit must be 1 through 1808");return 4;
   }
  }
 }
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
 if((!rpack&&n!=PACKCAP)||(rpack&&n<32)||
    pack[0]!=0x50||pack[1]!=0x41||
    pack[2]!=0x43||pack[3]!=0x4b) {
  printf("PACK HEADER FAIL BYTES %lu EXPECT %lu\n",n,PACKCAP);
  if(n>=12) {
   puts("PACK HEADER DETAIL");
   for(i=0;i<12;i++) printf("%02X",pack[i]);
   putchar('\n');
  }
  return 8;
 }
 if(pack[4]!=0||pack[5]!=0||pack[6]!=0||pack[7]!=2) {
  puts("UNSUPPORTED PACK VERSION");return 8;
 }
 /* Negative gate mutates only this in-memory copy, not CMS disk. */
 if(badsha) pack[n-1]=(unsigned char)(pack[n-1]==0?1:0);
 pack_sha(pack,n-20,digest);
 for(i=0;i<20;i++) if(digest[i]!=pack[n-20+i]) {
  int j;
  if(badsha) {
   puts("PASS BADSHA: CORRUPT TRAILER REJECTED");
   return 0;
  }
  puts("FAIL NATIVE PACK SHA1");
  printf("COMPUTED ");
  for(j=0;j<20;j++) printf("%02X",digest[j]);
  printf("\nTRAILER  ");
  for(j=0;j<20;j++) printf("%02X",pack[n-20+j]);
  putchar('\n');
  return 8;
 }
 if(badsha) {
  puts("FAIL BADSHA: CORRUPT TRAILER ACCEPTED");
  return 8;
 }
 printf("NATIVE PACK SHA1 ");
 for(i=0;i<20;i++) printf("%02X",digest[i]);
 putchar('\n');
 count=((unsigned long)pack[8]<<24)|
       ((unsigned long)pack[9]<<16)|
       ((unsigned long)pack[10]<<8)|pack[11];
 if(count>1808UL||count==0) {
  puts("PACK OBJECT COUNT OUT OF BOUNDS");return 8;
 }
 printf("PACK BYTES %lu OBJECTS %lu\n",n,count);
 pos=12;
 if(limit>count) limit=count;
 for(idx=0;idx<limit;idx++) {
  if(pos>=n-20) {puts("SHORT HEADER");return 8;}
  start=pos;
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
   dist=(unsigned long)(b&127);
   while(b&128) {
    if(pos>=n-20) return 8;
    b=pack[pos++];
    if(dist>(PACKCAP>>7)) {
     puts("OFS DISTANCE OVERFLOW");return 8;
    }
    dist=((dist+1)<<7)|(unsigned long)(b&127);
   }
   if(dist==0||dist>start) {
    puts("BAD OFS DISTANCE");return 8;
   }
   base=start-dist;
   for(i=0;i<(int)idx;i++) if(objpos[i]==base) break;
   if(i==(int)idx) {
    printf("UNRESOLVED OFS BASE OBJ %lu OFFSET %lu\n",
           idx+1,base);
    return 8;
   }
   baseidx=i;
   ofs_count++;
  } else if(type==7) {
   if(pos+20>n-20) return 8;
   memcpy(refbase,pack+pos,20);
   pos+=20;
   if(doapply) {
    /* OFSAPPLY normally skips OID work; REF needs base OIDs. */
    if(!dooid) for(i=0;i<(int)idx;i++) {
     if(!object_oid(objtype[i],objdata[i],
                    objlen[i],objoid[i])) {
      puts("REF BASE OID HASH FAIL");return 8;
     }
    }
    baseidx=find_ref_base(refbase,idx);
    if(baseidx<0&&xpack&&ext_lookup(refbase)) baseidx=-2;
    if(baseidx<0&&baseidx!=-2) {
     printf("UNRESOLVED REF BASE OBJ %lu\n",idx+1);
     return 8;
    }
    ref_count++;
   }
  } else if(type<1||type>4) {
   puts("BAD OBJECT TYPE");return 8;
  }
  objpos[idx]=start;
  if(type>=1&&type<=4) objtype[idx]=type;
  else if((type==6||type==7)&&doapply) {
   if(baseidx==-2&&type==7&&xpack)
    objtype[idx]=ext_type;
   else {
    if(baseidx<0||baseidx>=(int)idx) {
     puts("INVALID NATIVE DELTA BASE");return 8;
    }
    objtype[idx]=objtype[baseidx];
   }
  }
  if(pos>=n-20) return 8;
  if(size>OUTCAP) {
   printf("OBJ %lu OUTPUT CAP %lu SIZE %lu\n",
          idx+1,OUTCAP,size);
   return 8;
  }
  api[0]=(unsigned long)(pack+pos);
  api[1]=n-20-pos;
  api[2]=(unsigned long)output;
  api[3]=OUTCAP;
  api[4]=api[5]=0;
  rc=gitcapi(api);
  if(limit<=20 || rc!=0 || idx%100==0 || idx+1==limit) {
   printf("OBJ %lu TYPE %d SIZE %lu",
          idx+1,type,size);
   printf(" ZOFF %lu RC %d OUT %lu USED %lu\n",
          pos,rc,api[4],api[5]);
  }
  if(rc!=0||api[5]==0||api[5]>api[1]||
     api[4]!=size) {
   puts("FAIL OBJECT INFLATE");return 8;
  }
  if(doapply) {
   if(type>=1&&type<=4) {
    rs=size;
    tmp=output;
   } else if(type==6||type==7) {
    if(baseidx!=-2&&!objdata[baseidx]) {
     puts("MISSING RECONSTRUCTED BASE");return 8;
    }
    tmp=(unsigned char *)malloc(OUTCAP);
    if(!tmp) {puts("DELTA ALLOC FAIL");return 8;}
    if(profile) t0=clock();
    if(!dapply(output,size,
               baseidx==-2?ext_body:objdata[baseidx],
               baseidx==-2?ext_len:objlen[baseidx],
               tmp,&rs)) {
     puts("FAIL NATIVE DELTA APPLY");free(tmp);return 8;
    }
    if(profile) {
     delta_ticks+=clock()-t0;
     delta_bytes+=rs;
    }
    applied++;
   } else {
    puts("REF DELTA NEEDS OID RESOLUTION");return 8;
   }
   objdata[idx]=(unsigned char *)malloc(rs?rs:1);
   if(!objdata[idx]) {puts("OBJECT ALLOC FAIL");return 8;}
   for(i=0;i<(int)rs;i++) objdata[idx][i]=tmp[i];
   objlen[idx]=rs;
   if(type==6||type==7) free(tmp);
   if(dooid) {
    if(profile) t0=clock();
    if(optmode||optcheck||stage) use_opt_sha=1;
    if(optcheck) {
     if(!object_oid(objtype[idx],objdata[idx],rs,objoid[idx])) {
      puts("FAIL OPT OID");return 8;
     }
     use_opt_sha=0;
     if(!object_oid(objtype[idx],objdata[idx],rs,reference)) {
      puts("FAIL REFERENCE OID");return 8;
     }
     for(i=0;i<20;i++) if(objoid[idx][i]!=reference[i]) {
      printf("OPT OID MISMATCH OBJ %lu\n",idx+1);
      return 8;
     }
    } else if(fastonly) {
     if(!fast_oid(objtype[idx],objdata[idx],rs,objoid[idx])) {
      puts("FAIL FAST ONLY OID");return 8;
     }
    } else if(fastmode) {
     if(!fast_oid(objtype[idx],objdata[idx],rs,objoid[idx])||
        !object_oid(objtype[idx],objdata[idx],rs,reference)) {
      puts("FAIL FAST OID");return 8;
     }
     for(i=0;i<20;i++) if(objoid[idx][i]!=reference[i]) {
      printf("FAST OID MISMATCH OBJ %lu\n",idx+1);
      return 8;
     }
    } else if(!object_oid(objtype[idx],objdata[idx],rs,
                          objoid[idx])) {
     puts("FAIL OBJECT OID");return 8;
    }
    if(optmode||optcheck||stage) use_opt_sha=0;
    if(profile) {
     hash_ticks+=clock()-t0;
     hash_bytes+=rs;
    }
    if(idx<3||idx+1==count) {
     printf("OID OBJ %lu TYPE %d SIZE %lu ",
            idx+1,objtype[idx],rs);
     for(i=0;i<20;i++) printf("%02X",objoid[idx][i]);
     putchar('\n');
    }
   }
  }
  used=api[5];
  pos+=used;
 }
 if(idx==count && pos!=n-20) {
  printf("PACK END MISMATCH %lu EXPECT %lu\n",pos,n-20);
  return 8;
 }
 printf("PASS %lu OBJECTS NEXT OFFSET %lu\n",
        idx,pos);
 printf("OFS BASE POSITIONS RESOLVED %lu\n",ofs_count);
 if(doapply) printf("OFS DELTAS APPLIED %lu\n",applied-ref_count);
 if(doapply) printf("REF DELTAS APPLIED %lu\n",ref_count);
 if(dooid) printf("OBJECT OIDS COMPUTED %lu\n",idx);
 if(fastmode) printf("FAST OIDS MATCH REFERENCE %lu\n",idx);
 if(fastonly) printf("FAST ONLY OIDS COMPUTED %lu\n",idx);
 if(optmode) printf("OPT SHA OIDS COMPUTED %lu\n",idx);
 if(optcheck) printf("OPT OIDS MATCH REFERENCE %lu\n",idx);
 if(stage) {
  if(!stage_objects(count)) {puts("STAGE WRITE FAIL");return 8;}
  printf("STAGED OBJECTS %lu\n",count);
 }
 if(profile) {
  printf("PROFILE CLOCKS PER SEC %lu\n",
         (unsigned long)CLOCKS_PER_SEC);
  printf("PROFILE DELTA TICKS %lu BYTES %lu\n",
         (unsigned long)delta_ticks,delta_bytes);
  printf("PROFILE HASH TICKS %lu BYTES %lu\n",
         (unsigned long)hash_ticks,hash_bytes);
 }
 return 0;
}
