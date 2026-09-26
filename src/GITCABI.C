/* M13 GCCCMS external-call ABI probe. No inflater linked yet.
 * Compile with GCCE (NOASM PARM STD380 and inspect generated ASSEMBLE.
 * Do not LOAD until a matching assembler bridge is installed.
 */
#include <stdio.h>
extern int gitnapi(unsigned long *);
static unsigned long param[6];
int main(void) {
 int rc;
 param[0]=0;
 param[1]=0;
 param[2]=0;
 param[3]=0;
 param[4]=0;
 param[5]=0;
 rc=gitnapi(param);
 printf("GITNAPI RC %d OUTPUT %lu USED %lu\n",
        rc,param[4],param[5]);
 return rc;
}
