/*
 * Host-only smoke test for the native CMS staging format.
 * GCC/clang compile src/GITCWALK.C as C, not C++.
 */
#ifndef STAGE_HOST_ENTRY
#define STAGE_HOST_ENTRY main
#endif
#define main gitcwalk_entry
#include "../src/GITCWALK.C"
#undef main

int gitcapi(unsigned long *p) {
 (void)p;
 return 8; /* Inflater is unused by isolated staging tests. */
}
int STAGE_HOST_ENTRY(void) {
 static unsigned char abc[]={'a','b','c'};
 static unsigned char xyz[]={'x','y','z'};
 unsigned char reference[20],test[20],abc_oid[20];
 char line[256];
 FILE *f;
 unsigned long i,j;
 long at;
 int c;
 if(ref_selftest()!=0) return 22;
 if(!object_oid(3,abc,3,abc_oid)) return 1;
 printf("HOST ABC OID ");
 for(j=0;j<20;j++) printf("%02x",abc_oid[j]);
 putchar('\n');
 for(i=1;i<=4;i++) {
  if(!object_oid((int)i,abc,3,abc_oid)) return 20;
  printf("HOST OID %s ABC ",typenames[i]);
  for(j=0;j<20;j++) printf("%02x",abc_oid[j]);
  putchar('\n');
  if(!object_oid((int)i,abc,0,abc_oid)) return 21;
  printf("HOST OID %s EMPTY ",typenames[i]);
  for(j=0;j<20;j++) printf("%02x",abc_oid[j]);
  putchar('\n');
 }
 for(i=0;i<1808;i++) {
  objtype[i]=(int)(i%4)+1;
  objlen[i]=(i&&i%5==0)?0:3;
  objdata[i]=i%2?xyz:abc;
  use_opt_sha=0;
  if(!object_oid(objtype[i],objdata[i],
                 objlen[i],reference)) return 2;
  use_opt_sha=1;
  if(!object_oid(objtype[i],objdata[i],
                 objlen[i],test)) return 3;
  use_opt_sha=0;
  for(j=0;j<20;j++) if(reference[j]!=test[j]) return 4;
  for(j=0;j<20;j++) objoid[i][j]=test[j];
 }
 if(!stage_objects(1808)) return 5;
 if(verify_stage(0)!=0) return 6;
 if(verify_stage(1)!=0) return 7;
 if(verify_stage(0)!=0) return 8;
 f=fopen("dd:OBJOUT","r+b");
 if(!f) return 9;
 if(!fgets(line,sizeof line,f)) return 10;
 at=ftell(f);
 c=fgetc(f);
 if(c==EOF) return 11;
 if(fseek(f,at,SEEK_SET)!=0) return 12;
 if(fputc(c=='0'?'1':'0',f)==EOF) return 13;
 if(fclose(f)!=0) return 14;
 if(verify_stage(0)==0) return 15;
 f=fopen("dd:OBJOUT","r+b");
 if(!f||fseek(f,at,SEEK_SET)!=0) return 16;
 if(fputc(c,f)==EOF||fclose(f)!=0) return 17;
 if(verify_stage(0)!=0) return 18;
 if(remove("dd:OBJOUT")!=0) return 19;
 puts("HOST STAGING GATES PASSED");
 return 0;
}
