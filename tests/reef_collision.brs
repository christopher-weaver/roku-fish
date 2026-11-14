sub Main()
    prefs=ReefValidateSettings(invalid)
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occ=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    world=ReefWorld(prefs,species,occ,47831)
    for i=0 to world.fish.Count()-1
        f=world.fish[i]
        if ReefCoralBlocked(world,f,f,f) then print "FAIL unsafe spawn ";i : return
    end for
    print "PASS all fish spawn with body, tail and fins clear of coral"
    rows=["....#....","........."]
    if not ReefSolidRect(rows,8,31#,0#,34#,7#) then print "FAIL thin branch footprint" : return
    if ReefSolidRect(rows,8,0#,0#,23#,15#) then print "FAIL open footprint" : return
    print "PASS fine occupancy detects a partial-cell branch without blocking open water"
    f=world.fish[0]
    rear={x:70#,y:870#,z:0.25} : front={x:70#,y:870#,z:0.9}
    if not ReefCoralBlocked(world,f,rear,front) then print "FAIL swept depth crossing" : return
    print "PASS swept movement cannot tunnel through a coral slab"
    ' Put a single branch under the tail: the fish center remains in open water.
    sample={x:1000#,y:400#,z:0.48}
    p=ReefProjection(sample,64#)
    col=Int((p.x+64-f.sp.collisionHalfWidth*f.sp.length/f.sp.renderLength*.7)/8)
    row=Int((p.y+36)/8)
    mock=[]
    for y=0 to 143
        line=String(256,".")
        if y=row then line=Left(line,col)+"#"+Mid(line,col+2)
        mock.Push(line)
    end for
    testWorld={occupancy:{cell:8,planes:[{z:0.48,halfDepth:0.025,rows:mock}]}}
    if not ReefCoralBlocked(testWorld,f,sample,sample) then print "FAIL tail contact" : return
    print "PASS tail and fin footprint blocks contact even when the center is clear"
    violations=0 : stopped=0
    for tick=0 to 899
        ReefAdvance(world,1#/30#)
        for i=0 to world.fish.Count()-1
            f=world.fish[i]
            if ReefCoralBlocked(world,f,f,f) then violations=violations+1
            distance=Sqr((f.x-f.previousX)^2+(f.y-f.previousY)^2+((f.z-f.previousZ)*800)^2)
            if distance>f.sp.speed*1.3*1.18/30*1.1 then print "FAIL position jump" : return
            pose=ReefDisplayPose(f,0.5)
            if ReefCoralBlocked(world,f,pose,pose) then violations=violations+1
        end for
    end for
    if violations<>0 then print "FAIL coral intersections at simulation or interpolated poses ";violations : return
    print "PASS 30 seconds, 18 fish, whole footprints and interpolated poses stay clear without position jumps"
    s=ReefWorld(prefs,species,occ,1)
    if s.renderFps<>60 then print "FAIL default 60Hz target" : return
    for i=0 to 2
        ReefQualitySample(s,4#,160)
    end for
    if s.renderFps<>30 then print "FAIL stable 30Hz fallback" : return
    ReefQualitySample(s,4#,240)
    if s.renderFps<>30 then print "FAIL pacing oscillation" : return
    print "PASS 60Hz target falls back to stable 30Hz after sustained missed frames"
end sub
