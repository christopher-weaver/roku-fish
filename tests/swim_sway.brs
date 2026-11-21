sub Main()
    sp=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))["yellow_tang"]
    body=[] : tails=[] : fins=[]
    for i=0 to sp.frames.Count()-1
        body.Push({normal:"body",fractional:"body"})
    end for
    for i=0 to sp.tailFrames.Count()-1
        tails.Push({normal:"tail",fractional:"tail"})
    end for
    for i=0 to sp.finFrames.Count()-1
        fins.Push({normal:"fin",fractional:"fin"})
    end for
    screen={angles:[],DrawTransformedObject:SwimCapture}
    r={screen:screen,scale:1#,canvasOffset:0#,rotation:true,fractionalFish:true,placement:{}}
    s={camera:64#,displayTime:0#,lighting:[1#,0#,0#,0#],settings:{lighting:"Sunset"}}
    a={fish:{yellow_tang:body},tails:{yellow_tang:tails},fins:{yellow_tang:fins}}
    f={name:"yellow_tang",sp:sp,size:1#,speed:sp.speed,renderPose:{x:900#,y:400#,z:.7,heading:.35,pitch:0#,phase:0#,finPhase:0#}}
    low=100# : high=0#-100# : previous=invalid
    for tick=0 to 119
        f.renderPose.phase=tick*6.283185307/60#
        screen.angles=[] : ReefDrawFish(r,s,a,f)
        if screen.angles.Count()<>3 then print "FAIL body sway fragments fish" : return
        angle=screen.angles[0]
        if Abs(screen.angles[1]-angle)>.00001 or Abs(screen.angles[2]-angle)>.00001 then print "FAIL detached appendages" : return
        low=ReefMin(low,angle) : high=ReefMax(high,angle)
        if previous<>invalid and Abs(angle-previous)>.25 then print "FAIL swim angle jumps" : return
        previous=angle
        if Abs(f.renderPose.heading-.35)>.000001 or f.renderPose.y<>400# then print "FAIL display sway changes physics" : return
        if Abs(f.swimPose.x-900#)>3 or Abs(f.swimPose.y-400#)>3 or Abs(f.swimPose.z-.7)*800#>3 then print "FAIL swim sway exceeds clearance" : return
    end for
    if high-low<1# then print "FAIL whole body remains rigid" : return
    print "PASS production body, tail and fins sway together continuously while physical trajectory and clearance remain unchanged"
end sub
function SwimCapture(x as integer,y as integer,angle as float,sx as float,sy as float,source as dynamic,tint as integer) as boolean
    m.angles.Push(angle)
    return true
end function
