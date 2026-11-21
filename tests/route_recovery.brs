sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occ=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    starts=[[400#,630#,.12],[1230#,790#,.94],[1780#,630#,.94]]
    goals=[[1230#,630#,.94],[650#,440#,.12],[400#,630#,.12]]
    for encounter=0 to 2
        s=ReefWorld(ReefValidateSettings({density:"Low"}),species,occ,730+encounter)
    s.clam.enabled=false
        while s.fish.Count()>1
            s.fish.Pop()
        end while
        f=s.fish[0] : nodes=s.navigation.nodes
        start=invalid : goal=invalid
        for i=0 to nodes.Count()-1
            node=nodes[i]
            if node.x=starts[encounter][0] and node.y=starts[encounter][1] and Abs(node.z-starts[encounter][2])<.001 then start=i
            if node.x=goals[encounter][0] and node.y=goals[encounter][1] and Abs(node.z-goals[encounter][2])<.001 then goal=i
        end for
        if start=invalid or goal=invalid then print "FAIL recovery fixture has no safe endpoints ";encounter : return
        first=nodes[start] : last=nodes[goal]
        f.x=first.x : f.y=first.y : f.z=first.z
        if ReefCoralBlocked(s,f,f,f) then print "FAIL recovery start inside reef" : return
        f.tx=last.x : f.ty=last.y : f.tz=last.z
        f.route=[goal] : f.routeIndex=0 : f.routeCheckAt=0# : f.duration=180#
        f.heading=ReefAngle(f.tx-f.x,(f.tz-f.z)*800#) : f.speed=0# : f.vx=0# : f.vy=0# : f.vz=0#
        f.progressTime=5.99 : f.progressX=f.x : f.progressY=f.y : f.progressZ=f.z : f.recoveryCount=0
        f.state="Reef exploring" : ReefSavePose(f) : progress=0#
        for tick=0 to 449
            x=f.x : y=f.y : z=f.z
            ReefAdvance(s,1#/30#)
            distance=Sqr((f.x-x)^2+(f.y-y)^2+((f.z-z)*800#)^2)
            if distance>f.sp.speed*1.3*1.18/30#*1.1 then print "FAIL recovery teleports" : return
            if ReefCoralBlocked(s,f,f,f) then print "FAIL recovery crosses reef or floor" : return
            progress=ReefMax(progress,Sqr((f.x-first.x)^2+(f.y-first.y)^2+((f.z-first.z)*800#)^2))
        end for
        if f.recoveryCount<1 or progress<80# then print "FAIL stalled route not recovered ";encounter;progress;f.recoveryCount : return
        print "PASS stalled reef route ";encounter;" recovers into clear water, progress=";progress;" without teleport or reef/floor contact"
    end for
    s=ReefWorld(ReefValidateSettings({density:"Low"}),species,occ,730)
    s.clam.enabled=false
    while s.fish.Count()>1
        s.fish.Pop()
    end while
    f=s.fish[0] : f.x=900# : f.y=400# : f.z=.94
    f.tx=900# : f.ty=330# : f.tz=.94 : f.route=[]
    f.maneuverUntil=12# : f.recoveryUntil=12# : f.duration=12#
    f.state="Maneuvering" : f.stateTime=0# : f.speed=f.sp.speed*.4
    f.vx=0# : f.vy=0# : f.vz=0# : ReefSavePose(f)
    for tick=1 to 90
        ReefAdvance(s,1#/30#)
        if ReefCoralBlocked(s,f,f,f) then print "FAIL vertical recovery crosses reef" : return
    end for
    if f.y>380# or Abs(f.x-900#)>1# then print "FAIL vertical recovery loses propulsion";f.x;f.y : return
    print "PASS pure vertical recovery retains propulsion and follows its clear segment"
end sub
