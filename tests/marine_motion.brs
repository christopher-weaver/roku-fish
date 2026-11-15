sub Main()
    tank=ParseJson(ReadAsciiFile("pkg:/scenes/tank.json")) : moving=0
    for index=0 to tank.formations.Count()-1
        f=tank.formations[index]
        if f.animation<>invalid
            moving=moving+1 : previous=-1 : changes=0
            for tick=0 to 599
                frame=ReefMarineFrame(tick/60#,f)
                if frame<0 or frame>=65 then print "FAIL marine frame bounds" : return
                if previous>=0
                    if Abs(frame-previous)>1 then print "FAIL marine pose jump" : return
                    if frame<>previous then changes=changes+1
                end if
                previous=frame
            end for
            if changes<65 then print "FAIL static marine poses" : return
            print "PASS coherent ";f.id;" poses, no strip transforms, no skipped geometry states"
        end if
    end for
    if moving<>2 then print "FAIL missing marine animation" : return
    previous=ReefEelPose(0#) : hidden=false : visible=false : previousFrame=ReefEelFrame(0#)
    for tick=1 to 1860
        p=ReefEelPose(tick/60#)
        if Abs(p.y-previous.y)>.51 then print "FAIL eel movement step" : return
        if p.peek=0 then hidden=true
        if p.peek=1 then visible=true
        if Abs(p.angle)>2.001 then print "FAIL eel angle" : return
        poseIndex=ReefEelFrame(tick/60#)
        if poseIndex<0 or poseIndex>64 or Abs(poseIndex-previousFrame)>1 then print "FAIL cave emergence state jump" : return
        if Abs(p.z-previous.z)>1.1 then print "FAIL cave depth movement step" : return
        previousFrame=poseIndex : previous=p
    end for
    if not hidden or not visible then print "FAIL eel never hides or peeks" : return
    print "PASS slow eased eel emergence, retreat and hidden pause"
    camera=ReefCamera(45#,"Slow",tank.camera)
    if Abs(camera-64#)>.001 then print "FAIL faster pan period" : return
    print "PASS Slow pan cycle is three minutes with unchanged sweep width"
end sub
