sub Main()
    prefs=ReefValidateSettings({density:"Low"})
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    world=ReefWorld(prefs,species,invalid,730)
    while world.fish.Count()>1
        world.fish.Pop()
    end while
    f=world.fish[0] : f.route=[] : f.duration=1000#
    f.x=1024# : f.y=400# : f.z=0.5 : f.heading=0#
    f.tx=300# : f.ty=420# : f.tz=0.8
    f.yawVelocity=0# : f.yawAcceleration=0#
    for i=0 to 359
        if i=120 then f.tx=1750# : f.tz=0.2
        if i=240 then f.tx=350# : f.tz=0.8
        oldVelocity=f.yawVelocity : oldAcceleration=f.yawAcceleration
        ReefStep(world,1#/30#)
        if Abs(f.yawVelocity-oldVelocity)>0.65/30+0.00001 then print "FAIL angular acceleration" : return
        if Abs(f.yawAcceleration-oldAcceleration)>1.2/30+0.00001 then print "FAIL angular jerk" : return
        if Abs(f.yawVelocity)>f.turnRate+0.000001 then print "FAIL turn speed" : return
        a=ReefDisplayPose(f,0#) : b=ReefDisplayPose(f,1#)
        if Abs(ReefAngleDelta(a.heading,f.previousHeading))>0.000001 or Abs(ReefAngleDelta(b.heading,f.heading))>0.000001 then print "FAIL cubic endpoints" : return
        epsilon=0.0001
        first=ReefDisplayPose(f,epsilon) : last=ReefDisplayPose(f,1#-epsilon)
        initialRate=ReefAngleDelta(a.heading,first.heading)*30/epsilon
        finalRate=ReefAngleDelta(last.heading,b.heading)*30/epsilon
        if Abs(initialRate-f.previousYawVelocity)>0.001 or Abs(finalRate-f.yawVelocity)>0.001 then print "FAIL continuous angular velocity" : return
    end for
    print "PASS opposite target changes retain bounded turn speed, acceleration and jerk; cubic display headings preserve endpoint velocities"
    for each name in species
        sp=species[name]
        maxJump=0#
        for i=0 to sp.yawCount-1
            boundary=(i+0.5)*6.283185307/sp.yawCount
            left=ReefFishView(boundary-0.000001,sp)
            right=ReefFishView(boundary+0.000001,sp)
            if Abs(left.width-right.width)>0.001 then print "FAIL width jump ";name : return
        end for
    end for
    print "PASS all six fish retain continuous silhouette widths across every yaw index boundary"
    for sign=1 to 1
        for i=0 to 30
            angle=i*0.8-12#
            t=ReefFishTransform(950.375,610.625,sign*0.91,0.91,angle)
            c=Cos(t.angle/57.295779513#) : sn=Sin(t.angle/57.295779513#)
            x=t.x+4096*(c*t.sx+sn*t.sy)
            y=t.y+4096*(c*t.sy-sn*t.sx)
            if Abs(x-950.375)>0.002 or Abs(y-610.625)>0.002 then print "FAIL fractional fish center ";x;y;angle;t : return
        end for
    end for
    print "PASS positive-scale pitched fish retain their fractional center"
end sub
