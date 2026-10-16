#!/usr/bin/env python3
"""Cross-compile the small JNI helper, linking Android libc and libdl explicitly.
Temporary link-only stubs describe symbol dependencies, never ship in the APK.
"""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[1]
zig=R.parent/'tools/zig/ziglang/zig'
build=R/'build/native-link';build.mkdir(parents=True,exist_ok=True)
for name,source in [('libc','int mprotect(void*a,unsigned long n,int p){return 0;} int getpagesize(void){return 4096;}'),('libdl','int dl_iterate_phdr(void*a,void*b){return 0;}')]:
    f=build/(name+'.c');f.write_text(source)
    subprocess.run([str(zig),'cc','-target','aarch64-linux-android','-O2','-shared','-fPIC','-nostdlib','-fno-stack-protector',f'-Wl,-soname,{name}.so',str(f),'-o',str(build/(name+'.so'))],check=True)
subprocess.run([str(zig),'cc','-target','aarch64-linux-android','-O2','-shared','-fPIC','-nostdlib','-fno-stack-protector','-Wl,-z,defs','-Wl,-z,max-page-size=16384','-Wl,--build-id=sha1','-Wl,-soname,libxhyn_locale.so',str(R/'native/locale_bridge.c'),'-L'+str(build),'-Wl,--no-as-needed','-l:libc.so','-l:libdl.so','-o',str(R/'decoded/lib/arm64-v8a/libxhyn_locale.so')],check=True)
print('Built libxhyn_locale.so with explicit libc.so and libdl.so dependencies')
