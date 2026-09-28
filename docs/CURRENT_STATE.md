# Current CMS Git milestone

M45 actual z/VM CMS target regression passed on September 28, 2026. GITREC compiled cleanly; the standard M45 compact runner passed both independent original 1,808-object audits, all closures, recovery, failure and original-file protection. CPU 705.89 sec; elapsed 721.23 sec.

M46 adds raw-tree `TREECLOSURE` with full bounded local descendant verification. Its production source, one standard compact GITRUN, mandatory guard, and deep/limit host regression passed complete strict C89 native-stage CI in run 36491728941. Follow-on older-slot fallback, dual-invalid no-output and restored-newer-slot tests passed complete native-stage CI in run 36491830250; PR 23 was squash-merged main at abf855263be41e5dbd8c8000aeb68ab015b72356. M46 is fully host-CI-proven; actual CMS is not yet tested. M46 actual CMS has not yet been exercised.

Next after full merge: from the Mac ibm-sandbox/src directory, run git pull and transfer only GITREC.C and GITRUN.EXEC. On CMS run CMSCLNK GITREC PLAIN and GITRUN. Expect the final marker GITRUN M46 ALL READ ONLY NATIVE GIT TESTS PASSED only on genuine CMS success. Do not alter original GITFIX/M15NEW sealed stage/index/seek/GEN data, selector pointers, or GITPBUF PACK.
