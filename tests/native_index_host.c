/* Host-only index tests reuse the proven synthetic staging fixture. */
#define STAGE_HOST_ENTRY native_stage_entry
#include "native_stage_host.c"
#undef STAGE_HOST_ENTRY
#define main gitcidx_entry
#include "../src/GITCIDX.C"
#undef main
#include <unistd.h>
int main(void) {
 FILE *f;
 char line[256];
 long start,end;
 int old;
 unsigned char missing[20],needle[20];
 unsigned long k;
 if(native_stage_entry()!=0) return 1;
 if(!stage_objects(1808)) return 2;
 if(link("dd:OBJOUT","dd:STGIN")!=0) return 3;
 if(idx_build()!=0) return 4;
 if(idx_unique!=8) return 5;
 if(rename("dd:IDXOUT","dd:IDXIN")!=0) return 6;
 if(idx_read()!=0||idx_unique!=8) return 7;
 for(k=0;k<20;k++) needle[k]=objoid[0][k];
 if(idx_find(needle)!=0) return 8;
 for(k=0;k<idx_unique;k++)
  if(memcmp(idx_entries[k].oid,needle,20)==0) {
   if(idx_entries[k].number!=1||
      idx_entries[k].type!=1||
      idx_entries[k].size!=3) return 9;
   break;
  }
 if(k==idx_unique) return 10;
 for(k=0;k<20;k++) missing[k]=0xff;
 if(idx_find(missing)!=4) return 11;
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
 if(end<16||ftruncate(fileno(f),end-1)!=0) return 20;
 if(fclose(f)!=0) return 21;
 if(idx_read()==0) return 22;
 if(idx_build()!=0) return 23;
 if(rename("dd:IDXOUT","dd:IDXIN")!=0) return 24;
 if(idx_read()!=0) return 25;
 if(remove("dd:IDXIN")!=0||
    remove("dd:STGIN")!=0||
    remove("dd:OBJOUT")!=0) return 26;
 puts("HOST INDEX BUILD LOOKUP AND CORRUPTION GATES PASSED");
 return 0;
}
