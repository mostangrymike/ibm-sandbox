/* Read-only two-slot recovery with real full GEN2 verification. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int rec_active;
static const char *rec_expected[2];
static FILE *rec_open(const char *name,const char *mode) {
 static const char *map[2][4]={
  {"dd:C0STG","dd:C0IDX","dd:C0SEEK","dd:C0GEN"},
  {"dd:C1STG","dd:C1IDX","dd:C1SEEK","dd:C1GEN"}
 };
 if(strcmp(name,"dd:STGIN")==0)
  return fopen(map[rec_active][0],mode);
 if(strcmp(name,"dd:IDXIN")==0)
  return fopen(map[rec_active][1],mode);
 if(strcmp(name,"dd:FIDXIN")==0)
  return fopen(map[rec_active][2],mode);
 if(strcmp(name,"dd:GENIN")==0)
  return fopen(map[rec_active][3],mode);
 return fopen(name,mode);
}
#define fopen rec_open
#define main gitcidx_unused
#include "GITCIDX.C"
#undef main
#undef fopen
#define GITSEL_VERIFY 1
#define main gitsel_unused
#include "GITSEL.C"
#undef main
/* Bind slot record to its explicit CLI name and all four DDs. */
static int rec_manifest_digest(const char *wanted) {
 FILE *f;
 char line[128],hex[41],extra;
 int ok=0;
 f=rec_open("dd:GENIN","r");
 if(!f) return 0;
 if(idx_line(f,line,sizeof line)&&
    idx_line(f,line,sizeof line)&&
    sscanf(line,"DIGEST %40s %c",hex,&extra)==1&&
    strlen(hex)==40&&strcmp(hex,wanted)==0)
  ok=1;
 if(fclose(f)!=0) return 0;
 return ok;
}
int git_sel_verify(const char *name,const char *digest) {
 int i;
 for(i=0;i<2;i++) {
  if(strcmp(name,rec_expected[i])!=0) continue;
  rec_active=i;
  if(!rec_manifest_digest(digest)) continue;
  if(gen_check()==0) return 1;
 }
 return 0;
}
/* M22: validate the complete binary Git tree before emitting entries.
 * Display names as ASCII HEX to avoid CMS code-page ambiguity and
 * unsafe terminals. Never print partially parsed tree records.
 */
static int rec_tree_mode(const unsigned char *mode,
                         unsigned long n) {
 static const unsigned char valid[5][6]={
  {0x31,0x30,0x30,0x36,0x34,0x34},
  {0x31,0x30,0x30,0x37,0x35,0x35},
  {0x31,0x32,0x30,0x30,0x30,0x30},
  {0x31,0x36,0x30,0x30,0x30,0x30},
  {0x34,0x30,0x30,0x30,0x30,0x00}
 };
 static const unsigned long lengths[5]={6,6,6,6,5};
 unsigned int i;
 for(i=0;i<sizeof valid/sizeof valid[0];i++)
  if(lengths[i]==n&&
     memcmp(mode,valid[i],(size_t)n)==0) return 1;
 return 0;
}
static int rec_tree_walk(unsigned long n,int emit) {
 unsigned long at=0,mstart,mlen,nstart,nlen,j,count=0;
 char modes[7];
 while(at<n) {
  mstart=at;
  while(at<n&&idx_body[at]!=0x20&&at-mstart<=6) at++;
  mlen=at-mstart;
  if(mlen<5||mlen>6||at==n||
     !rec_tree_mode(idx_body+mstart,mlen)) return 0;
  for(j=0;j<mlen;j++)
   modes[j]=(char)('0'+idx_body[mstart+j]-0x30);
  modes[mlen]=0;
  at++;
  nstart=at;
  while(at<n&&idx_body[at]!=0) {
   if(idx_body[at]==0x2f) return 0;
   at++;
  }
  nlen=at-nstart;
  if(!nlen||at==n||n-at-1<20) return 0;
  at++;
  if(emit) {
   printf("TREE ENTRY MODE %s NAMELEN %lu OID ",
          modes,nlen);
   idx_print(stdout,idx_body+at);
   putchar('\n');
   for(j=0;j<nlen;j++) {
    if(j%32==0) fputs("TREE NAMEHEX ",stdout);
    printf("%02X",idx_body[nstart+j]);
    if(j%32==31||j+1==nlen) putchar('\n');
   }
  }
  at+=20;
  count++;
 }
 if(emit) printf("TREE ENTRIES %lu\n",count);
 return 1;
}
static int rec_tree(const unsigned char *oid) {
 int pos,rc;
 if(sidx_read()!=0) return 8;
 pos=sidx_locate(oid);
 if(pos<0) {puts("SEEK OID NOT FOUND");return 4;}
 if(sidx[pos].type!=2) {
  puts("OBJECT IS NOT A TREE");
  return 8;
 }
 sidx_silent=1;
 rc=sidx_get(oid);
 sidx_silent=0;
 if(rc!=0) return rc;
 if(!rec_tree_walk(sidx[pos].size,0)) {
  puts("TREE STRUCTURE INVALID");
  return 8;
 }
 puts("TREE DATA BEGIN");
 if(!rec_tree_walk(sidx[pos].size,1)) return 8;
 puts("TREE DATA END");
 return 0;
}
/* Git commit headers and OIDs are ASCII bytes, never CMS text.
 * Validate the entire header before exposing any parsed metadata.
 * Unknown ordinary Git header keys and continuation lines are
 * allowed; the required tree, author and committer are strict.
 */
static int rec_ascii_hex(int c) {
 if(c>=0x30&&c<=0x39) return c-0x30;
 if(c>=0x41&&c<=0x46) return c-0x41+10;
 if(c>=0x61&&c<=0x66) return c-0x61+10;
 return -1;
}
static int rec_ascii_oid(const unsigned char *src,
                         unsigned char *dst) {
 int j,hi,lo;
 for(j=0;j<20;j++) {
  hi=rec_ascii_hex(src[2*j]);
  lo=rec_ascii_hex(src[2*j+1]);
  if(hi<0||lo<0) return 0;
  dst[j]=(unsigned char)((hi<<4)|lo);
 }
 return 1;
}
static int rec_ascii_key(const unsigned char *line,
                         unsigned long n,const char *key) {
 static const unsigned char letters[][10]={
  {0x74,0x72,0x65,0x65,0x20},
  {0x70,0x61,0x72,0x65,0x6e,0x74,0x20},
  {0x61,0x75,0x74,0x68,0x6f,0x72,0x20},
  {0x63,0x6f,0x6d,0x6d,0x69,0x74,0x74,0x65,0x72,0x20}
 };
 static const unsigned int lengths[]={5,7,7,10};
 unsigned int i;
 static const char *names[]={"tree","parent","author","committer"};
 for(i=0;i<4;i++)
  if(strcmp(key,names[i])==0)
   return n>=lengths[i]&&
          memcmp(line,letters[i],lengths[i])==0;
 return 0;
}
static int rec_commit_walk(unsigned long n,int emit) {
 unsigned long at=0,begin,end,len,parents=0,body=0;
 unsigned long parent_start=0,message_start=0;
 unsigned long author=0,committer=0,j;
 int previous_header=0;
 unsigned char binary[20];
 /* Exactly one tree line comes first. */
 while(at<n&&idx_body[at]!=0x0a) at++;
 if(at==n||at!=45||
    !rec_ascii_key(idx_body,at,"tree")||
    !rec_ascii_oid(idx_body+5,binary)) return 0;
 at++;
 parent_start=at;
 /* Git parent lines must precede all other headers. */
 while(at<n) {
  begin=at;
  while(at<n&&idx_body[at]!=0x0a) at++;
  if(at==n) return 0;
  len=at-begin;
  if(!rec_ascii_key(idx_body+begin,len,"parent")) {
   at=begin;break;
  }
  if(len!=47||!rec_ascii_oid(idx_body+begin+7,binary))
   return 0;
  parents++;
  at++;
 }
 /* Scan remaining header records; stop on empty delimiter line. */
 while(at<n) {
  begin=at;
  while(at<n&&idx_body[at]!=0x0a) at++;
  if(at==n) return 0;
  len=at-begin;
  if(len==0) {at++;message_start=at;body=1;break;}
  if(idx_body[begin]==0x20) {
   /* Folded gpgsig/mergetag header, not a new field. */
   if(!previous_header||len==1) return 0;
  } else {
   end=begin;
   while(end<at&&idx_body[end]!=0x20) {
    if(!((idx_body[end]>=0x61&&idx_body[end]<=0x7a)||
         (idx_body[end]>=0x30&&idx_body[end]<=0x39)||
          idx_body[end]==0x2d)) return 0;
    end++;
   }
   if(end==begin||end==at||end+1==at) return 0;
   if(rec_ascii_key(idx_body+begin,len,"tree")||
      rec_ascii_key(idx_body+begin,len,"parent"))
    return 0;
   if(rec_ascii_key(idx_body+begin,len,"author")) {
    if(author++) return 0;
   }
   if(rec_ascii_key(idx_body+begin,len,"committer")) {
    if(committer++) return 0;
   }
   previous_header=1;
  }
  at++;
 }
 if(!body||author!=1||committer!=1) return 0;
 if(emit) {
  puts("COMMIT DATA BEGIN");
  fputs("COMMIT TREE ",stdout);
  if(!rec_ascii_oid(idx_body+5,binary)) return 0;
  idx_print(stdout,binary);putchar('\n');
  at=parent_start;
  for(j=0;j<parents;j++) {
   at+=7;
   if(!rec_ascii_oid(idx_body+at,binary)) return 0;
   fputs("COMMIT PARENT ",stdout);
   idx_print(stdout,binary);putchar('\n');
   at+=41;
  }
  printf("COMMIT PARENTS %lu\n",parents);
  printf("COMMIT MESSAGE BYTES %lu\n",n-message_start);
  puts("COMMIT DATA END");
 }
 return 1;
}
static int rec_commit(const unsigned char *oid) {
 int pos,rc;
 if(sidx_read()!=0) return 8;
 pos=sidx_locate(oid);
 if(pos<0) {puts("SEEK OID NOT FOUND");return 4;}
 if(sidx[pos].type!=1) {
  puts("OBJECT IS NOT A COMMIT");return 8;
 }
 sidx_silent=1;
 rc=sidx_get(oid);
 sidx_silent=0;
 if(rc!=0) return rc;
 if(!rec_commit_walk(sidx[pos].size,0)) {
  puts("COMMIT STRUCTURE INVALID");return 8;
 }
 if(!rec_commit_walk(sidx[pos].size,1)) return 8;
 return 0;
}

/* M27: follow the FIRST parent only within the same authenticated
 * generation. Verify the entire child AND the referenced parent body
 * before emitting any parent metadata. No cross-generation mixing.
 */
static int rec_firstpar(const unsigned char *child) {
 unsigned char parent[20],tree_oid[20];
 unsigned long first=46,sz;
 int pos,rc;
 if(sidx_read()!=0) return 8;
 pos=sidx_locate(child);
 if(pos<0) {puts("SEEK OID NOT FOUND");return 4;}
 if(sidx[pos].type!=1) {
  puts("OBJECT IS NOT A COMMIT");return 8;
 }
 sz=sidx[pos].size;
 sidx_silent=1;
 rc=sidx_get(child);
 sidx_silent=0;
 if(rc!=0) return rc;
 if(!rec_commit_walk(sz,0)) {
  puts("COMMIT STRUCTURE INVALID");return 8;
 }
 if(sz<=first||!rec_ascii_key(idx_body+first,sz-first,
                                "parent")) {
  puts("ROOT COMMIT HAS NO FIRST PARENT");return 4;
 }
 if(!rec_ascii_oid(idx_body+first+7,parent)) return 8;
 pos=sidx_locate(parent);
 if(pos<0) {puts("FIRST PARENT OBJECT NOT FOUND");return 4;}
 if(sidx[pos].type!=1) {
  puts("FIRST PARENT IS NOT A COMMIT");return 8;
 }
 sz=sidx[pos].size;
 sidx_silent=1;
 rc=sidx_get(parent);
 sidx_silent=0;
 if(rc!=0) return rc;
 if(!rec_commit_walk(sz,0)) {
  puts("FIRST PARENT STRUCTURE INVALID");return 8;
 }
 if(!rec_ascii_oid(idx_body+5,tree_oid)) return 8;
 puts("FIRST PARENT VERIFIED");
 fputs("FIRST PARENT OID ",stdout);
 idx_print(stdout,parent);putchar('\n');
 fputs("FIRST PARENT TREE ",stdout);
 idx_print(stdout,tree_oid);putchar('\n');
 return 0;
}
/* M28: bounded, read-only first-parent ancestry.
 * Each hop must be a fully rehashed and structurally valid Git commit
 * in the SAME already verified generation. Do not emit intermediate
 * ancestor results; missing or corrupt links fail closed.
 */
static int rec_ancestor(const unsigned char *starting,
                        unsigned int depth) {
 unsigned char current[20],next[20],tree[20];
 unsigned long sz;
 unsigned int hop;
 int pos,rc;
 if(sidx_read()!=0) return 8;
 memcpy(current,starting,20);
 for(hop=0;hop<=depth;hop++) {
  pos=sidx_locate(current);
  if(pos<0) {
   puts("ANCESTOR COMMIT NOT FOUND");return 4;
  }
  if(sidx[pos].type!=1) {
   puts("ANCESTOR OBJECT IS NOT A COMMIT");return 8;
  }
  sz=sidx[pos].size;
  sidx_silent=1;
  rc=sidx_get(current);
  sidx_silent=0;
  if(rc!=0) return rc;
  if(!rec_commit_walk(sz,0)) {
   puts("ANCESTOR COMMIT STRUCTURE INVALID");return 8;
  }
  if(hop==depth) {
   if(!rec_ascii_oid(idx_body+5,tree)) return 8;
   printf("ANCESTOR VERIFIED DEPTH %u\n",depth);
   fputs("ANCESTOR OID ",stdout);
   idx_print(stdout,current);putchar('\n');
   fputs("ANCESTOR TREE ",stdout);
   idx_print(stdout,tree);putchar('\n');
   return 0;
  }
  if(sz<=46||!rec_ascii_key(idx_body+46,sz-46,"parent")) {
   puts("ANCESTOR ROOT REACHED");return 4;
  }
  if(!rec_ascii_oid(idx_body+53,next)) return 8;
  memcpy(current,next,20);
 }
 return 8;
}
/* M29: verify every first-parent hop before showing any history.
 * Keep the bounded chain and tree IDs in local fixed-size arrays;
 * only commit to output after every linked object verifies.
 */
static int rec_history(const unsigned char *starting,
                       unsigned int depth) {
 unsigned char commits[17][20],trees[17][20],next[20];
 unsigned long sz;
 unsigned int hop,j;
 int pos,rc;
 if(sidx_read()!=0) return 8;
 memcpy(commits[0],starting,20);
 for(hop=0;hop<=depth;hop++) {
  pos=sidx_locate(commits[hop]);
  if(pos<0) {
   puts("HISTORY COMMIT NOT FOUND");return 4;
  }
  if(sidx[pos].type!=1) {
   puts("HISTORY OBJECT IS NOT A COMMIT");return 8;
  }
  sz=sidx[pos].size;
  sidx_silent=1;
  rc=sidx_get(commits[hop]);
  sidx_silent=0;
  if(rc!=0) return rc;
  if(!rec_commit_walk(sz,0)) {
   puts("HISTORY COMMIT STRUCTURE INVALID");return 8;
  }
  if(!rec_ascii_oid(idx_body+5,trees[hop])) return 8;
  if(hop==depth) break;
  if(sz<=46||!rec_ascii_key(idx_body+46,sz-46,"parent")) {
   puts("HISTORY ROOT REACHED");return 4;
  }
  if(!rec_ascii_oid(idx_body+53,next)) return 8;
  memcpy(commits[hop+1],next,20);
 }
 puts("HISTORY DATA BEGIN");
 for(j=0;j<=depth;j++) {
  printf("HISTORY HOP %u OID ",j);
  idx_print(stdout,commits[j]);
  putchar('\n');
  printf("HISTORY HOP %u TREE ",j);
  idx_print(stdout,trees[j]);
  putchar('\n');
 }
 printf("HISTORY HOPS %u\n",depth);
 puts("HISTORY DATA END");
 return 0;
}
/* M30: numbered parent of a fully verified Git commit.
 * Parent ordinals are 1 based and include merge's second parent.
 * Never output a parent OID until its body authenticates.
 */
static int rec_parent(const unsigned char *child,
                      unsigned int ordinal) {
 unsigned char target[20],tree[20];
 unsigned long at=46,begin,len,sz;
 unsigned int found=0;
 int pos,rc;
 if(sidx_read()!=0) return 8;
 pos=sidx_locate(child);
 if(pos<0) {puts("PARENT CHILD NOT FOUND");return 4;}
 if(sidx[pos].type!=1) {
  puts("PARENT CHILD NOT COMMIT");return 8;
 }
 sz=sidx[pos].size;
 sidx_silent=1;
 rc=sidx_get(child);
 sidx_silent=0;
 if(rc!=0) return rc;
 if(!rec_commit_walk(sz,0)) {
  puts("PARENT CHILD INVALID");return 8;
 }
 while(at<sz) {
  begin=at;
  while(at<sz&&idx_body[at]!=0x0a) at++;
  if(at==sz) return 8;
  len=at-begin;
  if(!rec_ascii_key(idx_body+begin,len,"parent")) break;
  found++;
  if(found==ordinal) {
   if(!rec_ascii_oid(idx_body+begin+7,target)) return 8;
   break;
  }
  at++;
 }
 if(found<ordinal) {
  puts("PARENT ORDINAL NOT FOUND");return 4;
 }
 pos=sidx_locate(target);
 if(pos<0) {puts("PARENT OBJECT NOT FOUND");return 4;}
 if(sidx[pos].type!=1) {
  puts("PARENT OBJECT NOT COMMIT");return 8;
 }
 sz=sidx[pos].size;
 sidx_silent=1;
 rc=sidx_get(target);
 sidx_silent=0;
 if(rc!=0) return rc;
 if(!rec_commit_walk(sz,0)) {
  puts("PARENT OBJECT INVALID");return 8;
 }
 if(!rec_ascii_oid(idx_body+5,tree)) return 8;
 printf("PARENT VERIFIED ORDINAL %u\n",ordinal);
 fputs("PARENT OID ",stdout);
 idx_print(stdout,target);putchar('\n');
 fputs("PARENT TREE ",stdout);
 idx_print(stdout,tree);putchar('\n');
 return 0;
}
/* M34: authenticate each direct root-tree link.
 * Gitlink entries refer to external repositories and are skipped.
 * The fixed bound prevents untrusted trees exhausting CMS memory.
 */
static int rec_root_links(const unsigned char *root,
                          unsigned int depth,
                          unsigned int *budget) {
 unsigned char refs[256][20],types[256];
 unsigned long at=0,ms,ml,n,sz;
 unsigned int count=0,entries=0,j;
 int pos,rc;
 static const unsigned char gitlink[6]={
  0x31,0x36,0x30,0x30,0x30,0x30
 };
 pos=sidx_locate(root);
 if(pos<0) {puts("ROOT LINK TREE NOT FOUND");return 4;}
 if(sidx[pos].type!=2) {
  puts("ROOT LINK OBJECT NOT TREE");return 8;
 }
 sz=sidx[pos].size;
 sidx_silent=1;
 rc=sidx_get(root);
 sidx_silent=0;
 if(rc!=0) return rc;
 if(!rec_tree_walk(sz,0)) {
  puts("ROOT LINK TREE INVALID");return 8;
 }
 if(*budget==0) {
  puts("NESTED LINK BUDGET EXCEEDED");return 8;
 }
 (*budget)--;
 while(at<sz) {
  ms=at;
  while(at<sz&&idx_body[at]!=0x20) at++;
  ml=at-ms;
  at++;
  while(at<sz&&idx_body[at]!=0) at++;
  at++;
  /* M43: external Gitlinks consume the entry budget too. */
  if(entries==256) {
   puts("ROOT LINK LIMIT EXCEEDED");return 8;
  }
  entries++;
  if(ml==6&&memcmp(idx_body+ms,gitlink,6)==0) {
   at+=20;
   continue;
  }
  types[count]=(idx_body[ms]==0x34)?2:3;
  memcpy(refs[count],idx_body+at,20);
  count++;
  at+=20;
 }
 for(j=0;j<count;j++) {
  pos=sidx_locate(refs[j]);
  if(pos<0) {
   puts("ROOT ENTRY OBJECT NOT FOUND");return 4;
  }
  if(sidx[pos].type!=types[j]) {
   puts("ROOT ENTRY TYPE MISMATCH");return 8;
  }
  /* M39: a subtree at positive depth will be rehashed
   * and parsed by the recursive call below. Avoid doing
   * the same indexed read and parse twice.
   */
  if(types[j]==2&&depth>0) continue;
  n=sidx[pos].size;
  sidx_silent=1;
  rc=sidx_get(refs[j]);
  sidx_silent=0;
  if(rc!=0) return rc;
  if(types[j]==2&&!rec_tree_walk(n,0)) {
   puts("ROOT ENTRY SUBTREE INVALID");return 8;
  }
 }
 if(depth>0) {
  for(j=0;j<count;j++) {
   if(types[j]!=2) continue;
   rc=rec_root_links(refs[j],depth-1,budget);
   if(rc!=0) return rc;
  }
 }
 return 0;
}
/* M44: iterative full local tree closure. A bounded work stack
 * avoids unbounded C recursion on deeply nested Git trees.
 * Every tree and local blob is rehashed inside the selected seal.
 */
static int rec_root_closure(const unsigned char *root,
                            unsigned int *budget) {
 unsigned char pending[1024][20],current[20];
 unsigned char refs[256][20],types[256];
 unsigned long at,ms,ml,sz;
 unsigned int top=0,count,entries,j;
 int pos,rc;
 static const unsigned char gitlink[6]={
  0x31,0x36,0x30,0x30,0x30,0x30
 };
 memcpy(pending[top++],root,20);
 while(top>0) {
  memcpy(current,pending[--top],20);
  if(*budget==0) {
   puts("NESTED LINK BUDGET EXCEEDED");return 8;
  }
  (*budget)--;
  pos=sidx_locate(current);
  if(pos<0) {puts("ROOT LINK TREE NOT FOUND");return 4;}
  if(sidx[pos].type!=2) {
   puts("ROOT LINK OBJECT NOT TREE");return 8;
  }
  sz=sidx[pos].size;
  sidx_silent=1;
  rc=sidx_get(current);
  sidx_silent=0;
  if(rc!=0) return rc;
  if(!rec_tree_walk(sz,0)) {
   puts("ROOT LINK TREE INVALID");return 8;
  }
  at=0;count=0;entries=0;
  while(at<sz) {
   ms=at;
   while(at<sz&&idx_body[at]!=0x20) at++;
   ml=at-ms;at++;
   while(at<sz&&idx_body[at]!=0) at++;
   at++;
   if(entries==256) {
    puts("ROOT LINK LIMIT EXCEEDED");return 8;
   }
   entries++;
   if(ml==6&&memcmp(idx_body+ms,gitlink,6)==0) {
    at+=20;continue;
   }
   types[count]=(idx_body[ms]==0x34)?2:3;
   memcpy(refs[count++],idx_body+at,20);
   at+=20;
  }
  for(j=0;j<count;j++) {
   pos=sidx_locate(refs[j]);
   if(pos<0) {
    puts("ROOT ENTRY OBJECT NOT FOUND");return 4;
   }
   if(sidx[pos].type!=types[j]) {
    puts("ROOT ENTRY TYPE MISMATCH");return 8;
   }
   if(types[j]==2) {
    if(top==1024) {
     puts("NESTED LINK BUDGET EXCEEDED");return 8;
    }
    memcpy(pending[top++],refs[j],20);
   } else {
    sidx_silent=1;
    rc=sidx_get(refs[j]);
    sidx_silent=0;
    if(rc!=0) return rc;
   }
  }
 }
 return 0;
}
/* M46: verify complete closure from a raw tree object ID,
 * without needing a commit or commit-relative path.
 * Release a directory listing only after every local link passes.
 */
static int rec_tree_closure(const unsigned char *oid) {
 unsigned int budget=1024;
 unsigned long n;
 int pos,rc;
 if(sidx_read()!=0) return 8;
 rc=rec_root_closure(oid,&budget);
 if(rc!=0) return rc;
 pos=sidx_locate(oid);
 n=sidx[pos].size;
 sidx_silent=1;
 rc=sidx_get(oid);
 sidx_silent=0;
 if(rc!=0) return rc;
 if(!rec_tree_walk(n,0)) {
  puts("TREE STRUCTURE INVALID");return 8;
 }
 puts("TREE FULL CLOSURE VERIFIED");
 puts("TREE DATA BEGIN");
 if(!rec_tree_walk(n,1)) return 8;
 puts("TREE DATA END");
 return 0;
}
/* M31: authenticate ALL parents of a commit before any output.
 * Every parent must exist and be a valid commit in the SAME
 * fully verified generation; no partial merge-parent lists.
 */
static int rec_parents(const unsigned char *child,
                       int check_trees,int check_child,
                       int check_links,unsigned int link_depth,
                       int report_depth) {
 unsigned char parents[16][20],trees[16][20];
 unsigned char child_tree[20];
 unsigned long at=46,begin,len,sz;
 unsigned int count=0,j,budget=1024;
 int pos,rc;
 if(sidx_read()!=0) return 8;
 pos=sidx_locate(child);
 if(pos<0) {puts("PARENTS CHILD NOT FOUND");return 4;}
 if(sidx[pos].type!=1) {
  puts("PARENTS CHILD NOT COMMIT");return 8;
 }
 sz=sidx[pos].size;
 sidx_silent=1;
 rc=sidx_get(child);
 sidx_silent=0;
 if(rc!=0) return rc;
 if(!rec_commit_walk(sz,0)) {
  puts("PARENTS CHILD INVALID");return 8;
 }
 if(check_child) {
  if(!rec_ascii_oid(idx_body+5,child_tree)) return 8;
 }
 while(at<sz) {
  begin=at;
  while(at<sz&&idx_body[at]!=0x0a) at++;
  if(at==sz) return 8;
  len=at-begin;
  if(!rec_ascii_key(idx_body+begin,len,"parent")) break;
  if(count==16) {
   puts("PARENTS LIMIT EXCEEDED");return 8;
  }
  if(!rec_ascii_oid(idx_body+begin+7,parents[count]))
   return 8;
  count++;
  at++;
 }
 for(j=0;j<count;j++) {
  pos=sidx_locate(parents[j]);
  if(pos<0) {puts("PARENTS OBJECT NOT FOUND");return 4;}
  if(sidx[pos].type!=1) {
   puts("PARENTS OBJECT NOT COMMIT");return 8;
  }
  sz=sidx[pos].size;
  sidx_silent=1;
  rc=sidx_get(parents[j]);
  sidx_silent=0;
  if(rc!=0) return rc;
  if(!rec_commit_walk(sz,0)) {
   puts("PARENTS OBJECT INVALID");return 8;
  }
  if(!rec_ascii_oid(idx_body+5,trees[j])) return 8;
 }
 if(check_trees) {
  for(j=0;j<count;j++) {
   pos=sidx_locate(trees[j]);
   if(pos<0) {
    puts("PARENT ROOT TREE NOT FOUND");return 4;
   }
   if(sidx[pos].type!=2) {
    puts("PARENT ROOT OBJECT NOT TREE");return 8;
   }
   sz=sidx[pos].size;
   sidx_silent=1;
   rc=sidx_get(trees[j]);
   sidx_silent=0;
   if(rc!=0) return rc;
   if(!rec_tree_walk(sz,0)) {
    puts("PARENT ROOT TREE INVALID");return 8;
   }
  }
 }
 if(check_child) {
  pos=sidx_locate(child_tree);
  if(pos<0) {puts("CHILD ROOT TREE NOT FOUND");return 4;}
  if(sidx[pos].type!=2) {
   puts("CHILD ROOT OBJECT NOT TREE");return 8;
  }
  sz=sidx[pos].size;
  sidx_silent=1;
  rc=sidx_get(child_tree);
  sidx_silent=0;
  if(rc!=0) return rc;
  if(!rec_tree_walk(sz,0)) {
   puts("CHILD ROOT TREE INVALID");return 8;
  }
  if(check_links) {
   rc=check_links==2?
      rec_root_closure(child_tree,&budget):
      rec_root_links(child_tree,link_depth,&budget);
   if(rc!=0) return rc;
   for(j=0;j<count;j++) {
    rc=check_links==2?
       rec_root_closure(trees[j],&budget):
       rec_root_links(trees[j],link_depth,&budget);
    if(rc!=0) return rc;
   }
   if(check_links==2) {
    puts("FULL ROOT CLOSURE VERIFIED");
   } else if(report_depth==2) {
    puts("NESTED ROOT LINKS VERIFIED");
    puts("DEEP ROOT LINKS VERIFIED");
    puts("LINK DEPTH 2 VERIFIED");
   } else if(report_depth)
    printf("LINK DEPTH %u VERIFIED\n",link_depth);
   else if(link_depth>1)
    puts("DEEP ROOT LINKS VERIFIED");
   else if(link_depth==1)
    puts("NESTED ROOT LINKS VERIFIED");
   else puts("ROOT DIRECT LINKS VERIFIED");
  } else puts("COMMIT ROOTS VERIFIED");
 } else if(check_trees) {
  puts("PARENT ROOT TREES VERIFIED");
 }
 puts("PARENTS DATA BEGIN");
 for(j=0;j<count;j++) {
  printf("PARENTS ORDINAL %u OID ",j+1);
  idx_print(stdout,parents[j]);putchar('\n');
  printf("PARENTS ORDINAL %u TREE ",j+1);
  idx_print(stdout,trees[j]);putchar('\n');
 }
 printf("PARENTS COUNT %u\n",count);
 puts("PARENTS DATA END");
 return 0;
}
/* M24: follow a commit's authenticated tree in the SAME
 * fully verified generation. Do not expose tree entries if either
 * linked object is missing, mis-typed or structurally invalid.
 */
static int rec_root(const unsigned char *oid) {
 unsigned char tree_oid[20];
 int pos,rc;
 if(sidx_read()!=0) return 8;
 pos=sidx_locate(oid);
 if(pos<0) {puts("SEEK OID NOT FOUND");return 4;}
 if(sidx[pos].type!=1) {
  puts("OBJECT IS NOT A COMMIT");return 8;
 }
 sidx_silent=1;
 rc=sidx_get(oid);
 sidx_silent=0;
 if(rc!=0) return rc;
 if(!rec_commit_walk(sidx[pos].size,0)) {
  puts("COMMIT STRUCTURE INVALID");return 8;
 }
 if(!rec_ascii_oid(idx_body+5,tree_oid)) return 8;
 /* rec_tree reopens only rec_active's already selected inputs. */
 return rec_tree(tree_oid);
}

/* M24: follow a raw-byte relative Git path from a commit.
 * PATHHEX is CLI text; after decoding it, all object content is
 * binary Git data, including tree names and mode fields.
 * Authenticate every linked object before printing any path result.
 */
static int rec_path(const unsigned char *commit_oid,
                    const unsigned char *path,unsigned long length,
                    int contents,unsigned int dir_depth) {
 unsigned char next[20],found[20];
 unsigned long start=0,end,at,mode_start,mode_len,name_start;
 unsigned long name_len,object_size;
 int pos,rc,expected_type=0,is_gitlink=0;
 unsigned int budget=1024;
 if(sidx_read()!=0) return 8;
 pos=sidx_locate(commit_oid);
 if(pos<0) {puts("SEEK OID NOT FOUND");return 4;}
 if(sidx[pos].type!=1) {
  puts("OBJECT IS NOT A COMMIT");return 8;
 }
 sidx_silent=1;
 rc=sidx_get(commit_oid);
 sidx_silent=0;
 if(rc!=0) return rc;
 if(!rec_commit_walk(sidx[pos].size,0)) {
  puts("COMMIT STRUCTURE INVALID");return 8;
 }
 if(!rec_ascii_oid(idx_body+5,next)) return 8;
 /* M47: authenticate the ENTIRE commit root before any PATH
  * metadata, even if the requested entry itself is intact.
  */
 if(contents>=6) {
  rc=rec_root_closure(next,&budget);
  if(rc!=0) return rc;
 }
 while(start<length) {
  end=start;
  while(end<length&&path[end]!=0x2f) end++;
  pos=sidx_locate(next);
  if(pos<0) {puts("PATH TREE NOT FOUND");return 4;}
  if(sidx[pos].type!=2) {
   puts("PATH EXPECTED TREE");return 8;
  }
  object_size=sidx[pos].size;
  sidx_silent=1;
  rc=sidx_get(next);
  sidx_silent=0;
  if(rc!=0) return rc;
  if(!rec_tree_walk(object_size,0)) {
   puts("PATH TREE STRUCTURE INVALID");return 8;
  }
  at=0;pos=-1;
  while(at<object_size) {
   mode_start=at;
   while(idx_body[at]!=0x20) at++;
   mode_len=at-mode_start;
   at++;
   name_start=at;
   while(idx_body[at]!=0) at++;
   name_len=at-name_start;
   at++;
   if(name_len==end-start&&
      memcmp(idx_body+name_start,path+start,
             (size_t)name_len)==0) {
    is_gitlink=(mode_len==6&&
      memcmp(idx_body+mode_start,
             "\x31\x36\x30\x30\x30\x30",6)==0);
    expected_type=(mode_len==5)?2:
                  (is_gitlink?1:3);
    memcpy(found,idx_body+at,20);
    pos=1;break;
   }
   at+=20;
  }
  if(pos<0) {puts("PATH NOT FOUND");return 4;}
  if(end<length) {
   if(expected_type!=2) {
    puts("PATH COMPONENT NOT A TREE");return 8;
   }
   memcpy(next,found,20);
   start=end+1;
   continue;
  }
  if(is_gitlink) {
   if(contents&&contents!=6) {
    puts(contents>=2?"LSDIR REQUIRES A TREE":
         "PATHCAT REQUIRES A LOCAL BLOB");return 8;
   }
   if(contents==6)
    puts("COMMIT ROOT FULL CLOSURE VERIFIED");
   puts("PATH GITLINK (EXTERNAL COMMIT)");
   fputs("PATH OID ",stdout);
   idx_print(stdout,found);putchar('\n');
   return 0;
  }
  pos=sidx_locate(found);
  if(pos<0) {puts("PATH OBJECT NOT FOUND");return 4;}
  if(sidx[pos].type!=expected_type) {
   puts("PATH OBJECT TYPE MISMATCH");return 8;
  }
  if((contents==1||contents==7)&&expected_type!=3) {
   puts("PATHCAT REQUIRES A BLOB");return 8;
  }
  if(contents>=2&&contents!=6&&contents!=7&&
     expected_type!=2) {
   puts("LSDIR REQUIRES A TREE");return 8;
  }
  object_size=sidx[pos].size;
  sidx_silent=1;
  rc=sidx_get(found);
  sidx_silent=0;
  if(rc!=0) return rc;
  /* M40: fully parse returned trees before ANY path output. */
  if(expected_type==2&&contents>=3) {
   rc=contents==5?
      rec_root_closure(found,&budget):
      rec_root_links(found,dir_depth,&budget);
   if(rc!=0) return rc;
   /* The walker reuses idx_body for linked children.
    * Reload the authenticated directory before listing.
    */
   sidx_silent=1;
   rc=sidx_get(found);
   sidx_silent=0;
   if(rc!=0) return rc;
   if(!rec_tree_walk(object_size,0)) return 8;
  } else if(expected_type==2&&
            !rec_tree_walk(object_size,0)) {
   puts("DIRECTORY TREE STRUCTURE INVALID");return 8;
  }
  if(contents>=6)
   puts("COMMIT ROOT FULL CLOSURE VERIFIED");
  if(contents==3) puts("DIRECTORY LINKS VERIFIED");
  if(contents==4)
   printf("DIRECTORY LINK DEPTH %u VERIFIED\n",dir_depth);
  if(contents==5) puts("DIRECTORY FULL CLOSURE VERIFIED");
  printf("PATH OBJECT TYPE %d SIZE %lu OID ",
         expected_type,object_size);
  idx_print(stdout,found);putchar('\n');
  if(contents>=2&&contents!=6&&contents!=7) {
   puts("TREE DATA BEGIN");
   if(!rec_tree_walk(object_size,1)) return 8;
   puts("TREE DATA END");
  }
  if(contents==1||contents==7) {
   unsigned long j;
   puts("PATH DATA BEGIN");
   for(j=0;j<object_size;j++) {
    if(j%32==0) fputs("PATH HEX ",stdout);
    printf("%02X",idx_body[j]);
    if(j%32==31||j+1==object_size) putchar('\n');
   }
   puts("PATH DATA END");
  }
  return 0;
 }
 return 8;
}
static int rec_path_hex(const char *s,unsigned char *dst,
                        unsigned long *length) {
 unsigned long j,n;
 int hi,lo;
 n=(unsigned long)strlen(s);
 if(n<2||n>510||n%2) return 0;
 *length=n/2;
 for(j=0;j<*length;j++) {
  hi=idx_nib((unsigned char)s[2*j]);
  lo=idx_nib((unsigned char)s[2*j+1]);
  if(hi<0||lo<0) return 0;
  dst[j]=(unsigned char)((hi<<4)|lo);
  if(dst[j]==0||(*length>1&&
     (j==0||j==*length-1)&&dst[j]==0x2f)||
     (j>0&&dst[j]==0x2f&&dst[j-1]==0x2f))
   return 0;
 }
 return 1;
}

/* SELECT stays read-only. GET adds a verified indexed object
 * lookup only after a complete native GENCHECK has selected a slot.
 * Never call SGET on an unverified candidate or infer an active
 * generation from a selector's unchecked contents.
 */
int main(int argc,char **argv) {
 struct slot a,b;
 unsigned char oid[20],path[255];
 unsigned long pathlen=0;
 unsigned int depth=0,dir_depth=0;
 unsigned long d;
 int get,full,tree,commit,root,path_command,pathcat;
 int pathfull,pathfullcat;
 int lsdir,lsdirv,lsdirdepth,lsdirfull;
 int firstpar,ancestor,history;
 int parent_cmd,parents_cmd;
 int roots_cmd,commitroots_cmd,linkroots_cmd;
 int nestedlinks_cmd,deeplinks_cmd,depthlinks_cmd;
 int linkbatch_cmd,closure_cmd,treeclosure_cmd,rc;
 get=argc==5&&strcmp(argv[1],"GET")==0;
 full=argc==5&&strcmp(argv[1],"CATHEX")==0;
 tree=argc==5&&strcmp(argv[1],"TREE")==0;
 commit=argc==5&&strcmp(argv[1],"COMMIT")==0;
 root=argc==5&&strcmp(argv[1],"LSROOT")==0;
 path_command=argc==6&&strcmp(argv[1],"PATH")==0;
 pathcat=argc==6&&strcmp(argv[1],"PATHCAT")==0;
 pathfull=argc==6&&strcmp(argv[1],"PATHFULL")==0;
 pathfullcat=argc==6&&strcmp(argv[1],"PATHFULLCAT")==0;
 lsdir=argc==6&&strcmp(argv[1],"LSDIR")==0;
 lsdirv=argc==6&&strcmp(argv[1],"LSDIRV")==0;
 lsdirdepth=argc==7&&strcmp(argv[1],"LSDIRDEPTH")==0;
 lsdirfull=argc==6&&strcmp(argv[1],"LSDIRFULL")==0;
 firstpar=argc==5&&strcmp(argv[1],"FIRSTPAR")==0;
 ancestor=argc==6&&strcmp(argv[1],"ANCESTOR")==0;
 history=argc==6&&strcmp(argv[1],"HISTORY")==0;
 parent_cmd=argc==6&&strcmp(argv[1],"PARENT")==0;
 parents_cmd=argc==5&&strcmp(argv[1],"PARENTS")==0;
 roots_cmd=argc==5&&strcmp(argv[1],"PARENTROOTS")==0;
 commitroots_cmd=argc==5&&strcmp(argv[1],"COMMITROOTS")==0;
 linkroots_cmd=argc==5&&strcmp(argv[1],"ROOTLINKS")==0;
 nestedlinks_cmd=argc==5&&strcmp(argv[1],"NESTLINKS")==0;
 deeplinks_cmd=argc==5&&strcmp(argv[1],"DEEPLINKS")==0;
 depthlinks_cmd=argc==6&&strcmp(argv[1],"DEPTHLINKS")==0;
 linkbatch_cmd=argc==5&&strcmp(argv[1],"LINKBATCH")==0;
 closure_cmd=argc==5&&strcmp(argv[1],"CLOSURE")==0;
 treeclosure_cmd=argc==5&&strcmp(argv[1],"TREECLOSURE")==0;
 if((!get&&!full&&!tree&&!commit&&!root&&!path_command&&
     !pathcat&&!pathfull&&!pathfullcat&&
     !lsdir&&!lsdirv&&
     !lsdirdepth&&
     !lsdirfull&&
     !firstpar&&!ancestor&&
     !history&&!parent_cmd&&!parents_cmd&&
     !roots_cmd&&!commitroots_cmd&&!linkroots_cmd&&
     !nestedlinks_cmd&&!deeplinks_cmd&&
     !depthlinks_cmd&&!linkbatch_cmd&&!closure_cmd&&
     !treeclosure_cmd&&
     (argc!=4||strcmp(argv[1],"SELECT")!=0))||
    !proper_name(argv[2])||!proper_name(argv[3])||
    strcmp(argv[2],argv[3])==0) {
  puts("GITREC SELECT C0NAME C1NAME");
  puts("GITREC GET C0NAME C1NAME OID40");
  puts("GITREC CATHEX C0NAME C1NAME OID40");
  puts("GITREC TREE C0NAME C1NAME OID40");
  puts("GITREC COMMIT C0NAME C1NAME OID40");
  puts("GITREC LSROOT C0NAME C1NAME COMMIT_OID40");
  puts("GITREC PATH C0NAME C1NAME COMMIT_OID40 PATHHEX");
  puts("GITREC PATHCAT C0NAME C1NAME COMMIT_OID40 PATHHEX");
  puts("GITREC PATHFULL C0 C1 COMMIT_OID40 PATHHEX");
  puts("GITREC PATHFULLCAT C0 C1 COMMIT_OID40 PATHHEX");
  puts("GITREC LSDIR C0NAME C1NAME COMMIT_OID40 DIRHEX");
  puts("GITREC LSDIRV C0 C1 COMMIT_OID40 DIRHEX");
  puts("GITREC LSDIRDEPTH C0 C1 OID40 DIRHEX DEPTH");
  puts("GITREC LSDIRFULL C0 C1 COMMIT_OID40 DIRHEX");
  puts("GITREC FIRSTPAR C0NAME C1NAME COMMIT_OID40");
  puts("GITREC ANCESTOR C0NAME C1NAME COMMIT_OID40 DEPTH");
  puts("GITREC HISTORY C0NAME C1NAME COMMIT_OID40 DEPTH");
  puts("GITREC PARENT C0NAME C1NAME COMMIT_OID40 N");
  puts("GITREC PARENTS C0NAME C1NAME COMMIT_OID40");
  puts("GITREC PARENTROOTS C0NAME C1NAME OID40");
  puts("GITREC COMMITROOTS C0NAME C1NAME OID40");
  puts("GITREC ROOTLINKS C0NAME C1NAME COMMIT_OID40");
  puts("GITREC NESTLINKS C0NAME C1NAME COMMIT_OID40");
  puts("GITREC DEEPLINKS C0NAME C1NAME COMMIT_OID40");
  puts("GITREC DEPTHLINKS C0 C1 COMMIT_OID40 DEPTH");
  puts("GITREC LINKBATCH C0 C1 COMMIT_OID40");
  puts("GITREC CLOSURE C0 C1 COMMIT_OID40");
  puts("GITREC TREECLOSURE C0 C1 TREE_OID40");
  return 4;
 }
 if((get||full||tree||commit||root||path_command||
     pathcat||pathfull||pathfullcat||
     lsdir||lsdirv||
     lsdirdepth||lsdirfull||
     firstpar||ancestor||history||
     parent_cmd||parents_cmd||roots_cmd||
     commitroots_cmd||linkroots_cmd||nestedlinks_cmd||
     deeplinks_cmd||depthlinks_cmd||linkbatch_cmd||
     closure_cmd||treeclosure_cmd)&&
    (strlen(argv[4])!=40||
    !idx_hex(argv[4],oid))) {
  puts("GET REQUIRES 40 HEX DIGITS");
  return 4;
 }
 if(ancestor||history||parent_cmd) {
  if(!argv[5][0]||strlen(argv[5])>2) {
   puts("ANCESTOR DEPTH MUST BE 1 THROUGH 16");return 4;
  }
  d=0;
  for(rc=0;argv[5][rc];rc++) {
   if(argv[5][rc]<'0'||argv[5][rc]>'9') {
    puts("ANCESTOR DEPTH MUST BE 1 THROUGH 16");return 4;
   }
   d=d*10+(unsigned long)(argv[5][rc]-'0');
  }
  if(d<1||d>16) {
   puts("ANCESTOR DEPTH MUST BE 1 THROUGH 16");return 4;
  }
  depth=(unsigned int)d;
 }
 if(depthlinks_cmd) {
  if(strlen(argv[5])!=1||
     argv[5][0]<'0'||argv[5][0]>'4') {
   puts("LINK DEPTH MUST BE 0 THROUGH 4");return 4;
  }
  depth=(unsigned int)(argv[5][0]-'0');
 }
 if(lsdirdepth) {
  if(strlen(argv[6])!=1||
     argv[6][0]<'0'||argv[6][0]>'4') {
   puts("DIRECTORY DEPTH MUST BE 0 THROUGH 4");
   return 4;
  }
  dir_depth=(unsigned int)(argv[6][0]-'0');
 }
 if((path_command||pathcat||pathfull||pathfullcat||
     lsdir||lsdirv||
     lsdirdepth||lsdirfull)&&
    !rec_path_hex(argv[5],path,&pathlen)) {
  puts("PATH REQUIRES VALID NONEMPTY HEX");return 4;
 }
 rec_expected[0]=argv[2];rec_expected[1]=argv[3];
 slot_read("dd:SEL0",&a);
 slot_read("dd:SEL1",&b);
 if(a.valid&&strcmp(a.gen,argv[2])!=0) {
  puts("SELECTOR SLOT 0 NAME MISMATCH");a.valid=0;
 }
 if(b.valid&&strcmp(b.gen,argv[3])!=0) {
  puts("SELECTOR SLOT 1 NAME MISMATCH");b.valid=0;
 }
 rc=selector_choose(&a,&b);
 if(rc!=0||(!get&&!full&&!tree&&!commit&&!root&&
             !path_command&&!pathcat&&!pathfull&&
             !pathfullcat&&
             !lsdir&&!lsdirv&&
             !lsdirdepth&&!lsdirfull&&
             !firstpar&&!ancestor&&!history&&
             !parent_cmd&&!parents_cmd&&!roots_cmd&&
             !commitroots_cmd&&!linkroots_cmd&&
             !nestedlinks_cmd&&!deeplinks_cmd&&
             !depthlinks_cmd&&!linkbatch_cmd&&
             !closure_cmd&&!treeclosure_cmd)) return rc;
 /* rec_active is set ONLY by the successful full-GEN2 callback. */
 if(tree) return rec_tree(oid);
 if(commit) return rec_commit(oid);
 if(root) return rec_root(oid);
 if(path_command) return rec_path(oid,path,pathlen,0,0);
 if(pathcat) return rec_path(oid,path,pathlen,1,0);
 if(pathfull) return rec_path(oid,path,pathlen,6,0);
 if(pathfullcat) return rec_path(oid,path,pathlen,7,0);
 if(lsdir) return rec_path(oid,path,pathlen,2,0);
 if(lsdirv) return rec_path(oid,path,pathlen,3,0);
 if(lsdirfull) return rec_path(oid,path,pathlen,5,0);
 if(lsdirdepth)
  return rec_path(oid,path,pathlen,4,dir_depth);
 if(firstpar) return rec_firstpar(oid);
 if(ancestor) return rec_ancestor(oid,depth);
 if(history) return rec_history(oid,depth);
 if(parent_cmd) return rec_parent(oid,depth);
 if(parents_cmd) return rec_parents(oid,0,0,0,0,0);
 if(roots_cmd) return rec_parents(oid,1,0,0,0,0);
 if(commitroots_cmd) return rec_parents(oid,1,1,0,0,0);
 if(linkroots_cmd) return rec_parents(oid,1,1,1,0,0);
 if(nestedlinks_cmd) return rec_parents(oid,1,1,1,1,0);
 if(deeplinks_cmd) return rec_parents(oid,1,1,1,2,0);
 if(depthlinks_cmd) return rec_parents(oid,1,1,1,depth,1);
 if(linkbatch_cmd) return rec_parents(oid,1,1,1,2,2);
 if(closure_cmd) return rec_parents(oid,1,1,2,0,0);
 if(treeclosure_cmd) return rec_tree_closure(oid);
 if(sidx_read()!=0) return 8;
 sidx_emit_full=full;
 return sidx_get(oid);
}
