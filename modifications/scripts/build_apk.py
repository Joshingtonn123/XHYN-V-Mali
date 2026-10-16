#!/usr/bin/env python3
"""Build and sign the current decoded local workspace, never a Git checkout."""
from pathlib import Path
import subprocess,json,hashlib,struct,zipfile,secrets,os
R=Path(__file__).resolve().parents[1];D=R/'decoded';OUT=R/'dist';OUT.mkdir(exist_ok=True)
SDK=R.parent/'recovered/hotfix2/extracted/XHYN-V-r30-Hotfix2/toolchain/android-ui'
sign=R/'signing';sign.mkdir(exist_ok=True);os.chmod(sign,0o700);key=sign/'xhyn-v-reborn.p12';password=sign/'password.txt'
if not key.exists():
    password.write_text(secrets.token_urlsafe(40)+'\n');os.chmod(password,0o600)
    subprocess.run(['java','sun.security.tools.keytool.Main','-genkeypair','-keystore',str(key),'-storetype','PKCS12','-storepass:file',str(password),'-keypass:file',str(password),'-alias','xhyn-v-reborn','-keyalg','RSA','-keysize','3072','-validity','10000','-dname','CN=XHYN V, O=XHYN PH, C=PH'],check=True);os.chmod(key,0o600)
fingerprints={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((D/'lib/arm64-v8a').glob('*.so'))}
(D/'assets/reborn-binary-fingerprints.json').write_text(json.dumps(fingerprints,sort_keys=True,indent=2)+'\n')
unsigned=OUT/'XHYN-V-0.1-unsigned.apk';final=OUT/'XHYN-V-0.1.apk'
subprocess.run(['java','-jar',str(R.parent/'tools/apktool.jar'),'b',str(D),'-o',str(unsigned)],check=True)
# Let the Android signer write its own valid alignment extra fields before
# calculating the signature; manually padding them can be shifted by signing.
subprocess.run(['java','-jar',str(SDK/'apksigner.jar'),'sign','--ks',str(key),'--ks-key-alias','xhyn-v-reborn','--ks-pass','file:'+str(password),'--v4-signing-enabled','false','--alignment-preserved','false','--lib-page-alignment','16384','--out',str(final),str(unsigned)],check=True)
v=subprocess.run(['java','-jar',str(SDK/'apksigner.jar'),'verify','--verbose','--print-certs',str(final)],check=True,text=True,capture_output=True);(R/'reports/signature-verification.txt').write_text(v.stdout+v.stderr)
print(v.stdout)
with zipfile.ZipFile(final) as z,final.open('rb') as stream:
    assert z.testzip() is None
    for i in z.infolist():
        if i.compress_type!=zipfile.ZIP_STORED:continue
        stream.seek(i.header_offset);h=stream.read(30);nl,el=struct.unpack_from('<HH',h,26);off=i.header_offset+30+nl+el;alignment=16384 if i.filename.startswith('lib/') and i.filename.endswith('.so') else 4
        assert off%alignment==0,(i.filename,off)
    assert z.read('classes.dex').startswith(b'dex\n')
    for name,digest in fingerprints.items():assert hashlib.sha256(z.read('lib/arm64-v8a/'+name)).hexdigest()==digest
    assert 'lib/arm64-v8a/libc.so' not in z.namelist() and 'lib/arm64-v8a/libdl.so' not in z.namelist()
result={'file':final.name,'bytes':final.stat().st_size,'sha256':hashlib.sha256(final.read_bytes()).hexdigest(),'signature_verified':True,'stored_native_libraries_aligned_to':16384,'native_fingerprints':fingerprints,'device_gameplay_tested':False}
(R/'reports/apk-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='native_fingerprints'},indent=2))
