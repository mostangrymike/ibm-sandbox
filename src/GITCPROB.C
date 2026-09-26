/* GCCCMS C89 feasibility probe: CMS hex-record PACK capture. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
static int nib(int c) {
    if(c>='0' && c<='9') return c-'0';
    if(c>='A' && c<='F') return c-'A'+10;
    if(c>='a' && c<='f') return c-'a'+10;
    return -1;
}
static unsigned long be32(const unsigned char *p) {
    return ((unsigned long)p[0]<<24)|((unsigned long)p[1]<<16)
         |((unsigned long)p[2]<<8)|(unsigned long)p[3];
}
int main(int argc,char **argv) {
    FILE *f;
    char line[1024];
    unsigned char hdr[12];
    unsigned long count=0, records=0;
    unsigned long x=0;
    int i,hi,lo;
    clock_t start,end;
    if(argc!=4) {
        puts("Usage: GITCPROB fn ft fm");
        return 4;
    }
    {
        char fileid[40];
        if(strlen(argv[1])>8 || strlen(argv[2])>8 || strlen(argv[3])>2) {
            puts("FAIL invalid CMS fileid"); return 4;
        }
        /* CMS FILEDEF PACKIN DISK fn ft fm must precede execution. */
        f=fopen("dd:PACKIN","r");
    }
    if(!f) { perror("GITCPROB"); return 8; }
    start=clock();
    while(fgets(line,sizeof line,f)) {
        ++records;
        for(i=0;line[i];) {
            if(line[i]==' ' || line[i]=='\n' || line[i]=='\r') {
                ++i; continue;
            }
            hi=nib((unsigned char)line[i++]);
            if(hi<0 || !line[i]) {
                puts("FAIL invalid hex"); fclose(f); return 8;
            }
            lo=nib((unsigned char)line[i++]);
            if(lo<0) { puts("FAIL invalid hex"); fclose(f); return 8; }
            x=(unsigned long)((hi<<4)|lo);
            if(count<12) hdr[count]=(unsigned char)x;
            ++count;
        }
    }
    if(ferror(f)) { puts("FAIL read"); fclose(f); return 8; }
    end=clock();
    fclose(f);
    if(count<12 || hdr[0]!=0x50 || hdr[1]!=0x41 ||
       hdr[2]!=0x43 || hdr[3]!=0x4b) {
        puts("FAIL PACK signature (check ASCII/EBCDIC)");
        return 8;
    }
    printf("VERSION %lu OBJECTS %lu BYTES %lu RECORDS %lu\n",
        be32(hdr+4),be32(hdr+8),count,records);
    printf("CPU TICKS %lu CLOCKS_PER_SEC %lu\n",
        (unsigned long)(end-start),(unsigned long)CLOCKS_PER_SEC);
    if(be32(hdr+4)!=2 || be32(hdr+8)!=1808 ||
       count!=340027UL) {
        puts("FAIL capture metadata mismatch"); return 8;
    }
    puts("PASS CMS hex-record PACK read");
    return 0;
}
