sub Main()
    wave={marker:7} : ReefSurface(.125,wave)
    if wave.marker<>7 or wave.first<>0 or wave.blend<>.5 then print "FAIL reusable wave sample" : return
    pacing={marker:7} : ReefFrameSchedule(0#,0#,60#,pacing)
    if pacing.marker<>7 or pacing.sleepMs<>0 then print "FAIL reusable pacing object" : return
    pan={marker:7} : ReefPixelPhase(1.25,pan)
    if pan.marker<>7 or pan.first<>1 or pan.blend<>.25 then print "FAIL reusable pan phase" : return
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    sp=species.blue_tang : ReefTailRigInit(sp)
    expected=0
    for each name in species.Keys()
        item=species[name] : expected=expected+item.frames.Count()+item.tailFrames.Count()+item.finFrames.Count()
    end for
    world={species:species} : a={fish:{blue_tang:true}}
    ReefReleaseAssetMetadata(world,a)
    if world.species.Count()<>1 or world.species.blue_tang=invalid then print "FAIL lost loaded species" : return
    if sp.frames<>invalid or sp.tailFrames<>invalid or sp.finFrames<>invalid then print "FAIL retained decoded frame metadata" : return
    if world.assetMemory.released_frame_objects<>expected then print "FAIL unexpected released frame table count" : return
    ReefTailRigInit(sp)
    if sp.tailBodyPoints=invalid or sp.tailSourcePoints=invalid then print "FAIL lost runtime attachments" : return
    print "PASS releases ";expected;" JSON frame objects and unused species after loading; runtime attachments survive"
    body={size:1,sp:{image:"test",length:100},bodyBounds:{sizeKey:1,species:"test",radius:100#,height:50#},x:0#,y:0#,z:.5}
    other={size:1,sp:body.sp,bodyBounds:body.bodyBounds,x:204.005,y:0#,z:.5}
    if ReefFishPairBlocked(body,body,body,other,false) then print "FAIL static fixture already touching" : return
    if not ReefFishPairBlocked(body,body,body,other,true) then print "FAIL missing swept contact precision margin" : return
    other.x=204.02
    if ReefFishPairBlocked(body,body,body,other,true) then print "FAIL oversized contact precision margin" : return
    if ReefMemoryPressure("roAppMemoryNotificationEvent",{memoryUsagePercent:75}) then print "FAIL collecting on memory recovery" : return
    if not ReefMemoryPressure("roAppMemoryNotificationEvent",{memoryUsagePercent:85}) then print "FAIL missed actual memory pressure" : return
    if ReefMemoryPressure("roDeviceInfoEvent",{generalMemoryLevel:"normal"}) then print "FAIL collecting on normal device memory" : return
    if not ReefMemoryPressure("roDeviceInfoEvent",{generalMemoryLevel:"low"}) then print "FAIL missed low general memory" : return
    s={settings:{quality:"Auto"},renderFps:60#,pacingPressure:0#,quality:1#,adaptation:0#}
    for i=0 to 2
        ReefQualitySample(s,4#,120,25#,0#)
    end for
    if s.renderFps<>30# then print "FAIL no steady cadence under sustained load" : return
    for i=0 to 4
        ReefQualitySample(s,4#,120,10#,0#)
    end for
    if s.renderFps<>60# then print "FAIL Auto permanently trapped at 30 FPS" : return
    s.renderFps=30#
    for i=0 to 7
        ReefQualitySample(s,4#,120,10#,15#)
    end for
    if s.renderFps<>30# then print "FAIL recovery ignores graphics blocking" : return
    fresh=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occ=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    clock=ReefWorld(ReefValidateSettings({density:"Low"}),fresh,occ,47831)
    clock.clam.enabled=false : clock.time=86399.99 : deadline=clock.time+10#
    ReefAdvance(clock,1#/30#)
    if clock.time<86400# or clock.displayTime<86399# or deadline-clock.time>10# then print "FAIL daily rollover reset deadlines or display time" : return
    print "PASS monotonic world/display clocks cross 24 hours without resetting deadlines"
    print "PASS memory recovery notifications do not force GC; Auto recovers only with sustained measured headroom"
end sub
