from pathlib import Path

root=Path(__file__).resolve().parent
s=(root/'build_dark_phonk_v3.py').read_text(encoding='utf-8-sig')
s=s.replace('NIGHT GRAVE V3','NIGHT GRAVE - DROP STUDY')
start=s.index('ids={}'); end=s.index('\ndef read_events',start)
s=s[:start]+'''ids={}
# One four-bar rhythm supplies the kick, bass and lead accents.
pockets=[0,1.75,3.25,4,6.5,8,9.75,11.25,12,14.5,15.5]
roots_by_bar=[38,38,39,38] # D pedal, brief Eb tension, return to D.
for variation in range(4):
    hits=pockets.copy()
    if variation==1:hits.remove(11.25)
    if variation==2:hits=[x for x in hits if x<14]+[14.25,15.25]
    if variation==3:hits=[x for x in hits if x<15]
    ids['kick'+str(variation)]=add_pattern('KICK / pocket '+str(variation+1),0,
        [nt(x,vel=110 if x%4==0 else 90 if x%1 else 102) for x in hits])
    bass=[]
    for i,x in enumerate(hits):
        following=hits[i+1] if i+1<len(hits) else 16
        dur=min(1.35,following-x-.16)
        bass.append(nt(x+.065,roots_by_bar[int(x//4)],length=max(.15,dur),vel=103 if x%4==0 else 86))
    ids['bass'+str(variation)]=add_pattern('BASS / shared pocket '+str(variation+1),7,bass)
    # A small D-F-Eb cell: statements at kick accents, answers in the rests.
    phrase=[(0,62,.45,91),(1.75,65,.22,77),(3.25,63,.28,70),
            (4,62,.65,83),(6.5,60,.3,68),
            (8,63,.45,87),(9.75,65,.22,74),(11.25,63,.25,70),
            (12,62,.75,88),(14.5,57,.38,65)]
    if variation==1:phrase=[n for n in phrase if n[0] not in [6.5,11.25]]
    if variation==2:phrase=phrase[:8]+[(12,62,.55,84),(14.25,63,.2,71),(15.25,62,.25,68)]
    if variation==3:phrase=phrase[:8]+[(12,62,1.3,83)]
    ids['lead'+str(variation)]=add_pattern('LEAD / linked phrase '+str(variation+1),5,
        [nt(x,k,length=d,vel=v) for x,k,d,v in phrase])
ids['clap']=add_pattern('CLAP / half-time anchor',1,[nt(x+.012,vel=100 if i%2==0 else 89) for i,x in enumerate([2,6,10,14])])
ids['ghost']=add_pattern('SNARE / quiet replies',2,[nt(x,vel=v,length=.06) for x,v in [(5.75,29),(10.75,35),(13.75,27),(15.75,39)]])
for variation in range(2):
    hats=[]
    for b in range(4):
        for x,v in [(0,59),(.58,34),(1.5,52),(2.58,39),(3,62),(3.58,32)]:
            if b==3 and variation and x>2:continue
            hats.append(nt(b*4+x,length=.045,vel=v,pan=60 if x%1 else 68))
    if variation:hats += [nt(14.75+i/6,length=.035,vel=28+i*5) for i in range(3)]
    ids['hat'+str(variation)]=add_pattern('HAT / broken swung weave '+str(variation+1),3,hats)
ids['open']=add_pattern('OPEN HAT / two breaths',4,[nt(3.5,vel=43),nt(11.5,vel=37)])
ids['pad']=add_pattern('PAD / pedal and tension',9,[nt(x,k,length=dur,vel=48) for x,dur,ks in [(0,7.6,[50,57]),(8,3.6,[51,58]),(12,3.6,[50,57])] for k in ks])
ids['air']=add_pattern('AIR / low tape bed',13,[nt(0,length=16,vel=42)])
ids['echo']=add_pattern('ECHO / phrase answer',6,[nt(6.5,60,vel=48),nt(14.5,57,vel=42)])
sections=[(0,'A / SHARED POCKET'),(4,'A / SPACE'),(8,'B / TENSION'),(12,'RETURN / CUT')]
for block in range(4):
    bar=block*4
    for role in ['kick','bass','lead']:place(ids[role+str(block)],bar)
    for role in ['clap','ghost','open','pad','air']:place(ids[role],bar)
    place(ids['hat'+str(block%2)],bar)
    if block in [1,3]:place(ids['echo'],bar)
''' + s[end:]
s=s.replace("effect_map={1:.12,5:.32,6:.32,9:.40,14:.30,15:.55}","effect_map={1:.08,5:.18,6:.24,9:.32}")
s=s.replace("bars=88,duration_seconds=88*SECONDS_BAR","bars=16,duration_seconds=16*SECONDS_BAR").replace('duration=88*SECONDS_BAR','duration=16*SECONDS_BAR')
s=s.replace("'DROP II / OCTAVE CURSE'","'RETURN / CUT'")
(root/'build_drop_study.py').write_text(s,encoding='utf-8')
print('Wrote independent 16-bar drop builder')
