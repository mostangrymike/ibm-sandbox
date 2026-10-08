/* M174: generalized indexed lookup for M173 CMS text stage. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define OBJMAX 100000UL
#define OBJMAXSZ (16UL*1024UL*1024UL)
#define W32 0xffffffffUL

struct idxent {
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

static int cmpent(const void *a,const void *b) {
 const struct idxent *x=(const struct idxent *)a;
 const struct idxent *y=(const struct idxent *)b;
 int c=memcmp(x->oid,y->oid,20);
 if(c) return c;
 if(x->num<y->num) return -1;
 if(x->num>y->num) return 1;
 return 0;
}

static int grow(struct idxent **p,unsigned long *cap,
                unsigned long need) {
 struct idxent *n;
 unsigned long next;
 if(need<=*cap) return 1;
 next=*cap?*cap*2:256;
 if(next<need) next=need;
 if(next>OBJMAX) next=OBJMAX;
 if(next<need) return 0;
 n=(struct idxent *)realloc(*p,(size_t)next*sizeof **p);
 if(!n) return 0;
 *p=n;
 *cap=next;
 return 1;
}

static int build_index(int prechecked) {
 FILE *f,*out,*probe;
 struct idxent *e=0;
 unsigned long cap=0,count=0,unique=0,num,size;
 unsigned char oid[20],got[20],*body=0;
 char line[128];
 long cookie;
 int type,ok=0;

 f=fopen("dd:STGIN","r");
 if(!f) {
  perror("STGIN");
  return 8;
 }
 while(1) {
  cookie=ftell(f);
  if(cookie<0) goto badstage;
  if(!linein(f,line,sizeof line)) {
   if(feof(f)) break;
   goto badstage;
  }
  if(!parse_header(line,&num,&type,&size,oid)||
     num!=count+1||count>=OBJMAX) goto badstage;
  if(!readbody(f,size,&body)) goto badstage;
  if(!object_oid(type,body,size,got)||
     memcmp(got,oid,20)!=0) goto badstage;
  free(body);
  body=0;
  if(!grow(&e,&cap,count+1)) goto badstage;
  memcpy(e[count].oid,oid,20);
  e[count].num=num;
  e[count].type=type;
  e[count].size=size;
  e[count].offset=cookie;
  count++;
  if(count==1||count%1000==0)
   printf("INDEX BUILD READ %lu\n",count);
 }
 if(count<1||ferror(f)) {
  fclose(f);
  f=0;
  goto done;
 }
 if(fclose(f)!=0) {
  f=0;
  goto done;
 }
 f=0;
 qsort(e,(size_t)count,sizeof e[0],cmpent);
 for(num=0;num<count;num++) {
  if(unique&&memcmp(e[num].oid,e[unique-1].oid,20)==0) {
   if(e[num].type!=e[unique-1].type||
      e[num].size!=e[unique-1].size) {
    puts("INDEX DUPLICATE CONFLICT");
    goto done;
   }
  } else {
   if(unique!=num) e[unique]=e[num];
   unique++;
  }
 }
 /* CMS FILEDEF can make nonexistent outputs appear readable.
  * Only a public STATE-guarded caller may request CHECKED.
  */
 if(!prechecked) {
  probe=fopen("dd:IDXOUT","r");
  if(probe) {
   fclose(probe);
   puts("INDEX OUTPUT EXISTS");
   goto done;
  }
 }
 out=fopen("dd:IDXOUT","w");
 if(!out) {
  perror("IDXOUT");
  goto done;
 }
 if(fprintf(out,"PIDX1 %lu %lu\n",count,unique)<0) goto badout;
 for(num=0;num<unique;num++) {
  if(fputs("OID ",out)==EOF) goto badout;
  printoid(out,e[num].oid);
  if(fprintf(out," %lu %d %lu %ld\n",
             e[num].num,e[num].type,e[num].size,
             e[num].offset)<0) goto badout;
 }
 if(fprintf(out,"PEND1 %lu %lu\n",count,unique)<0)
  goto badout;
 if(fclose(out)!=0) {
  out=0;
  goto done;
 }
 out=0;
 printf("INDEX WRITTEN %lu UNIQUE %lu\n",count,unique);
 puts("M174 INDEX BUILD PASS");
 ok=1;
 goto done;

badout:
 puts("INDEX WRITE FAIL");
 fclose(out);
 goto done;
badstage:
 puts("INDEX BAD STAGE");
 free(body);
 if(f) fclose(f);
 f=0;
done:
 free(e);
 return ok?0:8;
}

static int read_index(struct idxent **out,unsigned long *total,
                      unsigned long *unique) {
 FILE *f;
 struct idxent *e=0;
 char line[128],text[41],extra;
 unsigned long i,num,size,endtotal,endunique;
 int type,fields;
 f=fopen("dd:IDXIN","r");
 if(!f) {
  perror("IDXIN");
  return 8;
 }
 if(!linein(f,line,sizeof line)) goto bad;
 fields=sscanf(line,"PIDX1 %lu %lu %c",
               total,unique,&extra);
 if(fields!=2||*total<1||*total>OBJMAX||
    *unique<1||*unique>*total) goto bad;
 e=(struct idxent *)malloc((size_t)*unique*sizeof *e);
 if(!e) goto bad;
 for(i=0;i<*unique;i++) {
  if(!linein(f,line,sizeof line)) goto bad;
  fields=sscanf(line,"OID %40s %lu %d %lu %ld %c",
                text,&num,&type,&size,&e[i].offset,&extra);
  if(fields!=5||num<1||num>*total||
     type<1||type>4||size>OBJMAXSZ||
     e[i].offset<0||!hexoid(text,e[i].oid)) goto bad;
  if(i&&memcmp(e[i-1].oid,e[i].oid,20)>=0) goto bad;
  e[i].num=num;e[i].type=type;e[i].size=size;
 }
 if(!linein(f,line,sizeof line)) goto bad;
 fields=sscanf(line,"PEND1 %lu %lu %c",
               &endtotal,&endunique,&extra);
 if(fields!=2||endtotal!=*total||endunique!=*unique)
  goto bad;
 if(linein(f,line,sizeof line)||ferror(f)) goto bad;
 if(fclose(f)!=0) {
  free(e);
  return 8;
 }
 *out=e;
 return 0;
bad:
 puts("INDEX RECORD FAIL");
 free(e);
 fclose(f);
 return 8;
}

static long locate(struct idxent *e,unsigned long n,
                   const unsigned char oid[20]) {
 unsigned long lo=0,hi=n,mid;
 int c;
 while(lo<hi) {
  mid=lo+(hi-lo)/2;
  c=memcmp(e[mid].oid,oid,20);
  if(c<0) lo=mid+1;
  else hi=mid;
 }
 if(lo>=n||memcmp(e[lo].oid,oid,20)!=0) return -1;
 return (long)lo;
}

static int verify_at(FILE *f,const struct idxent *e,int emit) {
 char line[128];
 unsigned long num,size;
 unsigned char oid[20],got[20],*body=0;
 int type;
 if(fseek(f,e->offset,SEEK_SET)!=0||
    !linein(f,line,sizeof line)||
    !parse_header(line,&num,&type,&size,oid)||
    num!=e->num||type!=e->type||size!=e->size||
    memcmp(oid,e->oid,20)!=0||
    !readbody(f,size,&body)||
    !object_oid(type,body,size,got)||
    memcmp(got,oid,20)!=0) {
  free(body);
  return 0;
 }
 free(body);
 if(emit) {
  printf("INDEX OID ");
  printoid(stdout,e->oid);
  printf(" OBJ %lu TYPE %d SIZE %lu OFFSET %ld\n",
         e->num,e->type,e->size,e->offset);
 }
 return 1;
}

static int check_index(void) {
 struct idxent *e=0;
 unsigned long total=0,unique=0;
 if(read_index(&e,&total,&unique)!=0) return 8;
 free(e);
 printf("INDEX VERIFIED %lu UNIQUE %lu\n",total,unique);
 puts("M174 INDEX CHECK PASS");
 return 0;
}

static int audit_index(void) {
 struct idxent *e=0;
 unsigned char *seen=0,*body=0,oid[20],got[20];
 unsigned long total=0,unique=0,j,num,size,matched=0;
 char line[128];
 long cookie,at;
 int type;
 FILE *f;
 if(read_index(&e,&total,&unique)!=0) return 8;
 seen=(unsigned char *)calloc((size_t)unique,1);
 if(!seen) {
  free(e);
  return 8;
 }
 f=fopen("dd:STGIN","r");
 if(!f) {
  free(seen);free(e);
  perror("STGIN");
  return 8;
 }
 for(j=1;j<=total;j++) {
  cookie=ftell(f);
  if(cookie<0||!linein(f,line,sizeof line)||
     !parse_header(line,&num,&type,&size,oid)||
     num!=j) goto bad;
  at=locate(e,unique,oid);
  if(at<0||e[at].type!=type||e[at].size!=size||
     e[at].num>j) goto bad;
  if(!readbody(f,size,&body)||
     !object_oid(type,body,size,got)||
     memcmp(got,oid,20)!=0) goto bad;
  free(body);body=0;
  if(e[at].num==j) {
   if(seen[at]||e[at].offset!=cookie) goto bad;
   seen[at]=1;
   matched++;
  }
  if(j==1||j==total||j%1000==0)
   printf("INDEX AUDIT %lu OF %lu\n",j,total);
 }
 if(linein(f,line,sizeof line)||ferror(f)||
    matched!=unique) goto bad;
 if(fclose(f)!=0) {
  free(seen);free(e);
  return 8;
 }
 free(seen);free(e);
 printf("INDEX AUDIT VERIFIED %lu UNIQUE %lu\n",
        total,unique);
 puts("M174 INDEX AUDIT PASS");
 return 0;
bad:
 free(body);
 printf("INDEX AUDIT FAIL OBJ %lu\n",j);
 fclose(f);
 free(seen);free(e);
 return 8;
}

static int get_index(const char *text) {
 struct idxent *e=0;
 unsigned long total=0,unique=0;
 unsigned char oid[20];
 long at;
 FILE *f;
 if(strlen(text)!=40||!hexoid(text,oid)) {
  puts("GET REQUIRES 40 HEX DIGITS");
  return 4;
 }
 if(read_index(&e,&total,&unique)!=0) return 8;
 at=locate(e,unique,oid);
 if(at<0) {
  free(e);
  puts("INDEX OID NOT FOUND");
  return 4;
 }
 f=fopen("dd:STGIN","r");
 if(!f) {
  free(e);
  perror("STGIN");
  return 8;
 }
 if(!verify_at(f,&e[at],1)) {
  fclose(f);
  free(e);
  puts("INDEX GET STAGE VERIFY FAIL");
  return 8;
 }
 if(fclose(f)!=0) {
  free(e);
  return 8;
 }
 free(e);
 puts("M174 INDEX GET PASS");
 return 0;
}

int main(int argc,char **argv) {
 if(argc==2&&strcmp(argv[1],"BUILD")==0)
  return build_index(0);
 if(argc==3&&strcmp(argv[1],"BUILD")==0&&
    strcmp(argv[2],"CHECKED")==0)
  return build_index(1);
 if(argc==2&&strcmp(argv[1],"CHECK")==0)
  return check_index();
 if(argc==2&&strcmp(argv[1],"AUDIT")==0)
  return audit_index();
 if(argc==3&&strcmp(argv[1],"GET")==0)
  return get_index(argv[2]);
 puts("Usage: GITPIDX BUILD [CHECKED] | CHECK | AUDIT | GET oid");
 return 4;
}
