from pathlib import Path
import struct,json,zipfile,subprocess,shutil
import pyflp,numpy as np,soundfile as sf
from pyflp._events import EventEnum,_EventEnumMeta
original=_EventEnumMeta.__call__
def compat(cls,value,*args,**kw):return cls._missing_(value) if cls is EventEnum else original(cls,value,*args,**kw)
_EventEnumMeta.__call__=compat
root=Path(__file__).resolve().parent/'NIGHT GRAVE - DROP STUDY'
flp=root/'NIGHT GRAVE - DROP STUDY.flp';p=pyflp.parse(flp)
ar=next(iter(p.arrangements));clips=[i for t in ar.tracks for i in t]
assert len(p.channels)==16 and len(clips)==38
assert max(c.position+c.length for c in clips)==16*384
assert p.tempo==144 and p.events.first(9).value
assert all(c.sample_path.exists() for c in p.channels)
fx=[dict(insert=i.iid+1,track=i.name,plugin=s.internal_name,mix=s._kw['params'][1]['msg']/12800) for i in p.mixer for s in i if s.plugin and s.internal_name=='Fruity Reeverb 2']
assert len(fx)==4
native=root/'FL Render/NIGHT GRAVE - DROP STUDY.wav'
a,sr=sf.read(native,always_2d=True)
assert 26<len(a)/sr<36 and np.max(np.abs(a))>.1 and np.all(np.isfinite(a))
report=dict(fl_studio='24.2.2.4597',bpm=144,seconds=len(a)/sr,peak_dbfs=float(20*np.log10(np.max(np.abs(a)))),rms_dbfs=float(20*np.log10(np.sqrt(np.mean(a*a)))),effects=fx,clips=len(clips),notes=sum(len(list(q.notes)) for q in p.patterns))
(root/'validation.json').write_text(json.dumps(report,indent=2))
shutil.copy2(native,root/'NIGHT GRAVE - DROP STUDY.wav')
subprocess.run(['ffmpeg','-v','error','-i',str(native),'-codec:a','libmp3lame','-b:a','256k','-y',str(root/'NIGHT GRAVE - DROP STUDY.mp3')],check=True)
readme='''NIGHT GRAVE - DROP STUDY
16-bar replacement drop, 144 BPM. Original kick/bass pocket, half-time
clap, sparse D-F-Eb lead cell, pitched bass and matching pedal harmony.
No vocal playback. Four phrases introduce rests and alternate endings.
This is a listening study, not a completed full-song revision.
Open the FLP with the sample WAVs beside it, or open the complete ZIP.
Audio exported in the installed FL Studio. Sound design uses V3 assets.
'''
(root/'README.txt').write_text(readme,encoding='utf-8')
data=flp.read_bytes();pos=data.index(b'FLdt')+8;ev=[]
def encode(id,payload):
 out=bytes([id])
 if id>=192:
  n=len(payload)
  while n>=128:out+=bytes([(n&127)|128]);n>>=7
  out+=bytes([n])
 return out+payload
while pos<len(data):
 id=data[pos];pos+=1
 if id<192:n=1 if id<64 else 2 if id<128 else 4
 else:
  n=0;shift=0
  while True:
   b=data[pos];pos+=1;n|=(b&127)<<shift;shift+=7
   if b<128:break
 payload=data[pos:pos+n];pos+=n
 if id==196:payload=(Path(payload.decode('utf-16le').rstrip('\0')).name+'\0').encode('utf-16le')
 ev.append(encode(id,payload))
encoded=b''.join(ev);portable=data[:14]+b'FLdt'+struct.pack('<I',len(encoded))+encoded
with zipfile.ZipFile(root/'NIGHT GRAVE - DROP STUDY - complete project.zip','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('NIGHT GRAVE - DROP STUDY.flp',portable)
 for f in (root/'Samples').glob('*.wav'):z.write(f,f.name)
 for name in ['README.txt','production.json','validation.json','NIGHT GRAVE - DROP STUDY.mp3']:z.write(root/name,name)
with zipfile.ZipFile(root/'NIGHT GRAVE - DROP STUDY - complete project.zip') as z:assert z.testzip() is None
print(json.dumps(report,indent=2))

dest=Path(__file__).resolve().parent/'projects/NIGHT GRAVE - DROP STUDY'
dest.mkdir(parents=True,exist_ok=True)
(dest/'NIGHT GRAVE - DROP STUDY.flp').write_bytes(portable)
for f in (root/'Samples').glob('*.wav'):shutil.copy2(f,dest/f.name)
for name in ['README.txt','production.json','validation.json','NIGHT GRAVE - DROP STUDY.mp3','NIGHT GRAVE - DROP STUDY.wav']:shutil.copy2(root/name,dest/name)
shutil.copy2(root/'NIGHT GRAVE - DROP STUDY - complete project.zip',Path(__file__).resolve().parent/'downloads/NIGHT GRAVE - DROP STUDY - complete project.zip')
