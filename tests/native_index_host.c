/* Host-only index tests reuse the proven synthetic staging fixture. */
#define STAGE_HOST_ENTRY native_stage_entry
#include "native_stage_host.c"
#undef STAGE_HOST_ENTRY
/* Count native indexer STGIN opens, not fixture/setup opens. */
static unsigned long stage_opens=0;
static FILE *tracked_open(const char *name,const char *mode) {
 if(strcmp(name,"dd:STGIN")==0) stage_opens++;
 return fopen(name,mode);
}
#define fopen tracked_open
#define main gitcidx_entry
#include "../src/GITCIDX.C"
#undef main
#undef fopen
#define main selector_unused
#include "../src/GITSEL.C"
#undef main
#include <unistd.h>
static int write_slot(const char *path,unsigned long seq,
                      const char *gen,const char *digest) {
 FILE *f;
 char payload[90];
 unsigned long crc;
 sprintf(payload,"SEL1 %lu %s %s",seq,gen,digest);
 crc=crc32_ascii(payload);
 f=fopen(path,"w");
 if(!f) return 0;
 if(fprintf(f,"%s %08lX\n",payload,crc)<0)
  return 0;
 return fclose(f)==0;
}
static int copy_host_file(const char *source,
                          const char *dest) {
 FILE *src,*dst;
 int c;
 src=fopen(source,"rb");
 if(!src) return 0;
 dst=fopen(dest,"wb");
 if(!dst) {fclose(src);return 0;}
 while((c=fgetc(src))!=EOF)
  if(fputc(c,dst)==EOF) return 0;
 if(ferror(src)||fclose(src)!=0) return 0;
 return fclose(dst)==0;
}
static int selected_output(const char *expected) {
 FILE *f;
 char line[256];
 f=fopen("recovery.log","r");
 if(!f) return 0;
 while(fgets(line,sizeof line,f))
  if(strstr(line,expected)) {
   fclose(f);return 1;
  }
 fclose(f);
 return 0;
}
/* Refuse indexes generated with the legacy EBCDIC-hash code. */
static int reject_v1(const char *filename,long at,int seek) {
 FILE *f;
 int c;
 f=fopen(filename,"r+b");
 if(!f) return 0;
 if(fseek(f,at,SEEK_SET)!=0) return 0;
 c=fgetc(f);
 if(c!='2'||fseek(f,at,SEEK_SET)!=0||
    fputc('1',f)==EOF||fclose(f)!=0) return 0;
 if((seek?sidx_read():idx_read())==0) return 0;
 f=fopen(filename,"r+b");
 if(!f||fseek(f,at,SEEK_SET)!=0||
    fputc('2',f)==EOF||fclose(f)!=0) return 0;
 return (seek?sidx_read():idx_read())==0;
}
int main(void) {
 FILE *f;
 char line[256];
 long start,end;
 int old;
 unsigned char missing[20],needle[20],digest[20];
 unsigned long k;
 if(idx_self()!=0) return 49;
 if(native_stage_entry()!=0) return 1;
 if(!stage_objects(1808)) return 2;
 for(k=0;k<1808;k++) {
  if(!idx_hash(objtype[k],objdata[k],objlen[k],digest)||
     memcmp(digest,objoid[k],20)!=0) return 33;
 }
 if(link("dd:OBJOUT","dd:STGIN")!=0) return 3;
 if(idx_build()!=0) return 4;
 if(sidx_build()!=0||sidx_count!=8) return 39;
 if(rename("dd:FIDXOUT","dd:FIDXIN")!=0||
    sidx_read()!=0||sidx_count!=8) return 40;
 if(!reject_v1("dd:FIDXIN",4,1)||
    sidx_audit()!=0||sidx_fast_audit()!=0)
  return 47;
 if(sidx_get(objoid[0])!=0||
    sidx_get(objoid[1807])!=0) return 41;
 if(idx_unique!=8) return 5;
 if(rename("dd:IDXOUT","dd:IDXIN")!=0) return 6;
 if(idx_read()!=0||idx_unique!=8||idx_audit()!=0) return 7;
 if(!reject_v1("dd:IDXIN",3,0)) return 48;
 if(idx_pair()!=0) return 50;
 if(gen_write()!=0||
    rename("dd:GENOUT","dd:GENIN")!=0||
    gen_check()!=0) return 70;
 /* Exercise actual GITREC with two complete, independent GEN2 inputs. */
 if(link("dd:STGIN","dd:C0STG")!=0||
    link("dd:IDXIN","dd:C0IDX")!=0||
    link("dd:FIDXIN","dd:C0SEEK")!=0||
    link("dd:GENIN","dd:C0GEN")!=0||
    !copy_host_file("dd:STGIN","dd:C1STG")||
    !copy_host_file("dd:IDXIN","dd:C1IDX")||
    !copy_host_file("dd:FIDXIN","dd:C1SEEK")||
    !copy_host_file("dd:GENIN","dd:C1GEN")) return 81;
 if(!gen_digest(digest)) return 82;
 {
  char digesthex[41];
  for(k=0;k<20;k++)
   sprintf(digesthex+2*k,"%02X",digest[k]);
  if(!write_slot("dd:SEL0",41,"GENOLD",digesthex)||
     !write_slot("dd:SEL1",42,"GENNEW",digesthex))
   return 83;
 }
 if(system("./native_recovery SELECT GENOLD GENNEW"
           " > recovery.log")!=0||
    !selected_output("SELECTED 42 GENNEW")) return 84;
 /* M18: production GET must reverify the selected complete
  * candidate before using its direct SIDX2 read position.
  * Neither an untrusted selector nor an unavailable generation
  * may authorize staged object bytes.
  */
 {
  char oidhex[41],missinghex[41],command[180];
  for(k=0;k<20;k++)
   sprintf(oidhex+2*k,"%02X",objoid[0][k]);
  memset(missinghex,'F',40);missinghex[40]=0;
  sprintf(command,"./native_recovery GET GENOLD GENNEW %s"
          " > recovery.log",oidhex);
  if(system(command)!=0||
     !selected_output("SELECTED 42 GENNEW")||
     !selected_output("SEEK OBJECT OID")) return 127;
  sprintf(command,"./native_recovery GET GENOLD GENNEW %s"
          " > recovery.log",missinghex);
  if(system(command)==0||
     !selected_output("SEEK OID NOT FOUND")) return 128;
  if(system("./native_recovery GET GENOLD GENNEW NOTANID"
            " > recovery.log")==0||
     !selected_output("GET REQUIRES 40 HEX DIGITS")) return 129;
  if(rename("dd:C1GEN","held-lookup-gen")!=0) return 130;
  sprintf(command,"./native_recovery GET GENOLD GENNEW %s"
          " > recovery.log",oidhex);
  if(system(command)!=0||
     !selected_output("RECOVERED 41 GENOLD")||
     !selected_output("SEEK OBJECT OID")) return 131;
  if(rename("held-lookup-gen","dd:C1GEN")!=0) return 132;
  if(rename("dd:C0GEN","held-old-lookup-gen")!=0||
     rename("dd:C1GEN","held-new-lookup-gen")!=0) return 133;
  if(system(command)==0||
     !selected_output("NO FULLY VERIFIED GENERATION")||
     selected_output("SEEK OBJECT OID")) return 134;
  if(rename("held-old-lookup-gen","dd:C0GEN")!=0||
     rename("held-new-lookup-gen","dd:C1GEN")!=0) return 135;
  if(system(command)!=0||
     !selected_output("SELECTED 42 GENNEW")||
     !selected_output("SEEK OBJECT OID")) return 136;
 }
 /* M19: complete verified object output, including empty
  * bodies. All generated bytes are compared to fixture content.
  */
 {
  char oidhex[41],command[180];
  for(k=0;k<20;k++) sprintf(oidhex+2*k,"%02X",objoid[0][k]);
  sprintf(command,"./native_recovery CATHEX GENOLD GENNEW %s"
          " > recovery.log",oidhex);
  if(system(command)!=0||
     !selected_output("SELECTED 42 GENNEW")||
     !selected_output("OBJECT DATA BEGIN")||
     !selected_output("HEX 616263")||
     !selected_output("OBJECT DATA END")) return 137;
  for(k=0;k<20;k++) sprintf(oidhex+2*k,"%02X",objoid[5][k]);
  sprintf(command,"./native_recovery CATHEX GENOLD GENNEW %s"
          " > recovery.log",oidhex);
  if(system(command)!=0||
     !selected_output("SELECTED 42 GENNEW")||
     !selected_output("SIZE 0 PREFIX -")||
     !selected_output("OBJECT DATA BEGIN")||
     !selected_output("OBJECT DATA END")||
     selected_output("HEX ")) return 138;
  if(rename("dd:C1GEN","held-cathex-gen")!=0) return 139;
  if(system(command)!=0||
     !selected_output("RECOVERED 41 GENOLD")||
     !selected_output("OBJECT DATA BEGIN")) return 140;
  if(rename("held-cathex-gen","dd:C1GEN")!=0) return 141;
  if(rename("dd:C0GEN","held-cathex-old")!=0||
     rename("dd:C1GEN","held-cathex-new")!=0) return 142;
  if(system(command)==0||
     !selected_output("NO FULLY VERIFIED GENERATION")||
     selected_output("OBJECT DATA BEGIN")) return 143;
  if(rename("held-cathex-old","dd:C0GEN")!=0||
     rename("held-cathex-new","dd:C1GEN")!=0) return 144;
  if(system("./native_recovery CATHEX GENOLD GENNEW BADID"
            " > recovery.log")==0||
     !selected_output("GET REQUIRES 40 HEX DIGITS")||
     selected_output("OBJECT DATA BEGIN")) return 145;
 }
 {
  char x[41];
  for(k=0;k<20;k++) sprintf(x+2*k,"%02X",digest[k]);
  if(!write_slot("dd:SEL1",43,"GENOLD",x)) return 101;
  if(system("./native_recovery SELECT GENOLD GENNEW"
            " > recovery.log")!=0||
     !selected_output("SELECTOR SLOT 1 NAME MISMATCH")||
     !selected_output("SELECTED 41 GENOLD")) return 102;
  if(!write_slot("dd:SEL1",42,"GENNEW",x)) return 103;
 }
 if(system("./native_recovery SELECT GENOLD GENOLD"
           " > recovery.log")==0) return 104;
 /* M15 host interrupted-promotion gates use disposable copies.
  * A valid older slot must survive each partial new-slot write
  * and each missing new-generation component. The real compiled
  * GITREC must execute full GENCHECK on every surviving candidate.
  */
 {
  const char *components[4]={
   "dd:C1STG","dd:C1IDX","dd:C1SEEK","dd:C1GEN"
  };
  const char *held[4]={
   "held-new-stage","held-new-index",
   "held-new-seek","held-new-gen"
  };
  char digesthex[41];
  long slotlen;
  long cut[5];
  int j;
  f=fopen("dd:SEL1","rb");
  if(!f||fseek(f,0,SEEK_END)!=0) return 105;
  slotlen=ftell(f);
  if(fclose(f)!=0||slotlen<32) return 106;
  for(j=0;j<20;j++)
   sprintf(digesthex+2*j,"%02X",digest[j]);
  cut[0]=0;cut[1]=1;cut[2]=8;
  cut[3]=slotlen/2;cut[4]=slotlen-1;
  for(j=0;j<5;j++) {
   if(!write_slot("dd:SEL1",42,"GENNEW",digesthex))
    return 107;
   f=fopen("dd:SEL1","r+b");
   if(!f||ftruncate(fileno(f),cut[j])!=0||
      fclose(f)!=0) return 108;
   if(system("./native_recovery SELECT GENOLD GENNEW"
             " > recovery.log")!=0||
      !selected_output("SELECTED 41 GENOLD"))
    return 109;
  }
  if(!write_slot("dd:SEL1",42,"GENNEW",digesthex))
   return 110;
  for(j=0;j<4;j++) {
   if(rename(components[j],held[j])!=0) return 111;
   if(system("./native_recovery SELECT GENOLD GENNEW"
             " > recovery.log")!=0||
      !selected_output("RECOVERED 41 GENOLD"))
    return 112;
   if(rename(held[j],components[j])!=0) return 113;
  }
  /* An interrupted manifest write cannot authorize a new gen. */
  if(rename("dd:C1GEN","held-new-gen")!=0) return 114;
  f=fopen("dd:C1GEN","w");
  if(!f||fputs("GEN2 1808 8\nDIGEST ",f)==EOF||
     fclose(f)!=0) return 115;
  if(system("./native_recovery SELECT GENOLD GENNEW"
            " > recovery.log")!=0||
     !selected_output("RECOVERED 41 GENOLD"))
   return 116;
  if(remove("dd:C1GEN")!=0||
     rename("held-new-gen","dd:C1GEN")!=0) return 117;
  if(system("./native_recovery SELECT GENOLD GENNEW"
            " > recovery.log")!=0||
     !selected_output("SELECTED 42 GENNEW")) return 118;
 }

 {
  char hex[41],fake[41];
  for(k=0;k<20;k++) sprintf(hex+2*k,"%02X",digest[k]);
  memset(fake,'0',40);fake[40]=0;
  if(!write_slot("dd:SEL1",60,"GENNEW",fake)) return 119;
  if(system("./native_recovery SELECT GENOLD GENNEW > recovery.log")!=0||
     !selected_output("RECOVERED 41 GENOLD")) return 120;
  if(!write_slot("dd:SEL1",40,"GENNEW",hex)) return 121;
  if(system("./native_recovery SELECT GENOLD GENNEW > recovery.log")!=0||
     !selected_output("SELECTED 41 GENOLD")) return 122;
  if(!write_slot("dd:SEL1",41,"GENNEW",hex)) return 123;
  if(system("./native_recovery SELECT GENOLD GENNEW > recovery.log")==0||
     !selected_output("CONFLICTING SELECTOR SEQUENCE")) return 124;
  if(!write_slot("dd:SEL1",42,"GENNEW",hex)) return 125;
  if(system("./native_recovery SELECT GENOLD GENNEW > recovery.log")!=0||
     !selected_output("SELECTED 42 GENNEW")) return 126;
 }
 f=fopen("dd:C1GEN","r+b");
 if(!f||fputc('X',f)==EOF||fclose(f)!=0) return 85;
 if(system("./native_recovery SELECT GENOLD GENNEW"
           " > recovery.log")!=0||
    !selected_output("RECOVERED 41 GENOLD")) return 86;
 if(remove("dd:C0GEN")!=0) return 87;
 if(system("./native_recovery SELECT GENOLD GENNEW"
           " > recovery.log")==0||
    !selected_output("NO FULLY VERIFIED GENERATION")) return 88;
 if(link("dd:GENIN","dd:C0GEN")!=0) return 89;
 /* A newer copy with changed object bytes must never be selected. */
 if(!copy_host_file("dd:GENIN","dd:C1GEN")) return 90;
 f=fopen("dd:C1STG","r+b");
 if(!f||!fgets(line,sizeof line,f)) return 91;
 start=ftell(f);old=fgetc(f);
 if(old==EOF||fseek(f,start,SEEK_SET)!=0||
    fputc(old=='0'?'1':'0',f)==EOF||
    fclose(f)!=0) return 92;
 if(system("./native_recovery SELECT GENOLD GENNEW"
           " > recovery.log")!=0||
    !selected_output("RECOVERED 41 GENOLD")) return 93;
 if(!copy_host_file("dd:STGIN","dd:C1STG")) return 94;
 /* Truncated newer seek index fails full GENCHECK, not just parsing. */
 if(remove("dd:C1SEEK")!=0) return 95;
 f=fopen("dd:C1SEEK","wb");
 if(!f||fputs("SIDX2 1808 8\n",f)==EOF||
    fclose(f)!=0) return 96;
 if(system("./native_recovery SELECT GENOLD GENNEW"
           " > recovery.log")!=0||
    !selected_output("RECOVERED 41 GENOLD")) return 97;
 if(!copy_host_file("dd:FIDXIN","dd:C1SEEK")) return 98;
 if(remove("dd:C1IDX")!=0) return 99;
 if(system("./native_recovery SELECT GENOLD GENNEW"
           " > recovery.log")!=0||
    !selected_output("RECOVERED 41 GENOLD")) return 100;


 /* A header mutation is rejected; restoring it passes. */
 f=fopen("dd:GENIN","r+b");
 if(!f||!fgets(line,sizeof line,f)) return 71;
 start=ftell(f);old=fgetc(f);
 if(old!='D'||fseek(f,start,SEEK_SET)!=0||
    fputc('X',f)==EOF||fclose(f)!=0) return 72;
 if(gen_check()==0) return 73;
 f=fopen("dd:GENIN","r+b");
 if(!f||fseek(f,start,SEEK_SET)!=0||
    fputc(old,f)==EOF||fclose(f)!=0) return 74;
 if(gen_check()!=0) return 75;
 /* Missing final manifest bytes cannot authorize a generation. */
 f=fopen("dd:GENIN","r+b");
 if(!f||fseek(f,0,SEEK_END)!=0) return 76;
 end=ftell(f);
 if(end<16||ftruncate(fileno(f),end-2)!=0) return 77;
 if(fclose(f)!=0||gen_check()==0) return 78;
 if(gen_write()!=0||
    rename("dd:GENOUT","dd:GENIN")!=0||
    gen_check()!=0) return 79;
 stage_opens=0;
 if(sidx_fast_audit()!=0||stage_opens!=1) return 62;
 stage_opens=0;
 if(sidx_audit()!=0||stage_opens!=1) return 60;
 stage_opens=0;
 if(idx_pair()!=0||stage_opens!=1) return 61;
 /* A structurally valid stale SIDX2 descriptor must fail PAIR. */
 f=fopen("dd:FIDXIN","r+b");
 if(!f||!fgets(line,sizeof line,f)) return 51;
 start=ftell(f);
 if(!fgets(line,sizeof line,f)) return 52;
 {
  char *q;
  q=strchr(line+45,' ');
  if(!q) return 53;
  q=strchr(q+1,' ');
  if(!q||q[1]<'0'||q[1]>'9') return 54;
  start+=(long)(q+1-line);
 }
 if(fseek(f,start,SEEK_SET)!=0) return 55;
 old=fgetc(f);
 if(old==EOF||fseek(f,start,SEEK_SET)!=0||
    fputc(old=='0'?'1':'0',f)==EOF||
    fclose(f)!=0) return 56;
 if(sidx_read()!=0||idx_pair()==0||
    sidx_fast_audit()==0||gen_check()==0) return 57;
 f=fopen("dd:FIDXIN","r+b");
 if(!f||fseek(f,start,SEEK_SET)!=0||
    fputc(old,f)==EOF||fclose(f)!=0) return 58;
 if(idx_pair()!=0||sidx_fast_audit()!=0||
    gen_check()!=0) return 59;

 for(k=0;k<20;k++) needle[k]=objoid[0][k];
 if(idx_find(needle)!=0||idx_get(needle)!=0) return 8;
 for(k=0;k<idx_unique;k++)
  if(memcmp(idx_entries[k].oid,needle,20)==0) {
   if(idx_entries[k].number!=1||
      idx_entries[k].type!=1||
      idx_entries[k].size!=3) return 9;
   break;
  }
 if(k==idx_unique) return 10;
 for(k=0;k<20;k++) missing[k]=0xff;
 if(idx_find(missing)!=4||idx_get(missing)!=4||
    sidx_get(missing)!=4) return 11;
 f=fopen("dd:IDXIN","r+b");
 if(!f||!fgets(line,sizeof line,f)) return 12;
 start=ftell(f);
 old=fgetc(f);
 if(old!= 'O') return 13;
 if(fseek(f,start,SEEK_SET)!=0||
    fputc('X',f)==EOF||fclose(f)!=0) return 14;
 if(idx_read()==0) return 15;
 f=fopen("dd:IDXIN","r+b");
 if(!f||fseek(f,start,SEEK_SET)!=0||
    fputc(old,f)==EOF||fclose(f)!=0) return 16;
 if(idx_read()!=0) return 17;
 f=fopen("dd:IDXIN","r+b");
 if(!f) return 18;
 if(fseek(f,0,SEEK_END)!=0) return 19;
 end=ftell(f);
 if(end<16||ftruncate(fileno(f),end-2)!=0) return 20;
 if(fclose(f)!=0) return 21;
 if(idx_read()==0) return 22;
 if(idx_build()!=0) return 23;
 if(rename("dd:IDXOUT","dd:IDXIN")!=0) return 24;
 if(idx_read()!=0) return 25;
 /* Valid hex corruption must still fail a GET content hash check. */
 f=fopen("dd:STGIN","r+b");
 if(!f||!fgets(line,sizeof line,f)) return 34;
 start=ftell(f);old=fgetc(f);
 if(old==EOF||fseek(f,start,SEEK_SET)!=0||
    fputc(old=='0'?'1':'0',f)==EOF||
    fclose(f)!=0) return 35;
 if(idx_get(needle)!=8||idx_audit()!=8||
    sidx_get(needle)!=8||sidx_audit()!=8||
    sidx_fast_audit()!=8||
    idx_pair()!=8||gen_check()!=8) return 36;
 f=fopen("dd:STGIN","r+b");
 if(!f||fseek(f,start,SEEK_SET)!=0||
    fputc(old,f)==EOF||fclose(f)!=0) return 37;
 if(idx_get(needle)!=0||idx_audit()!=0||
    sidx_get(needle)!=0||sidx_audit()!=0||
    sidx_fast_audit()!=0||
    idx_pair()!=0) return 38;
 /* Reject malformed staged hex, then restore the verified source. */
 f=fopen("dd:STGIN","r+b");
 if(!f||!fgets(line,sizeof line,f)) return 27;
 start=ftell(f);
 old=fgetc(f);
 if(old==EOF||fseek(f,start,SEEK_SET)!=0||
    fputc('G',f)==EOF||fclose(f)!=0) return 28;
 if(idx_build()==0||idx_audit()==0) return 29;
 f=fopen("dd:STGIN","r+b");
 if(!f||fseek(f,start,SEEK_SET)!=0||
    fputc(old,f)==EOF||fclose(f)!=0) return 30;
 if(idx_build()!=0||idx_audit()!=0) return 31;
 if(remove("dd:IDXOUT")!=0) return 32;
 f=fopen("dd:FIDXIN","r+b");
 if(!f||fseek(f,0,SEEK_END)!=0) return 42;
 end=ftell(f);
 if(end<16||ftruncate(fileno(f),end-2)!=0) return 43;
 if(fclose(f)!=0||sidx_read()==0||
    sidx_audit()==0||sidx_fast_audit()==0)
  return 44;
 if(sidx_build()!=0||
    rename("dd:FIDXOUT","dd:FIDXIN")!=0||
    sidx_read()!=0||sidx_get(objoid[1807])!=0||
    sidx_audit()!=0||sidx_fast_audit()!=0)
  return 45;
 if(remove("dd:GENIN")!=0) return 80;
 if(remove("dd:FIDXIN")!=0) return 46;
 if(remove("dd:IDXIN")!=0||
    remove("dd:STGIN")!=0||
    remove("dd:OBJOUT")!=0) return 26;
 puts("HOST INDEX BUILD LOOKUP AND CORRUPTION GATES PASSED");
 return 0;
}
