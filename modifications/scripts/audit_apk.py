#!/usr/bin/env python3
"""Inspect the final APK's manifest, retained classes and new helper references."""
from pathlib import Path
import json, zipfile, hashlib
from loguru import logger
logger.remove()
from androguard.core.apk import APK
from androguard.core.dex import DEX

R=Path(__file__).resolve().parents[1]
p=R/'dist/XHYN-V-0.1.apk'
a=APK(str(p))
assert (a.get_package(),a.get_androidversion_name(),a.get_androidversion_code(),a.get_app_name())==('com.xhynph.xhynv.reborn','0.1','1','XHYN V')
assert list(a.get_dex_names())==['classes.dex']
d=DEX(a.get_dex()); classes=d.get_classes(); names=[c.get_name() for c in classes]
assert len(names)==len(set(names)), 'Duplicate DEX classes'
by_name={c.get_name():c for c in classes}
original=APK(str(R.parent/'upload/dxvk功能优化-启动器.apk'))
base=DEX(original.get_dex());base_names={c.get_name() for c in base.get_classes()}
assert base_names<=set(names), 'Original classes were removed'
added=set(names)-base_names
assert all(n.startswith('Lcom/gtavsource/android/Reborn') or n in {
 'Lcom/gtavsource/android/XhynTrainerText;', 'Lcom/gtavsource/android/XhynLabels;',
 'Lcom/gtavsource/android/XhynVulkanFiles;'} for n in added), sorted(added)
assert sum(n.startswith('Lcom/gtavsource/android/Reborn') for n in added)==38

def descriptor(x):return x.replace(' ','')
methods={(c.get_name(),m.get_name(),descriptor(m.get_descriptor())) for c in classes for m in c.get_methods()}
fields={(c.get_name(),f.get_name(),f.get_descriptor()) for c in classes for f in c.get_fields()}
def resolves(owner,name,kind,defs):
 seen=set()
 while owner in by_name and owner not in seen:
  if (owner,name,kind) in defs:return True
  seen.add(owner);owner=by_name[owner].get_superclassname()
 # An inherited Android/JDK member is outside this DEX; this is not a host
 # replacement for Android's verifier.
 return owner not in by_name and not owner.startswith('Lcom/gtavsource/android/')

helper_method_refs=0; app_outgoing_refs=0
for ref in d.get_methods():
 owner=ref.get_class_name()
 if owner.startswith('Lcom/gtavsource/android/Reborn'):
  assert (owner,ref.get_name(),descriptor(ref.get_descriptor())) in methods,(owner,ref.get_name(),ref.get_descriptor())
  helper_method_refs+=1
for c in classes:
 if not c.get_name().startswith('Lcom/gtavsource/android/Reborn'):continue
 for m in c.get_methods():
  for ins in m.get_instructions():
   if not ins.get_name().startswith('invoke-'):continue
   index=ins.get_operands()[-1][1];ref=d.get_methods()[index];owner=ref.get_class_name()
   if owner.startswith('Lcom/gtavsource/android/'):
    assert resolves(owner,ref.get_name(),descriptor(ref.get_descriptor()),methods),(c.get_name(),owner,ref.get_name(),ref.get_descriptor())
    app_outgoing_refs+=1
for ref in d.get_fields():
 if ref.get_class_name().startswith('Lcom/gtavsource/android/Reborn'):
  assert (ref.get_class_name(),ref.get_name(),ref.get_type()) in fields

for name in ['RuntimeConfig','GTAVActivity','GameTelemetry','MenuDialogBuilder']:
 n='Lcom/gtavsource/android/'+name+';'
 before={m.get_name()+descriptor(m.get_descriptor()) for m in base.get_class(n).get_methods()}
 after={m.get_name()+descriptor(m.get_descriptor()) for m in by_name[n].get_methods()}
 assert before<=after, 'Compile-only stub replaced '+name
for name in [a.get_main_activity(),*a.get_activities()]:
 assert 'L'+name.replace('.','/')+';' in by_name,name
with zipfile.ZipFile(p) as z:
 fingerprints=json.loads(z.read('assets/reborn-binary-fingerprints.json'))
 for name,digest in fingerprints.items():assert hashlib.sha256(z.read('lib/arm64-v8a/'+name)).hexdigest()==digest
 assert not any('/test/' in n or '/stubs/' in n for n in z.namelist())
report={'result':'PASS','package':a.get_package(),'version_name':a.get_androidversion_name(),'version_code':a.get_androidversion_code(),'app_label':a.get_app_name(),'min_sdk':a.get_min_sdk_version(),'target_sdk':a.get_target_sdk_version(),'dex_classes':len(names),'new_reborn_helpers':38,'all_original_classes_retained':True,'helper_method_references_resolved':helper_method_refs,'helper_outgoing_app_references_checked':app_outgoing_refs,'original_stub_target_methods_retained':True,'packaged_native_fingerprints_match':True,'scope':'Static APK/DEX inspection; Android runtime verifier, device UI and gameplay remain untested'}
(R/'reports/apk-classes.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
