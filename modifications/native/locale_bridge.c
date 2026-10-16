/* Language selection for the exact supplied DXVK engine, before SDL main starts.
 * No per-frame hooks. The build script pins and verifies every instruction site.
 * Android's real device locale is never changed.
 */
typedef unsigned long uptr;
typedef unsigned long usize;
typedef struct { unsigned int type, flags; uptr offset, vaddr, paddr, filesz, memsz, align; } Phdr;
typedef struct { uptr base; const char *name; const Phdr *phdr; unsigned short count; } PhdrInfo;
extern int dl_iterate_phdr(int (*)(PhdrInfo*, usize, void*), void*);
extern int mprotect(void*, usize, int);
extern int getpagesize(void);

static uptr engine;
static int selected = -1;
static int suffix(const char *s, const char *want) {
    usize n=0, m=0; if(!s) return 0;
    while(s[n]) ++n; while(want[m]) ++m;
    if(n<m) return 0;
    for(usize i=0;i<m;++i) if(s[n-m+i]!=want[i]) return 0;
    return n==m || s[n-m-1]=='/';
}
static int find_engine(PhdrInfo *p, usize n, void *unused) {
    (void)n;(void)unused;
    if(!suffix(p->name,"libgtav.so")) return 0;
    engine=p->base; return 1;
}
static void cache_sync(uptr start, uptr end) {
    uptr ctr; __asm__ volatile("mrs %0, ctr_el0":"=r"(ctr));
    uptr d=4UL<<((ctr>>16)&15), i=4UL<<(ctr&15);
    for(uptr p=start&~(d-1);p<end;p+=d) __asm__ volatile("dc cvau, %0"::"r"(p):"memory");
    __asm__ volatile("dsb ish":::"memory");
    for(uptr p=start&~(i-1);p<end;p+=i) __asm__ volatile("ic ivau, %0"::"r"(p):"memory");
    __asm__ volatile("dsb ish\nisb":::"memory");
}
static unsigned int mov_w0(int id) { return 0x52800000U|((unsigned int)id<<5); }
static unsigned int cmp_w0(int id) { return 0x7100001fU|((unsigned int)id<<10); }
static unsigned int word(uptr a) { return *(const unsigned int*)(engine+a); }
static void put_word(uptr a, unsigned int v) { *(unsigned int*)(engine+a)=v; }
static void string_at(uptr a,const char *s) {
    char *p=(char*)(engine+a);
    for(int i=0;i<16;++i) p[i]=0;
    for(int i=0;s[i]&&i<15;++i) p[i]=s[i];
}

/* IDs are rlScLanguage values, verified from this binary's code-name table.
 * They are NOT sysLanguage ordinals. */
static const char *archive[14]={"chinese","american","french","german","italian","japanese","korean","polish","portuguese","portuguese","russian","spanish","mexican","chinesesimp"};
static const char *font[14]={"chinese","efigs","efigs","efigs","efigs","japanese","korean","efigs","efigs","efigs","efigs","efigs","efigs","chinesesimp"};

/* Return values: 0 success, negative guard/protection error. Reconfiguration of
 * a running engine is refused; new language choices require a fresh process. */
__attribute__((visibility("default")))
int Java_com_gtavsource_android_RebornNative_configure(void *env,void *cls,int id) {
    (void)env;(void)cls;
    if(id<0||id>13) id=1;
    if(selected>=0) return selected==id?0:-5;
    if(!engine) dl_iterate_phdr(find_engine,(void*)0);
    if(!engine) return -1;
    if(word(0x2163a3c)!=mov_w0(0)||word(0x2163a44)!=mov_w0(1)||word(0x2163a58)!=mov_w0(1)||
       word(0x2163a90)!=cmp_w0(1)||word(0x2163a48)!=0xd65f03c0U) return -2;
    const uptr pages[2]={0xe257b4,0x2163a44};
    int size=getpagesize(); if(size<4096||(size&(size-1))) return -3;
    uptr start[2]; for(int i=0;i<2;++i) start[i]=(engine+pages[i])&~((uptr)size-1);
    /* RW while the game has not started, then restore RX. Never request RWX. */
    if(mprotect((void*)start[0],size,3)) return -4;
    if(mprotect((void*)start[1],size,3)) { return mprotect((void*)start[0],size,5)?-6:-4; }
    string_at(0xe257b4,font[id]);string_at(0xe257d4,archive[id]);
    put_word(0x2163a3c,mov_w0(id==0||id==5||id==6||id==13));
    put_word(0x2163a44,mov_w0(id));put_word(0x2163a58,mov_w0(id));put_word(0x2163a90,cmp_w0(id));
    cache_sync(start[0],start[0]+size);cache_sync(start[1],start[1]+size);
    int a=mprotect((void*)start[0],size,5), b=mprotect((void*)start[1],size,5);
    if(a||b) return -6;
    selected=id;return 0;
}
