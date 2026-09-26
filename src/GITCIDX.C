/* GITCIDX: bounded CMS text index for verified GITCWALK stage. */
/* BUILD: STGIN -> IDXOUT. CHECK/FIND: IDXIN only. */
/* Not a Git loose-object store. All data remains bounded. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define IDXCAP 1808UL
#define IDXSIZE 65536UL
struct idx_entry {
 unsigned char oid[20];
 unsigned long number,size;
 int type;
};
static struct idx_entry idx_entries[1808];
static unsigned long idx_unique;
static int idx_nib(int c) {
 if(c>='0'&&c<='9') return c-'0';
 if(c>='A'&&c<='F') return c-'A'+10;
 if(c>='a'&&c<='f') return c-'a'+10;
 return -1;
}
static int idx_hex(const char *s,unsigned char *oid) {
 int i,hi,lo;
 for(i=0;i<20;i++) {
  if(!s[2*i]||!s[2*i+1]) return 0;
  hi=idx_nib((unsigned char)s[2*i]);
  lo=idx_nib((unsigned char)s[2*i+1]);
  if(hi<0||lo<0) return 0;
  oid[i]=(unsigned char)((hi<<4)|lo);
 }
 return s[40]==0;
}
static void idx_print(FILE *f,const unsigned char *oid) {
 static const char hex[]="0123456789ABCDEF";
 int i;
 for(i=0;i<20;i++) {
  fputc(hex[oid[i]>>4],f);
  fputc(hex[oid[i]&15],f);
 }
}
static int idx_line(FILE *f,char *line,int cap) {
 int n;
 if(!fgets(line,cap,f)) return 0;
 n=(int)strlen(line);
 if(n==cap-1&&line[n-1]!='\n') return 0;
 while(n>0&&(line[n-1]=='\n'||line[n-1]=='\r'||
             line[n-1]==' ')) line[--n]=0;
 return n<=80;
}
static int idx_cmp(const void *a,const void *b) {
 const struct idx_entry *x=(const struct idx_entry *)a;
 const struct idx_entry *y=(const struct idx_entry *)b;
 int c=memcmp(x->oid,y->oid,20);
 if(c) return c;
 if(x->number<y->number) return -1;
 if(x->number>y->number) return 1;
 return 0;
}
/* Validate every STGIN record before writing IDXOUT. */
static int idx_build(void) {
 FILE *f,*out;
 char line[128],oidtext[41],extra;
 unsigned long j,num,n,k,take,m,unique=0;
 int typ,fields;
 struct idx_entry next;
 f=fopen("dd:STGIN","r");
 if(!f) {perror("STGIN");return 8;}
 for(j=0;j<IDXCAP;j++) {
  if(!idx_line(f,line,sizeof line)) goto badstage;
  fields=sscanf(line,"OBJ %lu %d %lu %40s %c",
                &num,&typ,&n,oidtext,&extra);
  if(fields!=4||num!=j+1||typ<1||typ>4||
     n>IDXSIZE||!idx_hex(oidtext,next.oid))
   goto badstage;
  next.number=num;next.type=typ;next.size=n;
  idx_entries[j]=next;
  if(n==0) {
   if(!idx_line(f,line,sizeof line)||line[0])
    goto badstage;
  }
  for(k=0;k<n;k+=take) {
   take=n-k;
   if(take>32) take=32;
   if(!idx_line(f,line,sizeof line)) goto badstage;
   if(strlen(line)!=2*take) goto badstage;
   for(m=0;m<take*2;m++)
    if(idx_nib((unsigned char)line[m])<0)
     goto badstage;
  }
 }
 if(idx_line(f,line,sizeof line)||ferror(f))
  goto badstage;
 if(fclose(f)!=0) return 8;
 qsort(idx_entries,IDXCAP,sizeof idx_entries[0],idx_cmp);
 for(j=0;j<IDXCAP;j++) {
  if(unique&&memcmp(idx_entries[j].oid,
                   idx_entries[unique-1].oid,20)==0) {
   if(idx_entries[j].size!=idx_entries[unique-1].size||
      idx_entries[j].type!=idx_entries[unique-1].type) {
    puts("INDEX DUPLICATE CONFLICT");return 8;
   }
  } else {
   idx_entries[unique++]=idx_entries[j];
  }
 }
 out=fopen("dd:IDXOUT","w");
 if(!out) {perror("IDXOUT");return 8;}
 if(fprintf(out,"IDX1 1808 %lu\n",unique)<0) goto badout;
 for(j=0;j<unique;j++) {
  if(fputs("OID ",out)==EOF) goto badout;
  idx_print(out,idx_entries[j].oid);
  if(fprintf(out," %lu %d %lu\n",
             idx_entries[j].number,idx_entries[j].type,
             idx_entries[j].size)<0) goto badout;
 }
 /* A missing trailer makes interrupted writes detectable. */
 if(fprintf(out,"END 1808 %lu\n",unique)<0) goto badout;
 if(fclose(out)!=0) {puts("INDEX CLOSE FAIL");return 8;}
 idx_unique=unique;
 printf("INDEX WRITTEN 1808 UNIQUE %lu\n",unique);
 return 0;
badstage:
 printf("INDEX BAD STAGE OBJ %lu\n",j+1);
 fclose(f);
 return 8;
badout:
 puts("INDEX WRITE FAIL");
 fclose(out);
 return 8;
}
/* A complete, sorted, self-terminating index is required. */
static int idx_read(void) {
 FILE *f;
 char line[128],oidtext[41],extra;
 unsigned long j=0,total,unique,num,size,endtotal,endunique;
 int typ,fields;
 struct idx_entry prev;
 f=fopen("dd:IDXIN","r");
 if(!f) {perror("IDXIN");return 8;}
 if(!idx_line(f,line,sizeof line)) goto bad;
 fields=sscanf(line,"IDX1 %lu %lu %c",
               &total,&unique,&extra);
 if(fields!=2||total!=IDXCAP||unique<1||unique>IDXCAP)
  goto bad;
 for(j=0;j<unique;j++) {
  if(!idx_line(f,line,sizeof line)) goto bad;
  fields=sscanf(line,"OID %40s %lu %d %lu %c",
                oidtext,&num,&typ,&size,&extra);
  if(fields!=4||num<1||num>IDXCAP||
     typ<1||typ>4||size>IDXSIZE||
     !idx_hex(oidtext,idx_entries[j].oid))
   goto bad;
  idx_entries[j].number=num;
  idx_entries[j].type=typ;
  idx_entries[j].size=size;
  if(j&&memcmp(prev.oid,idx_entries[j].oid,20)>=0)
   goto bad;
  prev=idx_entries[j];
 }
 if(!idx_line(f,line,sizeof line)) goto bad;
 fields=sscanf(line,"END %lu %lu %c",
               &endtotal,&endunique,&extra);
 if(fields!=2||endtotal!=total||endunique!=unique)
  goto bad;
 if(idx_line(f,line,sizeof line)||ferror(f)) goto bad;
 if(fclose(f)!=0) return 8;
 idx_unique=unique;
 return 0;
bad:
 printf("INDEX RECORD FAIL ENTRY %lu\n",j+1);
 fclose(f);
 return 8;
}
static int idx_locate(const unsigned char *target) {
 unsigned long lo=0,hi=idx_unique,mid;
 int cmp;
 while(lo<hi) {
  mid=lo+(hi-lo)/2;
  cmp=memcmp(idx_entries[mid].oid,target,20);
  if(cmp<0) lo=mid+1;
  else hi=mid;
 }
 if(lo==idx_unique||
    memcmp(idx_entries[lo].oid,target,20)!=0)
  return -1;
 return (int)lo;
}
static int idx_find(const unsigned char *target) {
 int pos=idx_locate(target);
 if(pos<0) {puts("INDEX OID NOT FOUND");return 4;}
 printf("INDEX OID ");
 idx_print(stdout,idx_entries[pos].oid);
 printf(" OBJ %lu TYPE %d SIZE %lu\n",
        idx_entries[pos].number,
        idx_entries[pos].type,idx_entries[pos].size);
 return 0;
}
/* Independently rehash the selected stored object before returning it. */
#define IS32 0xffffffffUL
#define IXOR(a,b) (((a)|(b))&(~((a)&(b))))
static unsigned long ih[5];
static unsigned char idx_hashbuf[65568];
static unsigned char idx_body[65536];
static const char *idx_types[5]={
 "","commit","tree","blob","tag"
};
static unsigned long idx_rol(unsigned long x,unsigned int n) {
 x&=IS32;
 return ((x<<n)|(x>>(32-n)))&IS32;
}
static void idx_block(const unsigned char *p) {
 unsigned long w[80],a,b,c,d,e,t,fun,k;
 unsigned int i;
 for(i=0;i<16;i++)
  w[i]=((unsigned long)p[i*4]<<24)|
       ((unsigned long)p[i*4+1]<<16)|
       ((unsigned long)p[i*4+2]<<8)|p[i*4+3];
 for(i=16;i<80;i++)
  w[i]=idx_rol(IXOR(IXOR(w[i-3],w[i-8]),
                  IXOR(w[i-14],w[i-16])),1);
 a=ih[0];b=ih[1];c=ih[2];d=ih[3];e=ih[4];
 for(i=0;i<80;i++) {
  if(i<20) {fun=(b&c)|((~b)&d);k=0x5a827999UL;}
  else if(i<40) {fun=IXOR(IXOR(b,c),d);k=0x6ed9eba1UL;}
  else if(i<60) {fun=(b&c)|(b&d)|(c&d);k=0x8f1bbcdcUL;}
  else {fun=IXOR(IXOR(b,c),d);k=0xca62c1d6UL;}
  t=(idx_rol(a,5)+fun+e+k+w[i])&IS32;
  e=d;d=c;c=idx_rol(b,30);b=a;a=t;
 }
 ih[0]=(ih[0]+a)&IS32;ih[1]=(ih[1]+b)&IS32;
 ih[2]=(ih[2]+c)&IS32;ih[3]=(ih[3]+d)&IS32;
 ih[4]=(ih[4]+e)&IS32;
}
static int idx_hash(int type,const unsigned char *body,
                    unsigned long n,unsigned char digest[20]) {
 unsigned char tail[128];
 unsigned long total,full,rem,bits;
 unsigned int i,j;
 int head;
 if(type<1||type>4||n>IDXSIZE) return 0;
 head=sprintf((char *)idx_hashbuf,"%s %lu",
              idx_types[type],n);
 idx_hashbuf[head++]=0;
 memcpy(idx_hashbuf+head,body,(size_t)n);
 total=(unsigned long)head+n;
 full=total/64;rem=total%64;bits=total*8;
 ih[0]=0x67452301UL;ih[1]=0xefcdab89UL;
 ih[2]=0x98badcfeUL;ih[3]=0x10325476UL;
 ih[4]=0xc3d2e1f0UL;
 for(i=0;i<full;i++) idx_block(idx_hashbuf+i*64);
 memset(tail,0,sizeof tail);
 memcpy(tail,idx_hashbuf+full*64,(size_t)rem);
 tail[rem]=0x80;
 for(i=0;i<8;i++) tail[(rem<56?56:120)+i]=
  (unsigned char)(i<4?0:(bits>>(8*(7-i))));
 idx_block(tail);
 if(rem>=56) idx_block(tail+64);
 for(i=0;i<5;i++) for(j=0;j<4;j++)
  digest[i*4+j]=(unsigned char)(ih[i]>>(24-j*8));
 return 1;
}
/* GET confirms the selected staged object still hashes to its OID. */
static int idx_get(const unsigned char *target) {
 FILE *f;
 char line[128],oidtext[41],extra;
 unsigned char headeroid[20],digest[20];
 unsigned long j,k,n,num,take,at,m;
 int pos,typ,fields,hi,lo;
 pos=idx_locate(target);
 if(pos<0) {puts("INDEX OID NOT FOUND");return 4;}
 f=fopen("dd:STGIN","r");
 if(!f) {perror("STGIN");return 8;}
 for(j=1;j<=idx_entries[pos].number;j++) {
  if(!idx_line(f,line,sizeof line)) goto badget;
  fields=sscanf(line,"OBJ %lu %d %lu %40s %c",
                &num,&typ,&n,oidtext,&extra);
  if(fields!=4||num!=j||typ<1||typ>4||
     n>IDXSIZE||!idx_hex(oidtext,headeroid))
   goto badget;
  if(j==idx_entries[pos].number) {
   if(memcmp(headeroid,target,20)!=0||
      typ!=idx_entries[pos].type||
      n!=idx_entries[pos].size) goto badget;
  }
  if(n==0) {
   if(!idx_line(f,line,sizeof line)||line[0])
    goto badget;
  }
  for(k=0;k<n;k+=take) {
   take=n-k;
   if(take>32) take=32;
   if(!idx_line(f,line,sizeof line)||
      strlen(line)!=2*take) goto badget;
   for(m=0;m<take;m++) {
    hi=idx_nib((unsigned char)line[m*2]);
    lo=idx_nib((unsigned char)line[m*2+1]);
    if(hi<0||lo<0) goto badget;
    if(j==idx_entries[pos].number)
     idx_body[k+m]=(unsigned char)((hi<<4)|lo);
   }
  }
 }
 if(fclose(f)!=0) return 8;
 if(!idx_hash(idx_entries[pos].type,idx_body,
              idx_entries[pos].size,digest)) return 8;
 if(memcmp(digest,target,20)!=0) {
  puts("OBJECT CONTENT OID MISMATCH");
  return 8;
 }
 printf("OBJECT READ OID ");
 idx_print(stdout,target);
 printf(" OBJ %lu TYPE %d SIZE %lu PREFIX ",
        idx_entries[pos].number,
        idx_entries[pos].type,idx_entries[pos].size);
 at=idx_entries[pos].size;
 if(at>16) at=16;
 if(at==0) putchar('-');
 for(k=0;k<at;k++) printf("%02X",idx_body[k]);
 putchar('\n');
 return 0;
badget:
 printf("OBJECT STAGE RECORD FAIL OBJ %lu\n",j);
 fclose(f);
 return 8;
}

/* Independently reconcile every stored object with the sorted index. */
static int idx_audit(void) {
 static unsigned char seen[1808];
 unsigned char headeroid[20],digest[20];
 char line[128],oidtext[41],extra;
 unsigned long j,num,n,k,take,m,matched=0;
 int typ,fields,hi,lo,pos;
 FILE *f;
 if(idx_read()!=0) return 8;
 memset(seen,0,sizeof seen);
 f=fopen("dd:STGIN","r");
 if(!f) {perror("STGIN");return 8;}
 for(j=1;j<=IDXCAP;j++) {
  if(!idx_line(f,line,sizeof line)) goto bad;
  fields=sscanf(line,"OBJ %lu %d %lu %40s %c",
                &num,&typ,&n,oidtext,&extra);
  if(fields!=4||num!=j||typ<1||typ>4||
     n>IDXSIZE||!idx_hex(oidtext,headeroid)) goto bad;
  pos=idx_locate(headeroid);
  if(pos<0||idx_entries[pos].size!=n||
     idx_entries[pos].type!=typ||
     idx_entries[pos].number>j) goto bad;
  if(idx_entries[pos].number==j&&!seen[pos]) {
   seen[pos]=1;matched++;
  }
  if(n==0) {
   if(!idx_line(f,line,sizeof line)||line[0])
    goto bad;
  }
  for(k=0;k<n;k+=take) {
   take=n-k;if(take>32) take=32;
   if(!idx_line(f,line,sizeof line)||
      strlen(line)!=2*take) goto bad;
   for(m=0;m<take;m++) {
    hi=idx_nib((unsigned char)line[m*2]);
    lo=idx_nib((unsigned char)line[m*2+1]);
    if(hi<0||lo<0) goto bad;
    idx_body[k+m]=(unsigned char)((hi<<4)|lo);
   }
  }
  if(!idx_hash(typ,idx_body,n,digest)||
     memcmp(digest,headeroid,20)!=0) goto bad;
 }
 if(idx_line(f,line,sizeof line)||ferror(f)) goto bad;
 if(fclose(f)!=0) return 8;
 if(matched!=idx_unique) {
  puts("AUDIT INDEX COVERAGE FAIL");return 8;
 }
 printf("AUDIT VERIFIED 1808 UNIQUE %lu\n",matched);
 return 0;
bad:
 printf("AUDIT OBJECT FAIL %lu\n",j);
 fclose(f);
 return 8;
}
int main(int argc,char **argv) {
 unsigned char query[20];
 if(argc==2&&strcmp(argv[1],"AUDIT")==0)
  return idx_audit();
 if(argc==2&&strcmp(argv[1],"BUILD")==0)
  return idx_build();
 if(argc==2&&strcmp(argv[1],"CHECK")==0) {
  if(idx_read()!=0) return 8;
  printf("INDEX VERIFIED 1808 UNIQUE %lu\n",idx_unique);
  return 0;
 }
 if(argc==3&&(strcmp(argv[1],"FIND")==0||
               strcmp(argv[1],"GET")==0)) {
  if(strlen(argv[2])!=40||!idx_hex(argv[2],query))
   {puts("REQUIRES 40 HEX DIGITS");return 4;}
  if(idx_read()!=0) return 8;
  if(strcmp(argv[1],"GET")==0) return idx_get(query);
  return idx_find(query);
 }
 puts("Usage: GITCIDX BUILD | CHECK | FIND/GET 40-hex-OID");
 return 4;
}
