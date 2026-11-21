sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occ=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    world=ReefWorld(ReefValidateSettings(invalid),species,occ,47831)
    lateral=0 : nearHome=0
    for i=0 to world.fish.Count()-1
        f=world.fish[i]
        if Abs(Cos(f.heading))<.95 then print "FAIL fish starts staring" : return
        ReefPlanRoute(world,f)
        if f.route.Count()=0
            if Abs(f.tx-f.x)>200 then lateral=lateral+1
            if Abs(f.tz-f.homeZ)<.25 then nearHome=nearHome+1
        end if
        if f.route.Count()>0
            goal=world.navigation.nodes[f.route[f.route.Count()-1]]
            if Abs(goal.x-f.x)>200 then lateral=lateral+1
            if Abs(goal.z-f.homeZ)<.25 then nearHome=nearHome+1
        end if
    end for
    if lateral<6 or nearHome<6 then print "FAIL insufficient lateral/home-depth routes ";lateral;nearHome : return
    print "PASS profile-facing starts and predominantly lateral, home-depth goals"
    while world.fish.Count()>1
        world.fish.Pop()
    end while
    world.occupancy=invalid : world.navigation=invalid
    f=world.fish[0] : f.state="Hovering" : f.stateTime=0# : f.duration=100# : f.route=[]
    f.heading=.1 : f.yawVelocity=0# : f.yawAcceleration=0#
    f.tx=f.x+15# : f.ty=f.y : f.tz=f.z
    for tick=0 to 89
        ReefStep(world,1#/30#)
        if Abs(Cos(f.heading))<.8 then print "FAIL hovering fish stares at viewer" : return
    end for
    print "PASS hovering fish retain a side-facing pose"
    f.x=900# : f.y=300# : f.z=.5 : f.heading=0# : f.pitch=0#
    f.vx=0# : f.vy=0# : f.vz=0# : f.speed=0# : f.yawVelocity=0# : f.yawAcceleration=0#
    f.state="Cruising" : f.stateTime=0# : f.duration=1000# : f.tx=900# : f.ty=100# : f.tz=.5
    for tick=0 to 59
        ReefStep(world,1#/30#)
        if Abs(ReefAngleDelta(0#,f.heading))>.05 then print "FAIL vertical route points at viewer" : return
    end for
    print "PASS vertical escape keeps a steady swimming profile"
end sub
