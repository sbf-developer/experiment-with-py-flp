"""Original editable FL Studio composition using locally installed sounds."""
from pathlib import Path
import struct, json, subprocess, base64
import numpy as np
import soundfile as sf
from scipy.signal import butter,sosfilt,resample_poly
import pyflp
from pyflp._events import EventEnum,_EventEnumMeta
from pyflp.channel import EnvelopeLFOEvent

original=_EventEnumMeta.__call__
def compatible(cls,value,*args,**kw):
    return cls._missing_(value) if cls is EventEnum else original(cls,value,*args,**kw)
_EventEnumMeta.__call__=compatible
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'NIGHT GRAVE V3'; SAMPLES=OUT/'Samples'; SAMPLES.mkdir(parents=True,exist_ok=True)
PACKS=Path(r'C:\Program Files\Image-Line\FL Studio 2024\Data\Patches\Packs')
SR=44100; BPM=144; PPQ=96; BAR=384; SECONDS_BAR=5/3
rng=np.random.default_rng(731)
ledger=[]
def load(rel):
    try:a,sr=sf.read(PACKS/rel,always_2d=True,dtype='float32')
    except sf.LibsndfileError:
        raw=subprocess.run(['ffmpeg','-v','error','-i',str(PACKS/rel),'-f','f32le','-ac','2','-ar',str(SR),'-'],capture_output=True,check=True).stdout
        a=np.frombuffer(raw,dtype='<f4').reshape(-1,2).copy();sr=SR
    if sr!=SR:a=resample_poly(a,SR,sr)
    if a.shape[1]==1:a=np.repeat(a,2,axis=1)
    return a[:,:2]
def filt(a,f,typ='lowpass'):return sosfilt(butter(2,f,btype=typ,fs=SR,output='sos'),a,axis=0).astype('float32')
def pitch(a,ratio):
    pos=np.arange(0,len(a)-1,ratio)
    return np.stack([np.interp(pos,np.arange(len(a)),a[:,i]) for i in range(2)],axis=1).astype('float32')
def fade(a,start=.003,end=.03):
    a=a.copy();n=min(len(a),int(start*SR)); m=min(len(a),int(end*SR))
    if n:a[:n]*=np.linspace(0,1,n)[:,None]
    if m:a[-m:]*=np.linspace(1,0,m)[:,None]
    return a
def norm(a,peak=.8):return a*(peak/max(.00001,float(np.max(np.abs(a)))))
def save(name,a,source,process):
    a=fade(a);sf.write(SAMPLES/(name+'.wav'),a,SR,subtype='PCM_24')
    ledger.append(dict(file=name+'.wav',source=str(PACKS/source) if source else 'Generated transition from installed sample',processing=process))
    return a

# Process one shots, retaining native Sampler envelopes, pitch and note editing.
kick=save('01_Grave_Kick',norm(filt(load('Phonk/phonk mano/Kick Mano 2.wav'),8000),.9),'Phonk/phonk mano/Kick Mano 2.wav','DC removal; 8 kHz low pass; short tail')
clap=save('02_Tape_Clap',norm(filt(load('Phonk/phonk mano/Clap Mano.wav'),700,'highpass'),.75),'Phonk/phonk mano/Clap Mano.wav','High pass 700 Hz')
snare=save('03_Dry_Snare',norm(load('Phonk/phonk mano/Snare Mano 2.wav'),.7),'Phonk/phonk mano/Snare Mano 2.wav','Level matched')
hat_source='Drums (ModeAudio)/Hi Hats/Attack Hat 01.wv'
oh_source='Drums (ModeAudio)/Hi Hats/Volt CleanOHat 03.wv'
hat=save('04_Closed_Hat',norm(filt(load(hat_source)[:int(.10*SR)],5000,'highpass'),.55),hat_source,'5 kHz high pass; 100 ms tail')
oh=save('05_Open_Hat',norm(filt(load(oh_source),3500,'highpass'),.55),oh_source,'3.5 kHz high pass')
# Stable pitched instruments replace ambiguous roots in the first version.
t=np.arange(int(1.2*SR))/SR;f=261.625565
# Rounded tine: little high-frequency energy and no square-wave transient.
body=np.sin(2*np.pi*f*t+.38*np.sin(2*np.pi*2.002*f*t)*np.exp(-t/.23))
body+=.13*np.sin(2*np.pi*2.005*f*t)+.035*np.sin(2*np.pi*3.99*f*t)
body*=np.exp(-t/.34)*(1-np.exp(-t/.014))
bell=np.stack([body,body],axis=1).astype('float32');bell=filt(bell,2900)
bell=save('06_Velvet_Tine_C4',norm(bell,.65),None,'Rounded sine/FM tine; 14 ms attack; 340 ms decay; 2.9 kHz low pass; no square oscillators')
ghost=np.zeros((int(2.4*SR),2),np.float32)
for delay,gain in [(.3125,.4),(.625,.21),(.9375,.11)]:
    start=int(delay*SR);tail=filt(bell,2100)*gain
    ghost[start:start+len(tail)]+=tail[:,::-1] if delay==.625 else tail
ghost=save('07_Velvet_Echo_C4',ghost,None,'Filtered dotted-eighth delays 312.5/625/937.5 ms at 144 BPM')
t=np.arange(3*SR)/SR;f=65.406391
phase=2*np.pi*f*(t+.008*(1-np.exp(-t/.009)))
sub=np.sin(phase)+.12*np.sin(2*phase)+.04*np.sin(3*phase)
sub=np.tanh(sub*1.65)*np.exp(-t/1.25)*np.minimum(1,t/.004)
bass=np.repeat(sub[:,None],2,axis=1).astype('float32');bass=filt(filt(bass,25,'highpass'),900)
bass=save('08_Distorted_808_C2',norm(bass,.8),None,'Stable C2 sub; controlled saturation; fast transient pitch drop; mono; 25 Hz high pass')
t=np.arange(4*SR)/SR;f=130.812783
reese=np.stack([np.sin(2*np.pi*f*.996*t)+.25*np.sin(2*np.pi*2*f*t),np.sin(2*np.pi*f*1.004*t)+.25*np.sin(2*np.pi*2*f*t)],axis=1)
reese=filt(np.tanh(reese*2),850);reese=filt(reese,150,'highpass')
reese=save('09_Shadow_Reese_C3',norm(reese,.55),None,'Detuned stable C3 oscillators; 150Ã¢â‚¬â€œ850 Hz; smooth onset')
t=np.arange(7*SR)/SR;f=261.625565
pad=np.stack([sum(np.sin(2*np.pi*f*.998*h*t)/(h**1.6) for h in [1,2,3,4,5,7]),sum(np.sin(2*np.pi*f*1.002*h*t)/(h**1.6) for h in [1,2,3,4,5,7])],axis=1)
pad*=((1-np.exp(-t/.3))*np.exp(-t/7))[:,None];pad=filt(filt(pad,190,'highpass'),2100)
pad=save('10_Crypt_Pad_C4',norm(pad,.45),None,'Stable C4 dark detuned pad; 300 ms attack; 1.7 kHz low pass; live hall reverb on mixer')
impact=save('11_Impact',norm(load('Phonk/Life in Rio/Impact Mano.wav'),.7),'Phonk/Life in Rio/Impact Mano.wav','Level matched; fade tail')
reverse=norm(filt(impact[::-1],400,'highpass'),.5)
reverse=save('12_Reverse_Impact',reverse,'Phonk/Life in Rio/Impact Mano.wav','Reverse impact; high pass 400 Hz')
t=np.arange(int((16*60/BPM)*SR))/SR
noise=rng.normal(0,.2,(len(t),2)).astype('float32');noise=filt(noise,1700,'highpass')
sweep=np.sin(2*np.pi*(90*t+35*t*t))[:,None]*.025
riser=(noise+sweep)*np.linspace(0,1,len(t))[:,None]**2
riser=save('13_Riser_4bars',norm(riser,.35),None,'Deterministic filtered noise and rising oscillator; four bars')
texture=filt(rng.normal(0,.08,(int((16*60/BPM)*SR),2)).astype('float32'),3200)
texture=filt(texture,450,'highpass');texture=save('14_Tape_Air_4bars',norm(texture,.09),None,'Deterministic band-limited tape noise; four bars')

# Human vocal phrases from the local sample pack, chosen from active audio.
vocal_source='Phonk/Phonk song/Vocal (69).wav'
voice=load(vocal_source)
window=int(.8*SR);rms=[np.mean(voice[i:i+window]**2) for i in range(0,len(voice)-window,int(.1*SR))]
start=int(np.argmax(rms)*.1*SR);phrase=voice[start:start+window]
phrase=fade(filt(filt(pitch(phrase,.75),180,'highpass'),2800),.025,.09)
voxel=np.zeros((len(phrase)+int(.84*SR),2),np.float32)
voxel[:len(phrase)]+=phrase
for delay,gain in [(.416667,.22),(.833333,.10)]:
    offset=int(delay*SR);voxel[offset:offset+len(phrase)]+=phrase[:,::-1]*gain
vocal=save('15_Shadow_Vocal',norm(voxel,.6),vocal_source,'Active 800 ms phrase; pitch -5 semitones; radio band 180Ã¢â‚¬â€œ2800 Hz; quarter-note echo')
t=np.arange(int((16*60/BPM)*SR))/SR;f=130.812783
scape=np.stack([sum(np.sin(2*np.pi*f*.997*h*t+.2*np.sin(t*.7))/(h**1.8) for h in [1,2,3,5]),sum(np.sin(2*np.pi*f*1.003*h*t+.2*np.sin(t*.6))/(h**1.8) for h in [1,2,3,5])],axis=1)
scape*=((1-np.exp(-t/.8))*(.7+.3*np.sin(t*.38)**2))[:,None]
scape=filt(filt(scape,115,'highpass'),1500)
scape=save('16_Descent_Drone_C3',norm(fade(scape,.4,.6),.55),None,'Slowly evolving stereo drone; smooth 800 ms rise; compatible chord roots; native shared reverb')
names=['Grave Kick','Tape Clap','Dry Snare','Closed Hat','Open Hat','Velvet Tine','Velvet Echo','Distorted 808','Shadow Reese','Crypt Pad','Impact','Reverse Impact','Riser','Tape Air','Shadow Vocal','Descent Drone']
audio=[kick,clap,snare,hat,oh,bell,ghost,bass,reese,pad,impact,reverse,riser,texture,vocal,scape]
roots=[60]*len(names);roots[15]=48;roots[7]=36;roots[8]=48;roots[9]=60
gains=[.70,.31,.12,.15,.10,.23,.13,.48,.10,.46,.12,.08,.10,.09,.32,.24]
colors=[0x3838ca,0x5555da,0x7777dd,0xa6a050,0xc7bf69,0x9856dc,0xb989ef,0x5840b8,0x725cba,0xae8174,0x6082ad,0x759bbe,0x8bb6ca,0x737373,0xa17ca8,0x807eb6]
patterns=[]; placements=[]
def add_pattern(name,ch,notes,bars=4):
    pid=len(patterns)+1
    patterns.append(dict(id=pid,name=name,ch=ch,notes=notes,bars=bars))
    return pid
def nt(beat,key=60,length=.125,vel=100,pan=64):return (round(beat*PPQ),key,max(1,round(length*PPQ)),vel,pan)
def place(pid,bar):placements.append((pid,bar,patterns[pid-1]['ch']))
ids={}
# Steady drift-phonk pulse. Bass notes stop before the next kick.
for variant in range(3):
    ns=[nt(b*4+x,vel=111 if x%2==0 else 100) for b in range(4) for x in range(4)]
    if variant==1:ns=[n for n in ns if n[0]!=15*PPQ]
    if variant==2:ns += [nt(15.5,vel=82)]
    ids['kick'+str(variant)]=add_pattern('KICK / '+['locked pulse','stop before turn','last-bar pickup'][variant],0,ns)
ids['clap']=add_pattern('CLAP / locked backbeat',1,[nt(b*4+x,vel=100 if x==1 else 106) for b in range(4) for x in [1,3]])
ids['snare']=add_pattern('SNARE / one quiet pickup',2,[nt(14.75,vel=40),nt(15.75,vel=34)])
for variant in range(2):
    ns=[nt(b*4+x*.5+( .025 if x%2 else 0),length=.06,vel=72 if x%2 else 46,pan=62 if x%2 else 66) for b in range(4) for x in range(8)]
    if variant:ns += [nt(15.25+x*.25,length=.045,vel=38+x*5) for x in range(3)]
    ids['hat'+str(variant)]=add_pattern('HAT / restrained swing '+str(variant+1),3,ns)
ids['oh']=add_pattern('OPEN HAT / offbeats',4,[nt(b*4+x,vel=68,length=.22) for b in range(4) for x in [.5,2.5]])
hook=[(0,62),(.5,62),(1,69),(1.75,65),(2.5,62),(3.25,63),(3.5,62),
      (4,62),(4.5,65),(5.5,67),(6.25,65),(7,60),(7.5,62),
      (8,62),(8.5,65),(9,69),(9.75,65),(10.5,62),(11.25,63),(11.5,62),
      (12,60),(12.5,67),(13.5,65),(14.25,63),(15,60),(15.5,62)]
for variant in range(3):
    notes=[(b,k) for b,k in hook if b not in [.5,3.25,4.5,8.5,11.25,12.5]] if variant!=1 else [(b,k) for b,k in hook if b in [0,2.5,4,7,8,10.5,12,15.5]]
    ns=[nt(b,k,length=.17,vel=(92 if i%3==0 else 76) if variant!=1 else 65) for i,(b,k) in enumerate(notes)]
    if variant==2:ns=[nt(b,k,length=.25,vel=83 if i%3==0 else 67) for i,(b,k) in enumerate(notes)]
    ids['bell'+str(variant)]=add_pattern('TINE / '+['grave hook','distant motif','restrained answer'][variant],5,ns)
ids['echo']=add_pattern('DELAY / phrase endings',6,[nt(b,k,length=.3,vel=74) for b,k in hook if b in [3.5,7.5,11.5,15.5]])
for variant in range(3):
    ns=[]
    for b,key in enumerate([38,38,34,36]):
        hits=[(x+.07,.82) for x in range(4)]
        if variant==1:hits=[(.08,1.7),(2.08,1.7)]
        if variant==2 and b==3:hits=[(.07,.82),(1.07,.82),(2.07,.82),(3.07,.34),(3.57,.34)]
        ns += [nt(b*4+x,key,length=dur,vel=100) for x,dur in hits]
    ids['bass'+str(variant)]=add_pattern('808 / '+['kick pocket','break pulses','final pickup'][variant],7,ns)
ids['reese']=add_pattern('REESE / distant undercurrent',8,[nt(b*4,key,length=3.6,vel=72) for b,key in enumerate([50,50,46,48])])
ids['pad']=add_pattern('PAD / dark suspended harmony',9,[nt(b*4,k,length=3.7,vel=78) for b,ks in enumerate([[50,53,57],[50,53,60],[46,50,53],[48,51,55]]) for k in ks])
ids['vocal']=add_pattern('VOCAL / shadows answer',14,[nt(.5,60,length=1,vel=83),nt(10.5,60,length=1,vel=67)])
ids['drone']=add_pattern('DRONE / evolving root',15,[nt(b*4,key,length=3.85,vel=82) for b,key in enumerate([50,50,46,48])])
ids['impact']=add_pattern('IMPACT / downbeat',10,[nt(0,length=2,vel=100)])
ids['reverse']=add_pattern('REVERSE / inhale',11,[nt(12,length=4,vel=90)])
ids['riser']=add_pattern('RISER / tension',12,[nt(0,length=16,vel=100)])
ids['air']=add_pattern('AIR / tape floor',13,[nt(0,length=16,vel=85)])
ids['build']=add_pattern('SNARE / accelerating build',2,[nt(x,length=.08,vel=int(35+3*x)) for x in np.r_[np.arange(0,8,1),np.arange(8,12,.5),np.arange(12,15,.25),np.arange(15,15.875,.125)]])

sections=[(0,'INTRO / THE CRYPT'),(8,'BUILD / OMINOUS'),(16,'DROP I / NIGHT GRAVE'),(32,'DROP I / VARIATION'),(40,'BREAK / EMPTY STREETS'),(48,'BUILD II / RISE'),(56,'DROP II / FULL PRESSURE'),(72,'DROP II / OCTAVE CURSE'),(80,'OUTRO / AFTERMATH')]
for bar in range(0,88,4):
    for key in ['air']:place(ids[key],bar)
    place(ids['pad'],bar)
    place(ids['drone'],bar)
    if bar in [8,20,28,40,48,60,68,80]:place(ids['vocal'],bar)
    if bar<8 or 40<=bar<48 or bar>=80:
        place(ids['bell1'],bar);place(ids['echo'],bar)
        if bar in [4,44,80]:place(ids['bass1'],bar)
        if bar in [4,44,80]:place(ids['hat0'],bar)
    elif 8<=bar<16 or 48<=bar<56:
        place(ids['bell1'],bar);place(ids['bass1'],bar);place(ids['hat0'],bar)
        if bar in [12,52]:
            for key in ['build','riser','reverse']:place(ids[key],bar)
        else:place(ids['clap'],bar)
    else:
        v=2 if bar>=72 else (1 if bar in [24,36,64] else 0)
        for key in ['kick'+str(v),'clap','hat'+str(int(bar%8==4)),'bell'+str(2 if bar>=72 else 0),'bass'+str(v),'echo','reese']:place(ids[key],bar)
        if bar in [28,36,68,76]:place(ids['snare'],bar)
        if bar>=16:place(ids['oh'],bar)
        if bar in [36,76]:place(ids['reverse'],bar)
    if bar in [0,16,32,40,56,72,80]:place(ids['impact'],bar)

def read_events(path):
    data=path.read_bytes();pos=data.index(b'FLdt')+8;ev=[]
    while pos<len(data):
        id=data[pos];pos+=1
        if id<192:n=1 if id<64 else 2 if id<128 else 4
        else:
            n=0;shift=0
            while True:
                b=data[pos];pos+=1;n|=(b&127)<<shift;shift+=7
                if b<128:break
        ev.append((id,data[pos:pos+n]));pos+=n
    return data[:14],ev
def encode(id,payload):
    out=bytes([id])
    if id>=192:
        n=len(payload)
        while n>=128:out+=bytes([(n&127)|128]);n>>=7
        out+=bytes([n])
    return out+payload
def u16(n):return struct.pack('<H',n)
def u32(n):return struct.pack('<I',n)
def txt(s):return (s+'\0').encode('utf-16le')
template=Path(r'C:\Program Files\Image-Line\FL Studio 2024\Data\Templates\Minimal\Basic with limiter\Basic with limiter.flp')
header,events=read_events(template)
start=next(i for i,(eid,d) in enumerate(events) if eid==64)
second=next(i for i,(eid,d) in enumerate(events[start+1:],start+1) if eid==64)
arrstart=next(i for i,(eid,d) in enumerate(events) if eid==99)
sampler_template=events[start:second]
prefix=events[:start]
prefix=[(eid,u32(144000) if eid==156 else b'\x01' if eid==9 else txt('NIGHT GRAVE V3') if eid==194 else txt('Dark Phonk') if eid==206 else d) for eid,d in prefix]
# Preserve the install's template licensing fields exactly; don't infer license status.
notes_events=[];metadata=[]
for p in patterns:
    payload=b''.join(struct.pack('<IHHIHH8B',pos,0,p['ch'],length,key,0,120,0,64,0,pan,vel,128,128) for pos,key,length,vel,pan in sorted(p['notes']))
    notes_events += [(65,u16(p['id'])),(224,payload)]
    metadata += [(65,u16(p['id'])),(193,txt(p['name'])),(150,u32(colors[p['ch']])),(157,u32(0xffffffff)),(158,u32(0xffffffff)),(26,b''),(164,u32(p['bars']*BAR))]
channels=[]
for ch,name in enumerate(names):
    env_index=0
    for eid,d in sampler_template:
        if eid==64:d=u16(ch)
        elif eid==203:d=txt(name)
        elif eid==128:d=u32(colors[ch])
        elif eid==22:d=bytes([ch+1])
        elif eid==196:d=txt(str(SAMPLES/ledger[ch]['file']))
        elif eid==219:
            d=struct.pack('<iI',6400,10000)+d[8:]
        elif eid==135:d=u32(roots[ch])
        elif eid==143:d=u32(3) # no loop points
        elif eid==218:
            if env_index==1 and ch in [7,8,9,15]:
                e=EnvelopeLFOEvent(EventEnum(218),d);v=e.value
                v['envelope.enabled']=1;v['envelope.amount']=128
                v['envelope.predelay']=100;v['envelope.attack']=100 if ch==7 else 1000
                v['envelope.hold']=100;v['envelope.decay']=100;v['envelope.sustain']=128
                v['envelope.release']=700 if ch==7 else 4000
                # Serialize payload without event framing.
                encoded=bytes(e);j=1
                while encoded[j]&128:j+=1
                d=encoded[j+1:]
            env_index+=1
        channels.append((eid,d))
    if not any(eid==135 for eid,d in sampler_template):channels.append((135,u32(roots[ch])))
# Gains are baked into the sample assets, retaining predictable native volume controls.
for ch in range(len(names)):
    sf.write(SAMPLES/ledger[ch]['file'],audio[ch]*gains[ch],SR,subtype='PCM_24')
playlist=b''
for clip_index,(pid,bar,ch) in enumerate(sorted(placements,key=lambda x:(x[1],x[2]))):
    p=patterns[pid-1]
    playlist+=struct.pack('<IHHIHH2sH4sff',bar*BAR,20480,20480+pid,p['bars']*BAR,499-ch,0,b'\x78\x00',64,b'\x40\x64\x80\x80',struct.unpack('<f',b'\xff'*4)[0],struct.unpack('<f',b'\xff'*4)[0])+struct.pack('<I16sfI',64+clip_index,bytes(16),1.,0)
suffix=[];track=0
for eid,d in events[arrstart:]:
    if eid==241:d=txt('NIGHT GRAVE / FULL SONG')
    elif eid==233:d=playlist
    elif eid==238:
        track=struct.unpack_from('<I',d)[0]
        if track<=len(names):d=d[:4]+u32(colors[track-1])+d[8:]
    suffix.append((eid,d))
    if eid==233:
        for bar,label in sections:suffix += [(148,u32(bar*BAR)),(205,txt(label))]
    if eid==238 and track<=len(names):suffix.append((239,txt(names[track-1])))
# Use the complete compatible native plugin state, including its wrapper.
# Changing only the plugin name or loading old preset payloads can freeze FL.
effect_map={1:.12,5:.32,6:.32,9:.40,14:.30,15:.55}
effect_slots={};new_suffix=[];mix_index=-2
fxblock=json.loads((ROOT/'research/reverb_slot.json').read_text())
for eid,d in suffix:
    if eid==236:mix_index+=1
    if eid==236 and 0<=mix_index<len(names):
        new_suffix.append((eid,d));new_suffix.append((204,txt(names[mix_index])))
        continue
    if eid==98 and struct.unpack('<H',d)[0]==0 and mix_index in effect_map:
        amount=effect_map[mix_index]
        new_suffix += [(ident,struct.pack('<II',mix_index+1,0)+base64.b64decode(raw)[8:] if ident==212 else base64.b64decode(raw)) for ident,raw in fxblock]
        effect_slots[mix_index]=amount
    new_suffix.append((eid,d))
suffix=new_suffix
final_events=prefix+notes_events+channels+metadata+suffix
final_events=[(eid,b'24.2.2.4597\x00' if eid==199 else d) for eid,d in final_events]
data=b''.join(encode(eid,d) for eid,d in final_events)
header=header[:10]+u16(len(names))+u16(PPQ)
flp=OUT/'NIGHT GRAVE V3.flp';flp.write_bytes(header+b'FLdt'+u32(len(data))+data)
parsed=pyflp.parse(flp)
for ins in parsed.mixer:
    if 0<=ins.iid<len(names):
        try:ins.name=names[ins.iid]
        except Exception:pass
    if ins.iid in effect_slots:
        slot=ins[0]
        slot._kw['params'][0]['msg']=1
        slot._kw['params'][1]['msg']=round(12800*effect_slots[ins.iid])
pyflp.save(parsed,flp)
parsed=pyflp.parse(flp)

assert parsed.tempo==144 and len(parsed.channels)==len(names)
assert sum(1 for p in parsed.patterns)==len(patterns)
assert sum(len(list(p.notes)) for p in parsed.patterns)==sum(len(p['notes']) for p in patterns)
assert all(c.sample_path.exists() for c in parsed.channels)
json.dump(dict(title='NIGHT GRAVE',bpm=BPM,key='D phrygian',bars=88,duration_seconds=88*SECONDS_BAR,sections=sections,samples=ledger,patterns=patterns,placements=placements),open(OUT/'production.json','w'),indent=2)
print(json.dumps(dict(flp=str(flp),channels=len(names),patterns=len(patterns),clips=len(placements),notes=sum(len(p['notes']) for p in patterns),duration=88*SECONDS_BAR)))
