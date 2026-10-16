#!/usr/bin/env python3
from pathlib import Path
import subprocess,shutil
R=Path(__file__).resolve().parents[1]
TOOLS=R.parent/'recovered/hotfix2/extracted/XHYN-V-r30-Hotfix2/toolchain/android-ui'
BUILD=R/'build/helpers'
if BUILD.exists():shutil.rmtree(BUILD)
classes=BUILD/'classes';dex=BUILD/'dex';smali=BUILD/'smali'
classes.mkdir(parents=True);dex.mkdir()
sources=[str(p) for root in [R/'java',R/'stubs'] for p in root.rglob('*.java')]
subprocess.run(['java','com.sun.tools.javac.Main','--release','8','-encoding','UTF-8','-classpath',str(TOOLS/'android.jar'),'-d',str(classes)]+sources,check=True)
# Do not emit compile stubs into the DEX. Real classes come from the base APK.
real=[str(p) for p in classes.rglob('Reborn*.class')]
subprocess.run(['java','-cp',str(TOOLS/'r8.jar'),'com.android.tools.r8.D8','--min-api','30','--lib',str(TOOLS/'android.jar'),'--classpath',str(classes),'--output',str(dex)]+real,check=True)
subprocess.run(['java','-cp',str(TOOLS/'*'),'org.jf.baksmali.Main','disassemble',str(dex/'classes.dex'),'-o',str(smali)],check=True)
out=R/'decoded/smali'
for old in (out/'com/gtavsource/android').glob('Reborn*.smali'):old.unlink()
for p in smali.rglob('*.smali'):
    assert p.name.startswith('Reborn'),p
    destination=out/p.relative_to(smali);destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,destination)
print('Compiled and merged',len(list(smali.rglob('*.smali'))),'Reborn helper classes; no compile stubs packaged')
