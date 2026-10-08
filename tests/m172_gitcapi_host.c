#include <zlib.h>
#include <stddef.h>

int gitcapi(unsigned long *api) {
 const unsigned char *in=(const unsigned char *)api[0];
 unsigned long inlen=api[1];
 unsigned char *out=(unsigned char *)api[2];
 unsigned long outcap=api[3];
 z_stream z;
 int rc;
 z.zalloc=Z_NULL;
 z.zfree=Z_NULL;
 z.opaque=Z_NULL;
 z.next_in=(Bytef *)in;
 z.avail_in=(uInt)inlen;
 z.next_out=(Bytef *)out;
 z.avail_out=(uInt)outcap;
 rc=inflateInit(&z);
 if(rc!=Z_OK) return 8;
 rc=inflate(&z,Z_FINISH);
 api[4]=(unsigned long)z.total_out;
 api[5]=inlen-(unsigned long)z.avail_in;
 inflateEnd(&z);
 return rc==Z_STREAM_END?0:8;
}
