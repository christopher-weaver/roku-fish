sub Main()
    sp=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))["yellow_tang"]
    body=[] : tails=[] : fins=[]
    strips=[]
    for i=0 to 7
        center=(i-3.5)*sp.frameW/8#
        strips.Push({normal:"body",fractional:"body",offsetX:.5,offsetY:.5,centerX:center,waveForward:ReefWaveFactors(.5-center/(sp.frameW*.9)),waveReverse:ReefWaveFactors(.5+center/(sp.frameW*.9))})
    end for
    for i=0 to sp.frames.Count()-1
        body.Push({normal:"body",fractional:"body",bands:strips})
    end for
    for i=0 to sp.tailFrames.Count()-1
        tails.Push({normal:"tail",fractional:"tail",offsetX:.5,offsetY:.5})
    end for
    for i=0 to sp.finFrames.Count()-1
        fins.Push({normal:"fin",fractional:"fin",offsetX:.5,offsetY:.5})
    end for
    screen={angles:[],sources:[],opacity:[],DrawTransformedObject:SwimCapture}
    r={screen:screen,scale:1#,canvasOffset:0#,rotation:true,fractionalFish:true,placement:{}}
    s={camera:64#,displayTime:0#,lighting:[1#,0#,0#,0#],settings:{lighting:"Sunset"}}
    a={fish:{yellow_tang:body},tails:{yellow_tang:tails},fins:{yellow_tang:fins}}
    f={name:"yellow_tang",sp:sp,size:1#,speed:sp.speed,renderPose:{x:900#,y:400#,z:.7,heading:.35,pitch:0#,phase:0#,finPhase:0#}}
    previous=invalid : varied=false
    for tick=0 to 119
        f.renderPose.phase=tick*6.283185307/60#
        screen.angles=[] : screen.sources=[] : screen.opacity=[] : ReefDrawFish(r,s,a,f)
        if screen.angles.Count()<>18 then print "FAIL missing body curve or appendage" : return
        if screen.sources[16]<>"tail" or screen.sources[17]<>"fin" then print "FAIL duplicate appendages in yaw blend" : return
        if screen.opacity[0]<>255 or screen.opacity[8]<=0 or screen.opacity[8]>=255 then print "FAIL opaque body base/yaw interpolation" : return
        if Abs(screen.angles[1]-screen.angles[6])>.5 then varied=true
        for band=0 to 17
            if Abs(screen.angles[band])>12.601 then print "FAIL bend exceeds pitch clearance" : return
            if previous<>invalid
                if Abs(screen.angles[band]-previous[band])>.9 then print "FAIL body curve jumps" : return
            end if
        end for
        previous=screen.angles
        if f.swimPose.heading<>.35 or f.swimPose.y<>400# then print "FAIL body curve changes physical pose" : return
    end for
    if not varied then print "FAIL fish is still a rigid rocking card" : return
    if Abs(ReefBodyWave(0#,.4,4#))>.000001 then print "FAIL head not anchored" : return
    if ReefBodyWave(.25,0#,4#)*ReefBodyWave(.75,0#,4#)>=0# then print "FAIL no S curve" : return
    if Abs(ReefBodyWave(.6,.7,4#)+ReefBodyWave(.6,.7+3.141592654#,4#))>.000001 then print "FAIL no inverse S curve" : return
    for i=1 to 99
        u=i/100# : slope=(ReefBodyWave(u+.001,.7,4#)-ReefBodyWave(u-.001,.7,4#))/.002
        if Abs(slope-ReefBodyWaveSlope(u,.7,4#))>.02 then print "FAIL detached tangent" : return
    end for
    print "PASS anchored head, traveling S/inverse-S body curve, smooth independent section tangents and attached fin/tail motion within the collision envelope"
end sub
function SwimCapture(x as integer,y as integer,angle as float,sx as float,sy as float,source as dynamic,tint as integer) as boolean
    m.angles.Push(angle) : m.sources.Push(source) : m.opacity.Push(tint and 255)
    return true
end function
