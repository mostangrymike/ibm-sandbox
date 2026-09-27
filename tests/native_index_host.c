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
#include <unistd.h>
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
 if(!reject_v1("dd:FIDXIN",4,1)||sidx_audit()!=0)
  return 47;
 if(sidx_get(objoid[0])!=0||
    sidx_get(objoid[1807])!=0) return 41;
 if(idx_unique!=8) return 5;
 if(rename("dd:IDXOUT","dd:IDXIN")!=0) return 6;
 if(idx_read()!=0||idx_unique!=8||idx_audit()!=0) return 7;
 if(!reject_v1("dd:IDXIN",3,0)) return 48;
 if(idx_pair()!=0) return 50;
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
 if(sidx_read()!=0||idx_pair()==0) return 57;
 f=fopen("dd:FIDXIN","r+b");
 if(!f||fseek(f,start,SEEK_SET)!=0||
    fputc(old,f)==EOF||fclose(f)!=0) return 58;
 if(idx_pair()!=0) return 59;

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
    idx_pair()!=8) return 36;
 f=fopen("dd:STGIN","r+b");
 if(!f||fseek(f,start,SEEK_SET)!=0||
    fputc(old,f)==EOF||fclose(f)!=0) return 37;
 if(idx_get(needle)!=0||idx_audit()!=0||
    sidx_get(needle)!=0||sidx_audit()!=0||
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
 if(fclose(f)!=0||sidx_read()==0||sidx_audit()==0)
  return 44;
 if(sidx_build()!=0||
    rename("dd:FIDXOUT","dd:FIDXIN")!=0||
    sidx_read()!=0||sidx_get(objoid[1807])!=0||
    sidx_audit()!=0)
  return 45;
 if(remove("dd:FIDXIN")!=0) return 46;
 if(remove("dd:IDXIN")!=0||
    remove("dd:STGIN")!=0||
    remove("dd:OBJOUT")!=0) return 26;
 puts("HOST INDEX BUILD LOOKUP AND CORRUPTION GATES PASSED");
 return 0;
}
