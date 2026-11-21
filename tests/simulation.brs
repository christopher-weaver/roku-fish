' Direct tests of the production BrightScript, without a duplicate movement model.
sub Main()
    m.passed = 0 : m.failed = 0
    prefs = ReefValidateSettings(invalid)
    Check(prefs.lighting = "Sunset" and prefs.density = "Medium" and prefs.fps = "Off", "sunset defaults")
    bad = ReefValidateSettings({lighting:"invalid",density:72,camera:"Off",fps:"On"})
    Check(bad.lighting = "Sunset" and bad.density = "Medium" and bad.camera = "Off", "invalid settings recover")
    ReefSaveSettings(bad) : saved=ReefLoadSettings()
    Check(saved.camera = "Off" and saved.fps = "On", "registry write flush read roundtrip")
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occ=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    a=ReefWorld(prefs,species,occ,47831) : b=ReefWorld(prefs,species,occ,47831)
    a.clam.enabled=false
    b.clam.enabled=false
    Check(a.fish.Count()=8,"medium population")
    Check(a.fish[4].x=b.fish[4].x and a.fish[4].heading=b.fish[4].heading,"seed initialization repeats")
    low=ReefValidateSettings({density:"Low"}) : high=ReefValidateSettings({density:"High"})
    lowWorld=ReefWorld(low,species,occ,1) : highWorld=ReefWorld(high,species,occ,1)
    lowWorld.clam.enabled=false
    highWorld.clam.enabled=false
    Check(lowWorld.fish.Count()=6,"low population")
    Check(highWorld.fish.Count()=10,"high population")
    badSpeed=0 : badTurn=0 : badBoundary=0 : maxAccel=0#
    for tick=0 to 599
        previous=[]
        for each f in a.fish
            previous.Push({heading:f.heading,speed:f.speed,x:f.x,y:f.y,z:f.z})
        end for
        ReefStep(a,0.1) : ReefStep(b,0.1)
        for i=0 to a.fish.Count()-1
            f=a.fish[i] : old=previous[i]
            if f.speed > f.sp.speed*1.3*1.18+0.01 then badSpeed=badSpeed+1
            accel=Abs(f.speed-old.speed)/0.1
            if accel>maxAccel then maxAccel=accel
            if Abs(ReefAngleDelta(old.heading,f.heading)) > f.turnRate*0.1+0.00001 then badTurn=badTurn+1
            if f.x<0 or f.x>2048 or f.y<80 or f.y>1000 or f.z < -0.03 or f.z>1.03 then badBoundary=badBoundary+1
        end for
    end for
    Check(badSpeed=0,"species speed limits over 60 seconds")
    Check(maxAccel<=19.01,"acceleration capped")
    Check(badTurn=0,"heading turns capped")
    Check(badBoundary=0,"soft wall bounds over 60 seconds")
    Check(a.fish[3].x=b.fish[3].x and a.rng=b.rng,"whole simulation seed repeatability")
    before=a.time : ReefStep(a,50#)
    Check(Abs(a.time-before-0.1)<0.00001,"stalled frame timestep cap")
    pfar=ReefProjection({x:1500#,y:600#,z:0.1},64#) : pnear=ReefProjection({x:1500#,y:600#,z:0.9},64#)
    farMoved=ReefProjection({x:1500#,y:600#,z:0.1},74#) : nearMoved=ReefProjection({x:1500#,y:600#,z:0.9},74#)
    Check(pnear.scale>pfar.scale and Abs(pnear.x-nearMoved.x)>Abs(pfar.x-farMoved.x),"perspective size speed and camera parallax")
    Check(ReefSolid(a,40#,850#),"reef occupancy behind rock")
    Check(not ReefSolid(a,1100#,90#),"open water occupancy")
    cameraGood=true
    for i=0 to 2000
        cx=ReefCamera(i*177.37,"Slow")
        if cx<8 or cx>120 then cameraGood=false
    end for
    Check(cameraGood and ReefCamera(600#,"Off")=64,"camera covers viewport at all boundaries")
    day=ReefLighting(12#,"Automatic",7#,18.5) : night=ReefLighting(0#,"Automatic",7#,18.5) : dusk=ReefLighting(19#,"Automatic",7#,18.5)
    Check(day[0]>dusk[0] and dusk[0]>night[0],"local clock lighting levels")
    smooth=ReefLighting(19.001,"Automatic",7#,18.5)
    Check(Abs(dusk[0]-smooth[0])<0.002,"lighting thresholds continuous")
    sample={fps:30#,settings:{quality:"Auto"},quality:1#,adaptation:0#}
    for i=0 to 5
        ReefQualitySample(sample,4#,80)
    end for
    Check(sample.quality<1 and sample.quality>=0.3,"auto quality degrades optional effects")
    countBefore=a.effects.Count()
    for i=0 to 999
        ReefEffectsStep(a,0.1)
    end for
    Check(a.effects.Count()=countBefore and countBefore=72,"fixed effect pools recycle")
    group={fish:[{id:0,x:500#,y:400#,z:0.5,heading:0#,schooling:true,sp:{length:90}},{id:1,x:700#,y:410#,z:0.5,heading:0#,schooling:true,sp:{length:90}}]}
    steering=ReefNeighbors(group,group.fish[0])
    Check(steering.count=1 and steering.x>0,"school alignment and cohesion")
    group.fish[1].x=530 : steering=ReefNeighbors(group,group.fish[0])
    Check(steering.x<0,"short range separation")
    f=a.fish[0]
    Check(ReefCoralBlocked(a,f,{x:70#,y:870#,z:0.62},{x:70#,y:870#,z:0.9}),"coral depth plane crossing blocked")
    a.time=86399.98 : ReefStep(a,0.1)
    Check(a.time>=0 and a.time<1,"daily phase rollover")
    Check(ReefCamera(0#,"Slow")=8 and Abs(ReefCamera(120#,"Slow")-120)<0.0001 and ReefCamera(240#,"Slow")=8,"camera sweeps left right left with smooth endpoints")
    wave=ReefSurface(7.999) : seam=ReefSurface(8#)
    Check(wave.first=31 and wave.second=0 and seam.first=0 and seam.blend=0,"water surface animation loops continuously")
    Check(ReefBubbleScale(0#)*32>=13 and ReefBubbleScale(1#)*32>=27,"bubbles are larger across depth")
    fixedA=ReefWorld(prefs,species,occ,99) : fixedB=ReefWorld(prefs,species,occ,99)
    fixedA.clam.enabled=false
    fixedB.clam.enabled=false
    ReefAdvance(fixedA,0.1)
    ReefAdvance(fixedB,0.01) : ReefAdvance(fixedB,0.025) : ReefAdvance(fixedB,0.015) : ReefAdvance(fixedB,0.05)
    Check(Abs(fixedA.time-fixedB.time)<0.000001 and fixedA.fish[7].x=fixedB.fish[7].x,"fixed ticks withstand jittery rendering intervals")
    beforeTime=fixedA.time : ReefAdvance(fixedA,12#)
    Check(fixedA.time-beforeTime<0.101,"fixed simulation catches up with a bounded amount of work")
    interpolated=ReefDisplayPose(fixedA.fish[7],0.5)
    Check(interpolated.x>=ReefMin(fixedA.fish[7].previousX,fixedA.fish[7].x) and interpolated.x<=ReefMax(fixedA.fish[7].previousX,fixedA.fish[7].x),"rendering interpolates between fixed simulation poses")
    allFins=true
    for i=0 to fixedA.fish.Count()-1
        if fixedA.fish[i].finPhase=fixedA.fish[i].phase then allFins=false
    end for
    Check(allFins,"pectoral fins have independent animation phases")
    print "RESULT passed=";m.passed;" failed=";m.failed
end sub
sub Check(condition as boolean,name as string)
    if condition
        m.passed=m.passed+1 : print "PASS ";name
    else
        m.failed=m.failed+1 : print "FAIL ";name
    end if
end sub
