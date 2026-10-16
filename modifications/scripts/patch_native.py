#!/usr/bin/env python3
"""Exact-build language repair. Renderer and threading code are untouched."""
from pathlib import Path
import hashlib, io, json, struct
from elftools.elf.elffile import ELFFile

ROOT=Path(__file__).resolve().parents[1]
EXPECTED='b0464aa55843ebab78cb9993ec89146c08c29145c58a62f9197f2348248149f5'
GATE=0xe256b4
FONT=GATE+0x100
ARCHIVE=GATE+0x120

def offset(elf,a,n):
    for s in elf.iter_segments():
        if s['p_type']=='PT_LOAD' and s['p_vaddr']<=a and a+n<=s['p_vaddr']+s['p_filesz']:
            return s['p_offset']+a-s['p_vaddr']
    raise ValueError(hex(a))

def pair(pc,target,r):
    imm=(((target&~4095)-(pc&~4095))>>12)&0x1fffff
    return struct.pack('<II',0x90000000|((imm&3)<<29)|((imm>>2)<<5)|r,
                       0x91000000|((target&4095)<<10)|(r<<5)|r)

def patch(source):
    assert hashlib.sha256(source).hexdigest()==EXPECTED,'Unexpected engine; do not reuse these offsets on another build'
    elf=ELFFile(io.BytesIO(source));out=bytearray(source);edits=[]
    text=elf.get_section_by_name('.text');lo=text['sh_addr'];hi=lo+text['sh_size']
    calls=[];inside=[]
    text_offset=text['sh_offset']
    for a in range(lo,hi,4):
        w=struct.unpack_from('<I',source,text_offset+a-lo)[0]
        if w&0x7c000000==0x14000000:
            imm=w&0x3ffffff
            if imm&0x2000000:imm-=0x4000000
            target=a+imm*4
            if GATE<=target<GATE+0x400 and not GATE<=a<GATE+0x400:
                inside.append((a,target,w))
                if target==GATE and w&0xfc000000==0x94000000:calls.append(a)
    assert len(calls)==2 and len(inside)==2,(calls,inside)
    assert source[offset(elf,GATE,8):offset(elf,GATE,8)+8]==bytes.fromhex('ffc302d1fd7b08a9')
    for s in elf.iter_sections():
        if s['sh_type']=='SHT_RELA':
            for rel in s.iter_relocations():
                assert not GATE<=rel['r_addend']<GATE+0x400
                assert not FONT<=rel['r_offset']<ARCHIVE+16
    def replace(name,a,before,after):
        assert len(before)==len(after)
        o=offset(elf,a,len(before));assert source[o:o+len(before)]==before,name
        out[o:o+len(after)]=after
        edits.append(dict(name=name,address=hex(a),offset=o,before=before.hex(),after=after.hex()))
    for a in calls:
        o=offset(elf,a,4)
        replace('Accept device language at startup/resume call',a,source[o:o+4],bytes.fromhex('20008052'))
    replace('Default text formatting: non-Asian',0x2163a3c,bytes.fromhex('20008052'),bytes.fromhex('00008052'))
    for a in [0x2163a44,0x2163a58]:replace('Default game language: English',a,bytes.fromhex('a0018052'),bytes.fromhex('20008052'))
    replace('Default supported language: English',0x2163a90,bytes.fromhex('1f340071'),bytes.fromhex('1f040071'))
    # Both callers were removed above. Store separate font/archive names in the
    # now-unreachable gate body, leaving all function boundaries and FDEs intact.
    for a,value in [(FONT,b'efigs'),(ARCHIVE,b'american')]:
        o=offset(elf,a,16);replace('Dedicated language resource storage',a,source[o:o+16],value.ljust(16,b'\0'))
    pointers=[(0x2163a9c,FONT,0),(0x2163aa8,FONT,0),(0x2163aec,FONT,2)]
    pointers += [(a,ARCHIVE,3) for a in [0x21651b4,0x2165214,0x2165234,0x21665b8,0x21665fc,0x216663c]]
    for a,target,r in pointers:
        o=offset(elf,a,8);replace('Language resource pointer',a,source[o:o+8],pair(a,target,r))
    assert len(out)==len(source)
    audit=dict(source_sha256=EXPECTED,patched_sha256=hashlib.sha256(out).hexdigest(),
               edits=edits,locale_calls=[hex(a) for a in calls],renderer_changed=False,
               original_unwind_sections_unchanged=True,font_storage=hex(FONT),archive_storage=hex(ARCHIVE))
    return bytes(out),audit

if __name__=='__main__':
    import argparse,zipfile
    parser=argparse.ArgumentParser();parser.add_argument('--input-apk',type=Path);args=parser.parse_args()
    p=ROOT/'decoded/lib/arm64-v8a/libgtav.so'
    if args.input_apk:
        with zipfile.ZipFile(args.input_apk) as z:source=z.read('lib/arm64-v8a/libgtav.so')
    else:source=p.read_bytes()
    result,audit=patch(source);p.write_bytes(result)
    (ROOT/'reports/native-language-patch.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps({k:v for k,v in audit.items() if k!='edits'},indent=2))
