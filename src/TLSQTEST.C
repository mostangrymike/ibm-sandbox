#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <socket.h>

#ifndef SIOCTLSQUERY
#define SIOCTLSQUERY 0x803ADA03UL
#endif

struct querytls {
    char TLSLabel[8];
    char TLSKeyring[50];
};

int main(void)
{
    int s;
    int rc;
    struct querytls q;

    memset(&q, ' ', sizeof(q));
    errno = 0;

    s = socket(AF_INET, SOCK_STREAM, 0);
    printf("socket=%d errno=%d\n", s, errno);
    if (s < 0)
        return 8;

    errno = 0;
    rc = ioctl(s, SIOCTLSQUERY, (char *)&q);
    printf("tlsquery rc=%d errno=%d\n", rc, errno);

    close(s);
    return (rc == 0) ? 0 : 8;
}
