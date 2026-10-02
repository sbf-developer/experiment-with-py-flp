from pathlib import Path
import struct,json,zipfile,subprocess,shutil
import pyflp,numpy as np,soundfile as sf
from pyflp._events import EventEnum,_EventEnumMeta
original=_EventEnumMeta.__call__
def compat(cls,value,*args,**kw):return cls._missing_(value) if cls is EventEnum else original(cls,value,*args,**kw)
_EventEnumMeta.__call__=compat
root=Path(__file__).resolve().parent/'NIGHT GRAVE V3'
flp=root/'NIGHT GRAVE V3.flp';p=pyflp.parse(flp)
ar=next(iter(p.arrangements));clips=[i for t in ar.tracks for i in t]
assert len(p.channels)==16 and len(clips)==221
assert max(c.position+c.length for c in clips)==88*384
assert p.tempo==144 and p.events.first(9).value
assert all(c.sample_path.exists() for c in p.channels)
fx=[dict(insert=i.iid+1,track=i.name,plugin=s.internal_name,mix=s._kw['params'][1]['msg']/12800) for i in p.mixer for s in i if s.plugin and s.internal_name=='Fruity Reeverb 2']
assert len(fx)==6
native=root/'FL Render/NIGHT GRAVE V3.wav'
a,sr=sf.read(native,always_2d=True)
assert len(a)/sr>146 and np.max(np.abs(a))>.1 and np.all(np.isfinite(a))
report=dict(fl_studio='24.2.2.4597',bpm=144,seconds=len(a)/sr,peak_dbfs=float(20*np.log10(np.max(np.abs(a)))),rms_dbfs=float(20*np.log10(np.sqrt(np.mean(a*a)))),effects=fx,clips=len(clips),notes=sum(len(list(q.notes)) for q in p.patterns))
report['section_levels']={name:round(float(20*np.log10(np.sqrt(np.mean(a[int(bar*5/3*sr):int((bar+4)*5/3*sr)]**2)))),2) for bar,name in [(0,'intro'),(16,'drop1'),(40,'break'),(56,'drop2'),(80,'outro')]}
(root/'validation.json').write_text(json.dumps(report,indent=2))
shutil.copy2(native,root/'NIGHT GRAVE V3.wav')
subprocess.run(['ffmpeg','-v','error','-i',str(native),'-codec:a','libmp3lame','-b:a','256k','-y',str(root/'NIGHT GRAVE V3.mp3')],check=True)
readme='''NIGHT GRAVE V3 — dark atmospheric phonk
144 BPM, D Phrygian, 88 bars.
Rounded FM tine replaces the piercing cowbell; reduced melody density.
Stronger harmonic pad and a detuned drone follow the bass roots.
Filtered, pitched vocal chops from the locally installed Phonk pack
answer the melody in selected phrases. Filtered delays and six native
Fruity Reeverb 2 inserts connect the lead, voice and atmosphere.
16 sampler channels, 24 editable patterns and 221 playlist clips.
WAV and MP3 are rendered by FL Studio 24.2.2.4597.
Keep the FLP and sample WAVs together, or open the complete ZIP.
Sound design is printed into the assets; notes, routing, envelopes,
reverb blends and mixer controls remain editable.
See production.json for sources and validation.json for native checks.
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
with zipfile.ZipFile(root/'NIGHT GRAVE V3 - complete project.zip','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('NIGHT GRAVE V3.flp',portable)
 for f in (root/'Samples').glob('*.wav'):z.write(f,f.name)
 for name in ['README.txt','production.json','validation.json','NIGHT GRAVE V3.mp3']:z.write(root/name,name)
with zipfile.ZipFile(root/'NIGHT GRAVE V3 - complete project.zip') as z:assert z.testzip() is None
print(json.dumps(report,indent=2))

dest=Path(__file__).resolve().parent/'projects/NIGHT GRAVE V3'
dest.mkdir(parents=True,exist_ok=True)
(dest/'NIGHT GRAVE V3.flp').write_bytes(portable)
for f in (root/'Samples').glob('*.wav'):shutil.copy2(f,dest/f.name)
for name in ['README.txt','production.json','validation.json','NIGHT GRAVE V3.mp3','NIGHT GRAVE V3.wav']:shutil.copy2(root/name,dest/name)
shutil.copy2(root/'NIGHT GRAVE V3 - complete project.zip',Path(__file__).resolve().parent/'downloads/NIGHT GRAVE V3 - complete project.zip')
