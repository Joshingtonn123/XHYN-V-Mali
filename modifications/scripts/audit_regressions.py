#!/usr/bin/env python3
from pathlib import Path
import re,json,zipfile,collections,hashlib,struct,importlib.util
R=Path(__file__).resolve().parents[1];D=R/'decoded';changes=collections.Counter()
def compare(a,b,path):
    assert type(a)==type(b),path
    if isinstance(a,dict):
        assert a.keys()==b.keys(),path
        for k in a:compare(a[k],b[k],path+[k])
    elif isinstance(a,list):
        assert len(a)==len(b),path
        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+[i])
    elif a!=b:
        assert isinstance(a,str) and isinstance(b,str),path
        assert path[-1] in ['name','label','message','origin'] or 'viewports' in path,path
        assert not re.search('[\u3400-\u9fff]',b),path
        if path[-1]=='label':assert 0<len(b)<=24,(path,b)
        changes[str(path[-1])]+=1
with zipfile.ZipFile(R.parent/'upload/dxvk功能优化-启动器.apk') as z:
    for name in z.namelist():
        if name.startswith('assets/touch-layouts/') and name.endswith('.json'):compare(json.loads(z.read(name)),json.loads((D/name).read_text()),[name])
    def ini(t):
        out={};section=''
        for line in t.splitlines():
            line=line.strip()
            if line.startswith('['):section=line
            elif line and not line.startswith(('#',';')):k,v=line.split('=',1);out[(section,k.strip())]=v.strip()
        return out
    before=ini(z.read('assets/default-android.ini').decode());after=ini((D/'assets/default-android.ini').read_text());diff={str(k):(before.get(k),after.get(k)) for k in before.keys()|after.keys() if before.get(k)!=after.get(k)}
    assert diff=={"('[overlay]', 'border_color')":('#8068dfae','#80b79aff')},diff
    native={}
    for n in z.namelist():
        if n.startswith('lib/') and n.endswith('.so') and not n.endswith('/libgtav.so'):
            assert z.read(n)==(D/n).read_bytes(),n;native[n]=hashlib.sha256(z.read(n)).hexdigest()
with zipfile.ZipFile(R.parent/'recovered/branding/XHYN-V-r30-Hotfix2-unsigned.apk') as z:
    icon_count=0
    for n in z.namelist():
        if n.endswith('.png') and any(n.endswith('/'+s) for s in ['ui_logo.png','ic_launcher.png','ic_launcher_foreground.png']):
            decoded=n.replace('-v4/','/');assert z.read(n)==(D/decoded).read_bytes(),n;icon_count+=1
    assert icon_count==11
# Preserve the base's language-independent settings and unknown translation keys.
assert 'android:label="XHYN V"' in (D/'AndroidManifest.xml').read_text()
assert not list((D/'smali').rglob('RuntimeAudit*.smali'))
assert not list((D/'lib').rglob('libc.so')) and not list((D/'lib').rglob('libdl.so'))
for needle in ['init','isFailure']:
    assert 'RebornDiagnostics;->'+needle in (D/'smali/com/gtavsource/android/GameDiagnostics.smali').read_text()
assert 'Thread;->join()V' not in (D/'smali/org/libsdl/app/SDLActivity.smali').read_text()
assert 'RebornSession;->mainResult(I)V' in (D/'smali/org/libsdl/app/SDLMain.smali').read_text()
# Real frame format from the provided source has an ARRAY of classification tags.
spec=importlib.util.spec_from_file_location('analyzer',R/'scripts/analyze_performance.py');analyzer=importlib.util.module_from_spec(spec);spec.loader.exec_module(analyzer)
temp=R/'build/performance-fixture';temp.mkdir(parents=True,exist_ok=True)
rows=[dict(type='frame',frame=i,monotonic_ns=i*10000000,frame_ms=100 if i==100 else 10,classification=['GPU_BOUND']) for i in range(1,101)]
a=temp/'native.jsonl';a.write_text('\n'.join(map(json.dumps,rows))+'\n'+json.dumps(dict(type='frame',frame=101,frame_ms=-1))+'\n{"truncated":')
b=temp/'overlap.jsonl';b.write_text('\n'.join(map(json.dumps,rows[:3])))
summary=analyzer.summarize([a,b]);assert summary['sample_frames']==100 and summary['frame_ms_p50']==10 and summary['one_percent_low_fps']==10 and summary['classification_counts']['GPU_BOUND']==100
not_frames=temp/'session.jsonl';not_frames.write_text(json.dumps({'event':'sample','frames_per_second_over_interval':60})+'\n')
try:analyzer.summarize([not_frames]);raise AssertionError('UI/session average accepted as a frame-time sample')
except ValueError:pass
result={'result':'PASS','layout_display_changes':dict(changes),'layout_ids_commands_geometry_and_schema_unchanged':True,'default_ini_changes':diff,'original_native_libraries_preserved':native,'original_brand_icon_resources':icon_count,'frame_analysis_fixture':summary,'limits':'Static/source checks and synthetic host fixtures; no device UI or gameplay validation'}
(R/'reports/regressions.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['original_native_libraries_preserved','frame_analysis_fixture']},indent=2))
