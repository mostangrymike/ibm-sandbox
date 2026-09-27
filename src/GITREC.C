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
int main(int argc,char **argv) {
 struct slot a,b;
 if(argc!=4||strcmp(argv[1],"SELECT")!=0||
    !proper_name(argv[2])||!proper_name(argv[3])||
    strcmp(argv[2],argv[3])==0) {
  puts("GITREC SELECT C0NAME C1NAME");
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
 return selector_choose(&a,&b);
}
