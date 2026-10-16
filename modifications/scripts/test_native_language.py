#!/usr/bin/env python3
"""Execute the built ARM64 language bridge and game getters with Unicorn.
This checks real generated instructions; it is not an Android gameplay test.
"""
from pathlib import Path
import io,json,struct,hashlib,zipfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE,UC_PROT_ALL
from unicorn.arm64_const import *
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_ARM
R=Path(__file__).resolve().parents[1]
E=0x10000000;H=0x20000000;STACK=0x30000000;STUB=0x40000000;END=STUB+0x10000
engine=(R/'decoded/lib/arm64-v8a/libgtav.so').read_bytes();helper=(R/'decoded/lib/arm64-v8a/libxhyn_locale.so').read_bytes()
elf=ELFFile(io.BytesIO(engine));he=ELFFile(io.BytesIO(helper));cs=Cs(CS_ARCH_ARM64,CS_MODE_ARM)
symbols={s.name:s['st_value'] for s in he.get_section_by_name('.symtab').iter_symbols()}
ARCHIVES=['chinese','american','french','german','italian','japanese','korean','polish','portuguese','portuguese','russian','spanish','mexican','chinesesimp']
FONTS=['chinese','efigs','efigs','efigs','efigs','japanese','korean','efigs','efigs','efigs','efigs','efigs','efigs','chinesesimp']
def source(a,n):
 for seg in elf.iter_segments():
  if seg['p_type']=='PT_LOAD' and seg['p_vaddr']<=a and a+n<=seg['p_vaddr']+seg['p_filesz']:
   o=seg['p_offset']+a-seg['p_vaddr'];return engine[o:o+n]
 raise ValueError(hex(a))
def signed(v):return v-(1<<32) if v&(1<<31) else v
def text(u,a):return bytes(u.mem_read(a,32)).split(b'\0',1)[0].decode()
class Machine:
 def __init__(self,page=4096,fail=()):
  self.u=u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);self.calls=[];self.page=page;self.fail=set(fail);self.external={}
  u.mem_map(H,0x20000);u.mem_map(STACK,0x20000);u.mem_map(STUB,0x20000)
  for seg in he.iter_segments():
   if seg['p_type']=='PT_LOAD':u.mem_write(H+seg['p_vaddr'],seg.data())
  for seg in [0xe24000,0x2160000,0x2164000]:
   u.mem_map(E+seg,0x4000)
   for load in elf.iter_segments():
    if load['p_type']!='PT_LOAD':continue
    low=max(seg,load['p_vaddr']);high=min(seg+0x4000,load['p_vaddr']+load['p_filesz'])
    if low<high:u.mem_write(E+low,source(low,high-low))
  dy=he.get_section_by_name('.dynsym')
  for sec in he.iter_sections():
   if sec['sh_type']!='SHT_RELA':continue
   for rel in sec.iter_relocations():
    if rel['r_info_type']==1027:value=H+rel['r_addend']
    else:
     name=dy.get_symbol(rel['r_info_sym']).name;value=STUB+len(self.external)*0x100
     self.external[value]=name
    u.mem_write(H+rel['r_offset'],struct.pack('<Q',value))
  u.mem_write(H+symbols['engine'],struct.pack('<Q',E))
  u.hook_add(UC_HOOK_CODE,self.hook)
 def hook(self,u,a,size,_):
  if a in self.external:
   name=self.external[a]
   if name=='getpagesize':result=self.page
   elif name=='mprotect':
    start=u.reg_read(UC_ARM64_REG_X0);length=u.reg_read(UC_ARM64_REG_X1);prot=u.reg_read(UC_ARM64_REG_X2);self.calls.append((start,length,prot))
    assert prot in (3,5),'RWX was requested';result=-1 if len(self.calls) in self.fail else 0
    if result==0:u.mem_protect(start,length,prot)
   elif name=='dl_iterate_phdr':raise AssertionError('Unexpected dl_iterate_phdr; callback is tested separately')
   else:raise AssertionError(name)
   u.reg_write(UC_ARM64_REG_X0,result&0xffffffffffffffff);u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR));return
  word=bytes(u.mem_read(a,4));ins=next(cs.disasm(word,a),None)
  # Cache instructions are examined but not physically simulated. CTR is an
  # ordinary 64-byte cache-line layout; coherence still needs a real device.
  if ins and ins.mnemonic=='mrs' and 'ctr_el0' in ins.op_str:
   reg=int(ins.op_str.split(',')[0].strip()[1:]);u.reg_write(UC_ARM64_REG_X0+reg,0x8444c004);u.reg_write(UC_ARM64_REG_PC,a+4)
  elif ins and ins.mnemonic in ['dc','ic','dsb','isb']:u.reg_write(UC_ARM64_REG_PC,a+4)
 def call(self,a,args=()):
  for i,arg in enumerate(args):self.u.reg_write(UC_ARM64_REG_X0+i,arg&0xffffffffffffffff)
  self.u.reg_write(UC_ARM64_REG_SP,STACK+0x18000);self.u.reg_write(UC_ARM64_REG_LR,END);self.u.emu_start(a,END,count=100000)
  assert self.u.reg_read(UC_ARM64_REG_PC)==END,hex(self.u.reg_read(UC_ARM64_REG_PC))
  return self.u.reg_read(UC_ARM64_REG_W0)
 def configure(self,id):return signed(self.call(H+symbols['Java_com_gtavsource_android_RebornNative_configure'],[0,0,id]))
results=[]
for page in [4096,16384]:
 for id in range(14):
  m=Machine(page);u=m.u;assert m.configure(id)==0
  assert m.call(E+0x2163a44)==id
  assert m.call(E+0x2163a3c)==(id in [0,5,6,13])
  for getter in [0x2163a9c,0x2163aa8]:
   m.call(E+getter);assert text(u,u.reg_read(UC_ARM64_REG_X0))==FONTS[id]
  assert text(u,E+0xe257d4)==ARCHIVES[id]
  for a in [0x21651b4,0x2165214,0x2165234,0x21665b8,0x21665fc,0x216663c]:
   u.emu_start(E+a,E+a+8,count=2);assert text(u,u.reg_read(UC_ARM64_REG_X3))==ARCHIVES[id]
  assert m.call(E+0x2163a90,[id])==1
  assert m.call(E+0x2163a90,[(id+1)%14])==0
  count=len(m.calls);assert m.configure(id)==0 and len(m.calls)==count
  assert m.configure((id+1)%14)==-5 and len(m.calls)==count
  assert [p[2] for p in m.calls]==[3,3,5,5]
  results.append({'page_size':page,'rl_language_id':id,'archive':ARCHIVES[id],'font':FONTS[id],'result':'PASS'})
for bad in [-1,14,99]:
 m=Machine();assert m.configure(bad)==0 and m.call(E+0x2163a44)==1
for fail,expected in [([1],-4),([2],-4),([2,3],-6),([3],-6),([4],-6)]:
 m=Machine(fail=fail);assert m.configure(3)==expected
 if expected==-4:
  assert m.call(E+0x2163a44)==1 and text(m.u,E+0xe257b4)=='efigs'
m=Machine(page=123);assert m.configure(4)==-3 and not m.calls
m=Machine();m.u.mem_write(E+0x2163a44,b'\0'*4);assert m.configure(4)==-2 and not m.calls
# Check actual module-name matching callback with an Android-style path.
for filename,expected in [('/data/app/example/lib/arm64/libgtav.so',1),('/data/app/example/lib/arm64/notlibgtav.so',0)]:
 m=Machine();u=m.u;u.mem_write(H+symbols['engine'],b'\0'*8);u.mem_write(STACK+0x100,filename.encode()+b'\0');u.mem_write(STACK,struct.pack('<QQQH',E,STACK+0x100,0,0));assert m.call(H+symbols['find_engine'],[STACK,32,0])==expected
 assert struct.unpack('<Q',u.mem_read(H+symbols['engine'],8))[0]==(E if expected else 0)
with zipfile.ZipFile(R.parent/'upload/dxvk功能优化-启动器.apk') as z:original=z.read('lib/arm64-v8a/libgtav.so')
oe=ELFFile(io.BytesIO(original))
for name in ['.eh_frame','.eh_frame_hdr','.rela.dyn','.rela.plt','.dynamic']:assert oe.get_section_by_name(name).data()==elf.get_section_by_name(name).data(),name
needed=[t.needed for t in he.get_section_by_name('.dynamic').iter_tags() if t.entry.d_tag=='DT_NEEDED'];assert set(needed)=={'libc.so','libdl.so'}
out={'result':'PASS','language_matrix':results,'negative_and_reentrancy_checks':'PASS','unwind_and_dynamic_sections_unchanged':True,'helper_needed':needed,'scope':'ARM64 emulation and ELF checks; Android loading, cache coherence, actual game resources and gameplay remain untested'}
(R/'reports/native-language-tests.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='language_matrix'},indent=2))
