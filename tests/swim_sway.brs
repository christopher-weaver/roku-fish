sub Main()
    sp=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))["yellow_tang"]
    body=[] : tails=[] : fins=[]
    for i=0 to sp.frames.Count()-1
        source="body:"+i.ToStr()
        body.Push({wholeSwim:true,normal:source,fractional:source,offsetX:.5,offsetY:.5})
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
    f={name:"yellow_tang",sp:sp,size:1#,speed:sp.speed,renderPose:{x:900#,y:400#,z:.7,heading:.35,pitch:.12,phase:0#,finPhase:0#}}
    ReefTailRigInit(sp)
    draws=0 : partial=0
    for tick=0 to 119
        f.renderPose.phase=tick*6.283185307/60#
        screen.angles=[] : screen.sources=[] : screen.opacity=[] : ReefDrawFish(r,s,a,f)
        count=screen.sources.Count() : draws=draws+count
        if count<4 or count>6 then print "FAIL whole body draw budget" : return
        if screen.sources[0]<>"tail" or screen.sources[count-1]<>"fin" then print "FAIL duplicate appendages" : return
        if screen.opacity[1]<>255 then print "FAIL missing opaque body base" : return
        for i=1 to count-2
            if Left(screen.sources[i],5)<>"body:" then print "FAIL fragmented body" : return
            if screen.angles[i]<>screen.angles[1] then print "FAIL body slices rotate independently" : return
            if screen.opacity[i]>0 and screen.opacity[i]<255 then partial=partial+1
        end for
        ' Verify the actual source-over weights, including byte alpha rounding.
        weights={}
        for i=1 to count-2
            alpha=screen.opacity[i]/255#
            for each key in weights.Keys()
                weights[key]=weights[key]*(1#-alpha)
            end for
            key=screen.sources[i]
            if weights[key]=invalid then weights[key]=0#
            weights[key]=weights[key]+alpha
        end for
        position=(Sin(f.swimPose.phase)+1#)*.5*(sp.poseCount-1)
        first=Int(position) : second=first+1
        if second>=sp.poseCount then second=first
        phase=position-first : yaw=f.bodyView.blend
        ids=[f.bodyView.first*sp.poseCount+first,f.bodyView.first*sp.poseCount+second,f.bodyView.second*sp.poseCount+first,f.bodyView.second*sp.poseCount+second]
        values=[(1#-yaw)*(1#-phase),(1#-yaw)*phase,yaw*(1#-phase),yaw*phase]
        wanted={}
        for i=0 to 3
            key="body:"+ids[i].ToStr()
            if wanted[key]=invalid then wanted[key]=0#
            wanted[key]=wanted[key]+values[i]
        end for
        for each key in wanted.Keys()
            actual=0#
            if weights[key]<>invalid then actual=weights[key]
            if Abs(actual-wanted[key])>.012 then print "FAIL nonlinear phase/yaw weights" : return
        end for
        for i=0 to count-1
            if Abs(screen.angles[i])>12.601 then print "FAIL pitch clearance" : return
        end for
        if Abs(f.swimPose.heading-.35)>.029 or f.swimPose.y<>400# or f.renderPose.heading<>.35 then print "FAIL changed physical pose or excessive head sway" : return
    end for
    if partial=0 then print "FAIL missing smooth yaw/phase blends" : return
    for turnSide=-1 to 1 step 2
        f.renderPose.yawVelocity=turnSide*.3
        screen.angles=[] : screen.sources=[] : screen.opacity=[] : ReefDrawFish(r,s,a,f)
        count=screen.sources.Count()
        if count>6 then print "FAIL C-turn exceeds body draw budget" : return
        if turnSide*r.waveTurn<.999 then print "FAIL C turn points opposite steering" : return
        for i=1 to count-2
            index=Val(Mid(screen.sources[i],6))
            if index<sp.turnOffset then print "FAIL full turn retains stiff neutral body" : return
        end for
    end for
    print "PASS signed left/right C-turn bodies retain four body submissions and attached appendages"
    print "PASS 120 frames use ";draws;" transforms: complete S/inverse-S body poses, shared pitch, opaque base, smooth yaw/phase blends, one attached tail and fin; no body slices"
end sub
function SwimCapture(x as integer,y as integer,angle as float,sx as float,sy as float,source as dynamic,tint as integer) as boolean
    m.angles.Push(angle) : m.sources.Push(source) : m.opacity.Push(tint and 255)
    return true
end function
