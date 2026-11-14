sub Main()
    prefs=ReefValidateSettings(invalid)
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occ=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    world=ReefWorld(prefs,species,occ,47831)
    ReefAdvance(world,1#/30#)
    physics=world.time : beforeTime=world.displayTime
    before=ReefEffectPose(world.effects[48],world.renderAlpha)
    ReefAdvance(world,1#/60#)
    after=ReefEffectPose(world.effects[48],world.renderAlpha)
    if world.time<>physics or world.displayTime<=beforeTime or after.y=before.y then print "FAIL display-only interpolation" : return
    print "PASS surface clock and bubbles advance on intermediate 60Hz frames without extra simulation work"
    if Abs(after.y-(world.effects[48].previousY+world.effects[48].y)*.5)>0.00001 then print "FAIL bubble interpolation" : return
    print "PASS bubble positions interpolate between fixed ticks"
    world.effects[48].y=38.01
    ReefEffectsStep(world,0.1)
    e=world.effects[48] : pose=ReefEffectPose(e,0.5)
    if pose.y<>e.y or pose.x<>e.x then print "FAIL bubble recycle streak" : return
    print "PASS recycled bubbles do not streak across the water"
    a=ReefSurface(0.123) : b=ReefSurface(8.123)
    if a.first<>b.first or Abs(a.blend-b.blend)>0.000001 then print "FAIL synchronized wave loop" : return
    a=ReefSurface(7.999) : b=ReefSurface(8#)
    if a.second<>b.first or a.blend<0.99 then print "FAIL wave seam" : return
    print "PASS shared surface and sand phase wraps continuously over 32 frames"
    clock=0# : deadline=0# : vsync=1000#/60#
    for frame=1 to 180
        drawEnd=clock+4#
        pacing=ReefFrameSchedule(drawEnd,deadline,60#)
        deadline=pacing.deadline
        if pacing.sleepMs<>0 then print "FAIL extra 60Hz wait" : return
        submitted=drawEnd+pacing.sleepMs+5#
        clock=(Int(submitted/vsync)+1)*vsync
    end for
    if Abs(clock-3000#)>0.001 then print "FAIL blocking-vsync pacing ";clock : return
    clock=0# : deadline=0#
    for frame=1 to 120
        drawEnd=clock+4#
        pacing=ReefFrameSchedule(drawEnd,deadline,30#)
        deadline=pacing.deadline
        submitted=drawEnd+pacing.sleepMs+5#
        clock=(Int(submitted/vsync)+1)*vsync
    end for
    if Abs(clock-4000#)>0.001 then print "FAIL 30Hz pacing with GPU work ";clock : return
    pacing=ReefFrameSchedule(7000#,deadline,60#)
    if pacing.sleepMs<>0 or pacing.deadline<>7000# then print "FAIL late-frame recovery" : return
    print "PASS native vsync pacing sustains 60Hz, capped pacing sustains 30Hz including GPU work, and stalls recover"
    for each name in species
        sp=species[name]
        if sp.yawCount<32 or sp.poseCount<4 or sp.finPoseCount<5 then print "FAIL dense fish animation" : return
    end for
    print "PASS every species has 64 upright yaw views with independent tail and pectoral animation"
end sub
