/* GCCCMS feasibility gate: binary CMS stream and PACK header. */
/* Compile with GCCCMS; supply a real binary PACK stream as argv[1]. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static unsigned long be32(const unsigned char *p)
{
    return ((unsigned long)p[0]<<24) | ((unsigned long)p[1]<<16)
         | ((unsigned long)p[2]<<8) | (unsigned long)p[3];
}

int main(int argc, char **argv)
{
    FILE *fp;
    unsigned char hdr[12];
    unsigned char buf[8192];
    size_t n;
    unsigned long total = 0;
    clock_t start, end;
    if (argc != 2) {
        puts("Usage: GITCPROB binary-pack-filename");
        return 4;
    }
    fp = fopen(argv[1], "rb");
    if (!fp) {
        perror("GITCPROB fopen");
        return 8;
    }
    start = clock();
    n = fread(hdr, 1, sizeof hdr, fp);
    if (n != sizeof hdr || memcmp(hdr, "PACK", 4) != 0) {
        puts("FAIL: binary stream header unavailable or translated");
        fclose(fp);
        return 8;
    }
    printf("PACK VERSION %lu OBJECTS %lu\n",
           be32(hdr+4), be32(hdr+8));
    if (be32(hdr+4) != 2 || be32(hdr+8) != 1808) {
        puts("FAIL: unexpected capture; refusing throughput result");
        fclose(fp);
        return 8;
    }
    total = (unsigned long)n;
    while ((n = fread(buf, 1, sizeof buf, fp)) != 0)
        total += (unsigned long)n;
    if (ferror(fp)) {
        puts("FAIL: stream read error");
        fclose(fp);
        return 8;
    }
    end = clock();
    fclose(fp);
    printf("BINARY BYTES %lu CPU TICKS %lu CLOCKS_PER_SEC %lu\n",
           total, (unsigned long)(end-start),
           (unsigned long)CLOCKS_PER_SEC);
    if (total != 340027UL) {
        puts("FAIL: capture byte count changed or record framing exposed");
        return 8;
    }
    puts("PASS: binary stream and PACK header");
    return 0;
}
