sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occ=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    world=ReefWorld(ReefValidateSettings(invalid),species,occ,47831)
    lateral=0 : nearHome=0
    for i=0 to world.fish.Count()-1
        f=world.fish[i]
        if Abs(Cos(f.heading))<.95 then print "FAIL fish starts staring" : return
        ReefPlanRoute(world,f)
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
end sub
