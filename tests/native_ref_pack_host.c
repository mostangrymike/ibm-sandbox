/* Host adapter exercises actual GITCWALK RPACK parsing with zlib. */
#define main gitcwalk_entry
#include "../src/GITCWALK.C"
#undef main
#include <zlib.h>
int gitcapi(unsigned long *p) {
 z_stream z;
 int rc;
 memset(&z,0,sizeof z);
 if(p[1]>PACKCAP||p[3]>OUTCAP) return 8;
 z.next_in=(Bytef *)p[0];
 z.avail_in=(uInt)p[1];
 z.next_out=(Bytef *)p[2];
 z.avail_out=(uInt)p[3];
 rc=inflateInit(&z);
 if(rc!=Z_OK) return 8;
 rc=inflate(&z,Z_FINISH);
 if(rc==Z_STREAM_END) {
  p[4]=(unsigned long)z.total_out;
  p[5]=(unsigned long)z.total_in;
 }
 inflateEnd(&z);
 return rc==Z_STREAM_END?0:8;
}
int main(int argc,char **argv) {
 char *args[2]={"GITCWALK","RPACK"};
 if(argc==2) {
  if(strcmp(argv[1],"RAPPLY")==0||
     strcmp(argv[1],"XPACK")==0||
     strcmp(argv[1],"XAPPLY")==0||
     strcmp(argv[1],"FPACK")==0)
   args[1]=argv[1];
  else return 4;
 } else if(argc!=1) return 4;
 return gitcwalk_entry(2,args);
}
