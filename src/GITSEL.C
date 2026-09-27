/* Native CMS selector parser. CHECK lists untrusted candidates only. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

struct slot {
 unsigned long seq;
 char gen[9],digest[41];
 int valid;
};
static unsigned long crc32_ascii(const char *s) {
 static const char alphabet[]="ABCDEFGHIJKLMNOPQRSTUVWXYZ";
 static const char digits[]="0123456789";
 unsigned long crc=0xffffffffUL;
 unsigned long b;
 const char *p;
 int i,c;
 for(;*s;s++) {
  c=-1;
  for(p=alphabet;*p;p++)
   if(*p==*s) c=0x41+(int)(p-alphabet);
  for(p=digits;*p;p++)
   if(*p==*s) c=0x30+(int)(p-digits);
  if(*s==' ') c=0x20;
  if(c<0) return 0xffffffffUL;
  b=(crc^(unsigned long)c)&0xffUL;
  for(i=0;i<8;i++)
   b=(b&1UL)?(b>>1)^0xedb88320UL:b>>1;
  crc=(crc>>8)^b;
 }
 return crc^0xffffffffUL;
}
static int proper_name(const char *s) {
 const char *p;
 if(!*s||strlen(s)>8) return 0;
 for(p=s;*p;p++)
  if((*p<'A'||*p>'Z')&&(*p<'0'||*p>'9')) return 0;
 return 1;
}
static int proper_hex(const char *s) {
 const char *p;
 if(strlen(s)!=40) return 0;
 for(p=s;*p;p++)
  if((*p<'0'||*p>'9')&&(*p<'A'||*p>'F')) return 0;
 return 1;
}
static int slot_read(const char *dd,struct slot *out) {
 FILE *f;
 char line[128],tag[5],name[9],hash[41],sum[9];
 char extra,payload[90],check[128],suffix[16];
 unsigned long seq,crc,provided;
 int n,fields;
 memset(out,0,sizeof *out);
 f=fopen(dd,"r");
 if(!f) return 0;
 if(!fgets(line,sizeof line,f)) {
  fclose(f);return 0;
 }
 if(!strchr(line,'\n')) {
  fclose(f);return 0;
 }
 *strchr(line,'\n')=0;
 n=(int)strlen(line);
 while(n&&line[n-1]==' ') line[--n]=0;
 if(fgets(check,sizeof check,f)) {
  fclose(f);return 0;
 }
 if(ferror(f)||fclose(f)!=0||n>80) return 0;
 fields=sscanf(line,"%4s %lu %8s %40s %8s %c",
               tag,&seq,name,hash,sum,&extra);
 if(fields!=5||strcmp(tag,"SEL1")!=0||
    seq==0UL||seq>4294967295UL||
    !proper_name(name)||!proper_hex(hash)||
    strlen(sum)!=8) return 0;
 for(n=0;n<8;n++)
  if((sum[n]<'0'||sum[n]>'9')&&
     (sum[n]<'A'||sum[n]>'F')) return 0;
 sprintf(payload,"SEL1 %lu %s %s",seq,name,hash);
 sprintf(check,"%s %s",payload,sum);
 if(strcmp(line,check)!=0) return 0;
 crc=crc32_ascii(payload);
 sprintf(suffix,"%08lX",crc);
 if(strlen(suffix)!=8||strcmp(suffix,sum)!=0) return 0;
 provided=strtoul(sum,(char **)0,16);
 if(provided!=crc) return 0;
 out->seq=seq;
 strcpy(out->gen,name);strcpy(out->digest,hash);
 out->valid=1;
 return 1;
}
/* Write an untrusted SEL1 record to a caller-created output FILEDEF. */
static int selector_write(const char *sequence,const char *name,
                          const char *digest) {
 FILE *f;
 char payload[90],*end;
 unsigned long seq,crc;
 const char *p;
 if(!*sequence||strlen(sequence)>10||
    (sequence[0]=='0'&&sequence[1])||
    !proper_name(name)||!proper_hex(digest)) return 4;
 for(p=sequence;*p;p++)
  if(*p<'0'||*p>'9') return 4;
 seq=strtoul(sequence,&end,10);
 if(*end||seq==0||seq>4294967295UL) return 4;
 sprintf(payload,"SEL1 %lu %s %s",seq,name,digest);
 crc=crc32_ascii(payload);
 if(strlen(payload)+10>80) return 4;
 /* Prevent accidental overwrite of an existing active slot. */
 f=fopen("dd:SELOUT","r");
 if(f) {
  fclose(f);
  puts("SELECTOR OUTPUT EXISTS");
  return 8;
 }
 f=fopen("dd:SELOUT","w");
 if(!f) {perror("SELOUT");return 8;}
 if(fprintf(f,"%s %08lX\n",payload,crc)<0) {
  fclose(f);return 8;
 }
 if(fclose(f)!=0) return 8;
 printf("SELECTOR WRITTEN %lu %s (UNTRUSTED)\n",seq,name);
 return 0;
}
/* Read GEN2 DIGEST only for an untrusted, disposable selector. */
static int sel_line(FILE *f,char *line) {
 char *p;
 int n;
 if(!fgets(line,128,f)) return 0;
 n=(int)strlen(line);
 if(n&&line[n-1]=='\n') line[--n]=0;
 if(n&&line[n-1]=='\r') line[--n]=0;
 while(n&&line[n-1]==' ') line[--n]=0;
 p=line;
 if(n>80||!n) return 0;
 for(;*p;p++) if(*p=='\n'||*p=='\r') return 0;
 return 1;
}
static int selector_writegen(const char *sequence,const char *name) {
 FILE *f;
 char line[128],digest[41],minoid[41],maxoid[41],extra;
 unsigned long total,unique,endtotal,endunique;
 int ok=0;
 f=fopen("dd:GENIN","r");
 if(!f) {perror("GENIN");return 8;}
 if(!sel_line(f,line)||
    sscanf(line,"GEN2 %lu %lu %c",
           &total,&unique,&extra)!=2||
    total!=1808UL||unique<1||unique>1808UL)
  goto done;
 if(!sel_line(f,line)||
    sscanf(line,"DIGEST %40s %c",digest,&extra)!=1||
    !proper_hex(digest)) goto done;
 if(!sel_line(f,line)||
    sscanf(line,"MINOID %40s %c",minoid,&extra)!=1||
    !proper_hex(minoid)) goto done;
 if(!sel_line(f,line)||
    sscanf(line,"MAXOID %40s %c",maxoid,&extra)!=1||
    !proper_hex(maxoid)) goto done;
 if(!sel_line(f,line)||
    sscanf(line,"GEND2 %lu %lu %c",
           &endtotal,&endunique,&extra)!=2||
    endtotal!=total||endunique!=unique)
  goto done;
 if(fgets(line,sizeof line,f)||ferror(f)) goto done;
 ok=1;
done:
 if(fclose(f)!=0) return 8;
 if(!ok) {
  puts("GEN2 MANIFEST INVALID FOR SELECTOR");
  return 8;
 }
 /* The SELECT verifier must still perform the FULL GENCHECK. */
 return selector_write(sequence,name,digest);
}
/* Callback must fully rehash candidate and validate its GEN2 seal. */
#ifdef GITSEL_VERIFY
extern int git_sel_verify(const char *gen,const char *digest);
static int selector_choose(struct slot *a,struct slot *b) {
 struct slot *first,*second,*tmp;
 if(a->valid&&b->valid&&a->seq==b->seq&&
    (strcmp(a->gen,b->gen)!=0||
     strcmp(a->digest,b->digest)!=0)) {
  puts("CONFLICTING SELECTOR SEQUENCE");return 8;
 }
 first=a;second=b;
 if(b->valid&&(!a->valid||b->seq>a->seq)) {
  tmp=first;first=second;second=tmp;
 }
 if(first->valid&&
    git_sel_verify(first->gen,first->digest)==1) {
  printf("SELECTED %lu %s %s\n",first->seq,
         first->gen,first->digest);
  return 0;
 }
 if(second->valid&&
    git_sel_verify(second->gen,second->digest)==1) {
  printf("RECOVERED %lu %s %s\n",second->seq,
         second->gen,second->digest);
  return 0;
 }
 puts("NO FULLY VERIFIED GENERATION");
 return 8;
}
#endif
int main(int argc,char **argv) {
 struct slot a,b;
 if(argc==5&&strcmp(argv[1],"WRITE")==0)
  return selector_write(argv[2],argv[3],argv[4]);
 if(argc==4&&strcmp(argv[1],"WRITEGEN")==0)
  return selector_writegen(argv[2],argv[3]);
 if(argc!=2) {
  puts("Usage: GITSEL CHECK (candidates only)");
  return 4;
 }
 slot_read("dd:SEL0",&a);
 slot_read("dd:SEL1",&b);
#ifdef GITSEL_VERIFY
 if(strcmp(argv[1],"SELECT")==0)
  return selector_choose(&a,&b);
#endif
 if(strcmp(argv[1],"CHECK")!=0) {
  puts("Usage: GITSEL CHECK (candidates only)");
  return 4;
 }
 if(a.valid&&b.valid&&a.seq==b.seq&&
    (strcmp(a.gen,b.gen)!=0||
     strcmp(a.digest,b.digest)!=0)) {
  puts("CONFLICTING SELECTOR SEQUENCE");
  return 8;
 }
 if(a.valid) printf("CANDIDATE %lu %s %s\n",
                    a.seq,a.gen,a.digest);
 if(b.valid) printf("CANDIDATE %lu %s %s\n",
                    b.seq,b.gen,b.digest);
 if(!a.valid&&!b.valid) {
  puts("NO VALID SELECTOR SLOT");return 8;
 }
 puts("CANDIDATES UNTRUSTED: REQUIRE GENCHECK");
 return 0;
}
