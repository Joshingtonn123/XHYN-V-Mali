#!/usr/bin/env python3
"""Reuse the user's existing XHYN V icon and violet palette, without editing artwork."""
from pathlib import Path
import re,json,shutil,xml.etree.ElementTree as ET,hashlib
R=Path(__file__).resolve().parents[1];D=R/'decoded';OLD=R.parent/'recovered/branding/decoded';assets=R/'branding'
assets.mkdir(exist_ok=True)
colors={0x68dfae:0xb79aff,0x161a1c:0x100b1d,0x202628:0x21162f,0x232b2b:0x21162f}
def color(value):
    u=value&0xffffffff;return (u&0xff000000)|colors.get(u&0xffffff,u&0xffffff)
counts={};n=0
for p in (D/'smali/com/gtavsource/android').rglob('*.smali'):
    t=p.read_text()
    # Only original UI classes; never rewrite numerical constants in native/
    # gameplay protocols, nor edit saved user-selected colors.
    if not p.name.startswith(('MenuStyle','GameMenuActivity','TrainerOverlay','ControlCollectionEditor','LayoutEditor','DriverPicker','StoragePermissionActivity')):continue
    def replace(m):
        global n
        original=int(m[0],16);new=color(original)
        if new==(original&0xffffffff):return m[0]
        n+=1;return '-0x'+format((1<<32)-new,'x') if new&0x80000000 else '0x'+format(new,'x')
    t=re.sub(r'(?<![\w])-?0x[0-9a-f]+\b',replace,t)
    # Visible main-menu name only; GTA V game filenames/data and JNI stay intact.
    if p.name=='GameMenuActivity.smali':t=t.replace('const-string v12, "GTA V"','const-string v12, "XHYN V"').replace('"GTA V \\u00b7 Android"','"XHYN V \\u00b7 Android"')
    p.write_text(t)
for p in (D/'res').rglob('*.xml'):
    t=p.read_text()
    for a,b in colors.items():t=re.sub(r'(?i)(#[0-9a-f]{2})'+format(a,'06x'),lambda m:m[1]+format(b,'06x'),t)
    p.write_text(t)
for p in (R/'java/com/gtavsource/android').glob('Reborn*.java'):
    t=p.read_text().replace('XHYN V Reborn','XHYN V');p.write_text(t)
android='{http://schemas.android.com/apk/res/android}';ET.register_namespace('android',android[1:-1]);tree=ET.parse(D/'AndroidManifest.xml');tree.getroot().find('application').set(android+'label','XHYN V');tree.write(D/'AndroidManifest.xml',encoding='utf-8',xml_declaration=True)
copied=[]
for p in (OLD/'res').rglob('*.png'):
    if p.name not in ['ic_launcher.png','ic_launcher_foreground.png','ui_logo.png']:continue
    rel=p.relative_to(OLD/'res');target=D/'res'/rel;assert target.exists(),target
    saved=assets/rel;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,saved);shutil.copyfile(p,target)
    copied.append({'resource':str(rel),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
assert len(copied)==11,len(copied)
ini=D/'assets/default-android.ini';ini.write_text(ini.read_text().replace('#8068dfae','#80b79aff'))
report={'name':'XHYN V','accent':'#b79aff','background':'#100b1d','panel':'#21162f','smali_color_replacements':n,'copied_original_icon_resources':copied,'source_library_file':'libfile_695cd46ad7488191ab2a1ad10d84cfe5'}
(R/'reports/branding.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'name':report['name'],'palette':colors,'resources':len(copied),'color_changes':n}))
