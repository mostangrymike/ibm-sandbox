/* Host-only callback simulator; NOT a production GENCHECK. */
#define GITSEL_VERIFY 1
#include "../src/GITSEL.C"
int git_sel_verify(const char *gen,const char *digest) {
 FILE *f;
 char filename[32],line[64];
 sprintf(filename,"verified_%s.txt",gen);
 f=fopen(filename,"r");
 if(!f) return 0;
 if(!fgets(line,sizeof line,f)) {
  fclose(f);return 0;
 }
 if(fclose(f)!=0) return 0;
 if(strchr(line,'\n')) *strchr(line,'\n')=0;
 return strcmp(line,digest)==0;
}
