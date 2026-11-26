' Three minutes at the production 30 Hz tick, with the shipped scene and births.
sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occ=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    s=ReefWorld(ReefValidateSettings({density:"High"}),species,occ,47831)
    stats=[] : violations=0 : maxStuck=0# : stalls=0
    for tick=1 to 5400
        ReefStep(s,1#/30#)
        while stats.Count()<s.fish.Count()
            f=s.fish[stats.Count()]
            stats.Push({still:0#,maxStill:0#,travel:0#,windowX:f.x,windowY:f.y,windowZ:f.z,windows:0})
        end while
        for i=0 to s.fish.Count()-1
            f=s.fish[i] : metric=stats[i]
            distanceSquared=(f.x-f.previousX)^2+(f.y-f.previousY)^2+((f.z-f.previousZ)*800#)^2
            metric.travel=metric.travel+Sqr(distanceSquared)
            goal=(f.tx-f.x)^2+(f.ty-f.y)^2+((f.tz-f.z)*800#)^2
            if distanceSquared<.05^2 and f.emerging<>true and f.state<>"Hovering"
                metric.still=metric.still+1#/30#
            else
                metric.still=0#
            end if
            metric.maxStill=ReefMax(metric.maxStill,metric.still) : maxStuck=ReefMax(maxStuck,metric.still)
            if tick mod 180=0
                span=Sqr((f.x-metric.windowX)^2+(f.y-metric.windowY)^2+((f.z-metric.windowZ)*800#)^2)
                if f.emerging<>true and f.state<>"Hovering" and span<18#
                    stalls=stalls+1 : metric.windows=metric.windows+1
                    print "STALL ";FormatJson({time:s.time,id:f.id,name:f.name,x:f.x,y:f.y,z:f.z,span:span,still:metric.still,heading:f.heading,speed:f.speed,target:[f.tx,f.ty,f.tz],routeIndex:f.routeIndex,routeCount:f.route.Count(),state:f.state,recoveries:f.recoveryCount})
                end if
                metric.windowX=f.x : metric.windowY=f.y : metric.windowZ=f.z
            end if
        end for
        if tick mod 30=0
            for i=0 to s.fish.Count()-1
                f=s.fish[i]
                if ReefCoralBlocked(s,f,f,f) then violations=violations+1
                if ReefFishBlocked(s,f,f,f,false) then violations=violations+1
            end for
        end if
        if tick mod 300=0 then print "PROGRESS seconds=";tick/30;" fish=";s.fish.Count();" stall windows=";stalls;" max stationary=";maxStuck
    end for
    for i=0 to s.fish.Count()-1
        print "FISH ";FormatJson({id:s.fish[i].id,name:s.fish[i].name,travel:stats[i].travel,maxStill:stats[i].maxStill,stalls:stats[i].windows})
    end for
    print "THREE MINUTE RESULT seconds=180 ticks=5400 stalls=";stalls;" maxStationary=";maxStuck;" violations=";violations
    if violations>0 or maxStuck>3#
        print "FAIL sustained movement or swept collision safety"
    else
        print "PASS three-minute production movement and collision regression"
    end if
end sub
