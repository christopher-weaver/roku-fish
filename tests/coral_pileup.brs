' Reproduce three fish pinned together in front of the white coral crown.
sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occ=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    s=ReefWorld(ReefValidateSettings({density:"Low"}),species,occ,47831)
    s.clam.enabled=false
    while s.fish.Count()>3
        s.fish.Pop()
    end while
    names=["copperband_butterflyfish","mandarin_dragonet","banggai_cardinalfish"]
    for i=0 to 2
        f=s.fish[i] : f.name=names[i] : f.sp=species[names[i]] : f.size=1#
        f.x=650# : f.y=450# : f.z=.94
        f.route=[] : f.routeIndex=0 : f.routeCheckAt=0# : f.duration=180#
        f.tx=1800# : f.ty=450# : f.tz=.94
        f.heading=0# : f.speed=0# : f.speedAcceleration=0#
        f.vx=0# : f.vy=0# : f.vz=0# : f.yawVelocity=0# : f.yawAcceleration=0#
        f.progressTime=0# : f.recoveryCount=0 : f.blockedTime=0# : f.state="Cruising"
        ReefFishBounds(f)
    end for
    a=s.fish[0] : left=s.fish[1] : right=s.fish[2]
    left.x=a.x-a.bodyBounds.radius-left.bodyBounds.radius-4#-.0099999#
    right.x=a.x+a.bodyBounds.radius+right.bodyBounds.radius+4#+.0099999#
    right.heading=3.141592654# : right.tx=220#
    starts=[] : metrics=[]
    for i=0 to 2
        f=s.fish[i] : ReefSavePose(f)
        if ReefCoralBlocked(s,f,f,f) or ReefFishBlocked(s,f,f,f,false) then print "FAIL unsafe coral pileup fixture" : return
        starts.Push({x:f.x,y:f.y,z:f.z})
        metrics.Push({travel:0#,still:0#,maxStill:0#,progress:0#})
    end for
    ' A trapped middle fish must have a pure vertical recovery option.
    if not ReefLocalManeuver(s,a) then print "FAIL no escape between two contact neighbors" : return
    if Abs(a.tx-a.x)>.000001 or Abs(a.tz-a.z)>.000001 then print "FAIL contact escape is not vertical" : return
    for tick=1 to 450
        ReefStep(s,1#/30#)
        for i=0 to 2
            f=s.fish[i] : metric=metrics[i] : start=starts[i]
            fromPose={x:f.previousX,y:f.previousY,z:f.previousZ}
            distance=Sqr((f.x-fromPose.x)^2+(f.y-fromPose.y)^2+((f.z-fromPose.z)*800#)^2)
            if distance>f.sp.speed*1.3*1.18/30#*1.1 then print "FAIL pileup escape teleports" : return
            if ReefCoralBlocked(s,f,fromPose,f) or ReefFishBlocked(s,f,fromPose,f) then print "FAIL pileup escape swept collision" : return
            for sample=0 to 4
                pose=ReefDisplayPose(f,sample/4#)
                if ReefCoralBlocked(s,f,pose,pose) then print "FAIL interpolated escape enters reef" : return
                for j=0 to 2
                    if j<>i
                        o=s.fish[j] : otherPose=ReefDisplayPose(o,sample/4#)
                        otherPose.sp=o.sp : otherPose.size=o.size
                        if ReefFishPairBlocked(f,pose,pose,otherPose,false) then print "FAIL interpolated escape enters another fish" : return
                    end if
                end for
            end for
            metric.travel=metric.travel+distance
            if distance>=.05 then metric.still=0# else metric.still=metric.still+1#/30#
            metric.maxStill=ReefMax(metric.maxStill,metric.still)
            metric.progress=ReefMax(metric.progress,Sqr((f.x-start.x)^2+(f.y-start.y)^2+((f.z-start.z)*800#)^2))
        end for
    end for
    for i=0 to 2
        metric=metrics[i]
        print "PILEUP ";s.fish[i].name;" travel=";metric.travel;" displacement=";metric.progress;" maxStationary=";metric.maxStill
        if metric.progress<65# or metric.maxStill>3# then print "FAIL trapped fish did not resume swimming" : return
    end for
    print "PASS all three reported species leave the coral pileup within 15 seconds with swept and interpolated reef/fish clearance"
end sub
