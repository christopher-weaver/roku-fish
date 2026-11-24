sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occ=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    s=ReefWorld(ReefValidateSettings(invalid),species,occ,47831)
    c=s.clam : c.order=[0,1] : c.rng=1000#
    s.time=9# : ReefClamStep(s)
    if c.event<>0 or not c.released or ReefClamOpening(s.time)<>1# then print "FAIL pearl opening" : return
    c.rng=1000# : s.time=56# : ReefClamStep(s)
    if c.event<>1 or not c.released then print "FAIL bubble event" : return
    born=c.bubbles[0].born : seed=c.rng : ReefClamStep(s)
    if c.bubbles[0].born<>born then print "FAIL duplicate release" : return
    if c.rng<>seed then print "FAIL birth odds rerolled within one opening" : return
    if c.bubbles.Count()<>12 or c.bubbles[11].born<=born then print "FAIL bubble cluster" : return
    while s.fish.Count()>1
        s.fish.Pop()
    end while
    s.fish[0].x=250# : s.fish[0].y=400# : s.fish[0].z=.12
    c.rng=1# : s.time=87# : ReefClamStep(s)
    s.displayTime=s.time
    if ReefClamDisplayOpening(s)<>0# then print "FAIL birth must start inside closed clam" : return
    if s.fish.Count()<>2 or c.births<>1 then print "FAIL baby not added" : return
    baby=s.fish[1] : x=baby.x : y=baby.y
    if baby.name<>s.fish[0].name or baby.size>.4 then print "FAIL baby species cache or size" : return
    if ReefCoralBlocked(s,baby,baby,baby) or ReefFishBlocked(s,baby,baby,baby,false) then print "FAIL unsafe birth" : return
    ReefClamStep(s)
    if s.fish.Count()<>2 then print "FAIL duplicate birth" : return
    if baby.emerging<>true then print "FAIL no interior baby stage" : return
    s.time=99#
    for tick=1 to 240
        ReefStep(s,1#/30#)
        if ReefCoralBlocked(s,baby,baby,baby) then print "FAIL baby leaves swim volume" : return
    end for
    if baby.emerging=true then print "FAIL baby never clears the mouth" : return
    if baby.x=x and baby.y=y then print "FAIL baby is decorative/static" : return
    c.births=4 : c.rng=1# : s.time=244# : ReefClamStep(s)
    if c.event=2 then print "FAIL unbounded births" : return
    rare=0
    for bucket=0 to 49
        seed=Int((((bucket+.5)/50#)*2147483646#+1#)/48271#)
        sample={rng:seed,order:[0,1]}
        event=ReefClamEvent(sample,bucket)
        if event=2
            rare=rare+1
            if bucket<>0 then print "FAIL birth outside one-in-fifty bucket" : return
        else if event<>bucket mod 2
            print "FAIL ordinary pearl/bubble event" : return
        end if
    end for
    if rare<>1 then print "FAIL birth probability is not 1/50" : return
    print "PASS one birth bucket in fifty; one independent roll per clam opening"
    print "PASS clam pearl, staggered rising bubble pool, single safe live-fish birth, normal AI movement and bounded population"
    previous=ReefClamOpening(0#)
    for i=1 to 2820
        opening=ReefClamOpening(i/60#)
        if Abs(opening-previous)>.0063 then print "FAIL hinge discontinuity" : return
        previous=opening
    end for
    print "PASS slow continuous hinge motion with open/closed pauses"
    prefs=ReefValidateSettings({lighting:"Night"})
    light=ReefLighting(12#,prefs.lighting,7#,18.5)
    if prefs.lighting<>"Night" or light[0]>=.12 then print "FAIL selectable night darkness" : return
    screen={calls:[],DrawScaledObject:LifeCapture,DrawObject:LifeObject}
    r={screen:screen,scale:1#,canvasOffset:0#}
    a={glow:{normal:"glow"}}
    s.settings.lighting="Night" : s.lighting=light : s.displayTime=s.time
    ReefDrawBioluminescence(r,s,a)
    if screen.calls.Count()<>36 then print "FAIL missing emissive plankton/coral" : return
    screen.calls=[] : s.settings.lighting="Daylight" : ReefDrawBioluminescence(r,s,a)
    if screen.calls.Count()<>0 then print "FAIL daylight glow" : return
    print "PASS selectable Night lighting with blue-green coral and plankton emission confined to Night/dark Automatic"
    for each name in species
        f={sp:species[name],size:1.12,x:500#,y:30#,z:.94}
        if not ReefSurfaceBlocked(s,f,f,f) then print "FAIL surface envelope accepts shallow fish" : return
        f.y=350#
        if ReefSurfaceBlocked(s,f,f,f) then print "FAIL surface envelope blocks deep fish" : return
    end for
    print "PASS every species reserves full posed outline below surface ripples"
end sub
function LifeCapture(x as integer,y as integer,sx as float,sy as float,source as dynamic,tint as integer) as boolean
    m.calls.Push({x:x,y:y,tint:tint}) : return true
end function
function LifeObject(x as integer,y as integer,source as dynamic,tint as integer) as boolean
    return LifeCapture(x,y,1#,1#,source,tint)
end function
