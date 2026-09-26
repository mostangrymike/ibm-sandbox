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
 unsigned long j,total,unique,num,size,endtotal,endunique;
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
static int idx_find(const unsigned char *target) {
 unsigned long lo=0,hi=idx_unique,mid;
 int cmp;
 while(lo<hi) {
  mid=lo+(hi-lo)/2;
  cmp=memcmp(idx_entries[mid].oid,target,20);
  if(cmp<0) lo=mid+1;
  else hi=mid;
 }
 if(lo==idx_unique||
    memcmp(idx_entries[lo].oid,target,20)!=0) {
  puts("INDEX OID NOT FOUND");
  return 4;
 }
 printf("INDEX OID ");
 idx_print(stdout,idx_entries[lo].oid);
 printf(" OBJ %lu TYPE %d SIZE %lu\n",
        idx_entries[lo].number,
        idx_entries[lo].type,idx_entries[lo].size);
 return 0;
}
int main(int argc,char **argv) {
 unsigned char query[20];
 if(argc==2&&strcmp(argv[1],"BUILD")==0)
  return idx_build();
 if(argc==2&&strcmp(argv[1],"CHECK")==0) {
  if(idx_read()!=0) return 8;
  printf("INDEX VERIFIED 1808 UNIQUE %lu\n",idx_unique);
  return 0;
 }
 if(argc==3&&strcmp(argv[1],"FIND")==0) {
  if(strlen(argv[2])!=40||!idx_hex(argv[2],query))
   {puts("FIND REQUIRES 40 HEX DIGITS");return 4;}
  if(idx_read()!=0) return 8;
  return idx_find(query);
 }
 puts("Usage: GITCIDX BUILD | CHECK | FIND 40-hex-OID");
 return 4;
}
