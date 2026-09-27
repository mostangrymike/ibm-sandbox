/* Read-only two-slot recovery with real full GEN2 verification. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int rec_active;
static const char *rec_expected[2];
static FILE *rec_open(const char *name,const char *mode) {
 static const char *map[2][4]={
  {"dd:C0STG","dd:C0IDX","dd:C0SEEK","dd:C0GEN"},
  {"dd:C1STG","dd:C1IDX","dd:C1SEEK","dd:C1GEN"}
 };
 if(strcmp(name,"dd:STGIN")==0)
  return fopen(map[rec_active][0],mode);
 if(strcmp(name,"dd:IDXIN")==0)
  return fopen(map[rec_active][1],mode);
 if(strcmp(name,"dd:FIDXIN")==0)
  return fopen(map[rec_active][2],mode);
 if(strcmp(name,"dd:GENIN")==0)
  return fopen(map[rec_active][3],mode);
 return fopen(name,mode);
}
#define fopen rec_open
#define main gitcidx_unused
#include "GITCIDX.C"
#undef main
#undef fopen
#define GITSEL_VERIFY 1
#define main gitsel_unused
#include "GITSEL.C"
#undef main
/* Bind slot record to its explicit CLI name and all four DDs. */
static int rec_manifest_digest(const char *wanted) {
 FILE *f;
 char line[128],hex[41],extra;
 int ok=0;
 f=rec_open("dd:GENIN","r");
 if(!f) return 0;
 if(idx_line(f,line,sizeof line)&&
    idx_line(f,line,sizeof line)&&
    sscanf(line,"DIGEST %40s %c",hex,&extra)==1&&
    strlen(hex)==40&&strcmp(hex,wanted)==0)
  ok=1;
 if(fclose(f)!=0) return 0;
 return ok;
}
int git_sel_verify(const char *name,const char *digest) {
 int i;
 for(i=0;i<2;i++) {
  if(strcmp(name,rec_expected[i])!=0) continue;
  rec_active=i;
  if(!rec_manifest_digest(digest)) continue;
  if(gen_check()==0) return 1;
 }
 return 0;
}
/* M22: validate the complete binary Git tree before emitting entries.
 * Display names as ASCII HEX to avoid CMS code-page ambiguity and
 * unsafe terminals. Never print partially parsed tree records.
 */
static int rec_tree_mode(const unsigned char *mode,
                         unsigned long n) {
 static const unsigned char valid[5][6]={
  {0x31,0x30,0x30,0x36,0x34,0x34},
  {0x31,0x30,0x30,0x37,0x35,0x35},
  {0x31,0x32,0x30,0x30,0x30,0x30},
  {0x31,0x36,0x30,0x30,0x30,0x30},
  {0x34,0x30,0x30,0x30,0x30,0x00}
 };
 static const unsigned long lengths[5]={6,6,6,6,5};
 unsigned int i;
 for(i=0;i<sizeof valid/sizeof valid[0];i++)
  if(lengths[i]==n&&
     memcmp(mode,valid[i],(size_t)n)==0) return 1;
 return 0;
}
static int rec_tree_walk(unsigned long n,int emit) {
 unsigned long at=0,mstart,mlen,nstart,nlen,j,count=0;
 char modes[7];
 while(at<n) {
  mstart=at;
  while(at<n&&idx_body[at]!=0x20&&at-mstart<=6) at++;
  mlen=at-mstart;
  if(mlen<5||mlen>6||at==n||
     !rec_tree_mode(idx_body+mstart,mlen)) return 0;
  for(j=0;j<mlen;j++)
   modes[j]=(char)('0'+idx_body[mstart+j]-0x30);
  modes[mlen]=0;
  at++;
  nstart=at;
  while(at<n&&idx_body[at]!=0) {
   if(idx_body[at]==0x2f) return 0;
   at++;
  }
  nlen=at-nstart;
  if(!nlen||at==n||n-at-1<20) return 0;
  at++;
  if(emit) {
   printf("TREE ENTRY MODE %s NAMELEN %lu OID ",
          modes,nlen);
   idx_print(stdout,idx_body+at);
   putchar('\n');
   for(j=0;j<nlen;j++) {
    if(j%32==0) fputs("TREE NAMEHEX ",stdout);
    printf("%02X",idx_body[nstart+j]);
    if(j%32==31||j+1==nlen) putchar('\n');
   }
  }
  at+=20;
  count++;
 }
 if(emit) printf("TREE ENTRIES %lu\n",count);
 return 1;
}
static int rec_tree(const unsigned char *oid) {
 int pos,rc;
 if(sidx_read()!=0) return 8;
 pos=sidx_locate(oid);
 if(pos<0) {puts("SEEK OID NOT FOUND");return 4;}
 if(sidx[pos].type!=2) {
  puts("OBJECT IS NOT A TREE");
  return 8;
 }
 sidx_silent=1;
 rc=sidx_get(oid);
 sidx_silent=0;
 if(rc!=0) return rc;
 if(!rec_tree_walk(sidx[pos].size,0)) {
  puts("TREE STRUCTURE INVALID");
  return 8;
 }
 puts("TREE DATA BEGIN");
 if(!rec_tree_walk(sidx[pos].size,1)) return 8;
 puts("TREE DATA END");
 return 0;
}
/* SELECT stays read-only. GET adds a verified indexed object
 * lookup only after a complete native GENCHECK has selected a slot.
 * Never call SGET on an unverified candidate or infer an active
 * generation from a selector's unchecked contents.
 */
int main(int argc,char **argv) {
 struct slot a,b;
 unsigned char oid[20];
 int get,full,tree,rc;
 get=argc==5&&strcmp(argv[1],"GET")==0;
 full=argc==5&&strcmp(argv[1],"CATHEX")==0;
 tree=argc==5&&strcmp(argv[1],"TREE")==0;
 if((!get&&!full&&!tree&&
     (argc!=4||strcmp(argv[1],"SELECT")!=0))||
    !proper_name(argv[2])||!proper_name(argv[3])||
    strcmp(argv[2],argv[3])==0) {
  puts("GITREC SELECT C0NAME C1NAME");
  puts("GITREC GET C0NAME C1NAME OID40");
  puts("GITREC CATHEX C0NAME C1NAME OID40");
  puts("GITREC TREE C0NAME C1NAME OID40");
  return 4;
 }
 if((get||full||tree)&&(strlen(argv[4])!=40||
    !idx_hex(argv[4],oid))) {
  puts("GET REQUIRES 40 HEX DIGITS");
  return 4;
 }
 rec_expected[0]=argv[2];rec_expected[1]=argv[3];
 slot_read("dd:SEL0",&a);
 slot_read("dd:SEL1",&b);
 if(a.valid&&strcmp(a.gen,argv[2])!=0) {
  puts("SELECTOR SLOT 0 NAME MISMATCH");a.valid=0;
 }
 if(b.valid&&strcmp(b.gen,argv[3])!=0) {
  puts("SELECTOR SLOT 1 NAME MISMATCH");b.valid=0;
 }
 rc=selector_choose(&a,&b);
 if(rc!=0||(!get&&!full&&!tree)) return rc;
 /* rec_active is set ONLY by the successful full-GEN2 callback. */
 if(tree) return rec_tree(oid);
 if(sidx_read()!=0) return 8;
 sidx_emit_full=full;
 return sidx_get(oid);
}
