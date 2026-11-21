sub ReefEffectsInit(s as object)
    ' Fixed pools: no accumulation, texture loads, or spawning allocations at runtime.
    for i = 0 to 71
        bubble = i >= 48
        s.effects.Push({ x: ReefRange(s, 0, 2048), y: ReefRange(s, 0, 1080), z: ReefRandom(s), phase: ReefRange(s, 0, 6.283), speed: ReefRange(s, 2, 9), bubble: bubble, age: ReefRange(s, 0, 12), active: i })
    end for
    for each e in s.effects
        e.previousX = e.x : e.previousY = e.y
    end for
end sub

sub ReefEffectsStep(s as object, dt as double)
    for each e in s.effects
        e.previousX = e.x : e.previousY = e.y
        e.recycled = false
        e.phase = ReefWrap(e.phase + dt * 0.4, 6.283185307)
        e.x = e.x + (2 + e.z * 5 + Sin(e.phase) * 2) * dt
        if e.bubble
            e.age = e.age + dt
            e.y = e.y - (25 + e.speed * 3 + e.age * 0.4) * dt
            if e.y < 38
                e.y = 1040 + ReefRange(s, 0, 200)
                e.x = 1440 + ReefRange(s, -25, 25)
                e.age = 0
                e.recycled = true
            end if
        else
            e.y = e.y + e.speed * dt
            if e.y > 1090
                e.y = -10 : e.x = ReefRange(s, 0, 2048)
                e.recycled = true
            end if
        end if
        if e.x > 2058
            e.x = -10
            e.recycled = true
        end if
        if e.recycled
            e.previousX = e.x : e.previousY = e.y
        end if
    end for
end sub

' Returns dark-blue and warm-pink overlay alpha. Automatic thresholds are data-configurable.
function ReefLighting(hour as double, mode as string, dawn as double, dusk as double) as object
    day = 1# : warm = 0#
    if mode = "Sunset" then warm = 1
    if mode = "Dusk" then day = 0.52 : warm = 0.55
    if mode = "Moonlight" then day = 0.12
    if mode = "Night" then day = 0.06
    if mode = "Automatic"
        rise = ReefEase((hour - dawn) / 1.5)
        set = 1 - ReefEase((hour - dusk) / 1.5)
        day = 0.12 + 0.88 * rise * set
        warm = ReefClamp(1 - Abs(hour - (dusk + 0.6)) / 1.4, 0, 1)
    end if
    darkness=(1-day)*150
    if mode="Night" then darkness=205#
    return [day, warm, darkness, warm * 38]
end function

sub ReefLightingStep(s as object, hour as double, dt as double)
    target = ReefLighting(hour, s.settings.lighting, s.cfg.dawn, s.cfg.dusk)
    if s.frames = 0 then s.lighting = target
    for i = 0 to 3
        s.lighting[i] = s.lighting[i] + (target[i] - s.lighting[i]) * ReefClamp(dt / 20, 0, 1)
    end for
end sub

sub ReefQualitySample(s as object, seconds as double, frameCount as integer)
    if seconds <= 0 then return
    s.fps = frameCount / seconds
    if s.settings.quality <> "Auto" then return
    if s.renderFps = invalid then s.renderFps = 60#
    if s.pacingPressure = invalid then s.pacingPressure = 0#
    if s.renderFps = 60 and s.fps < 45
        s.pacingPressure = s.pacingPressure + seconds
        if s.pacingPressure >= 12
            ' Lock to an even 30Hz cadence rather than oscillating between frame caps.
            s.renderFps = 30#
            s.adaptation = 0#
        end if
    else
        s.pacingPressure = ReefMax(0#, s.pacingPressure - seconds)
    end if
    if s.fps < 25
        s.adaptation = s.adaptation + seconds
    else
        s.adaptation = ReefClamp(s.adaptation - seconds, 0, 60)
    end if
    if s.adaptation >= 12 then s.quality = ReefClamp(s.quality - 0.08, 0.3, 1) : s.adaptation = 6
    if s.fps > 29 and s.adaptation = 0 then s.quality = ReefClamp(s.quality + 0.02, 0.3, 1)
end sub

function ReefBubbleScale(z as double) as double
    ' 32px source rings yield 13-28px bubbles, versus the former 5-12px specks.
    return 0.42 + ReefClamp(z, 0, 1) * 0.45
end function

function ReefSurface(t as double) as object
    ' One phase drives both the moving surface and refracted sand highlights.
    phase = ReefWrap(ReefWrap(t, 8#) * 4#, 32#)
    first = Int(phase)
    return { first: first, second: (first + 1) mod 32, blend: phase - first }
end function

function ReefEffectPose(e as object, alpha as double) as object
    return {x:e.previousX + (e.x - e.previousX) * alpha, y:e.previousY + (e.y - e.previousY) * alpha}
end function

' Slow opening and closing with stationary holds at both ends.
function ReefClamOpening(time as double) as double
    q=ReefWrap(time+7#,47#)
    if q<8# or q>=27# then return 0#
    if q<13# then return ReefSmoother((q-8#)/5#)
    if q<22# then return 1#
    return 1#-ReefSmoother((q-22#)/5#)
end function

sub ReefClamInit(s as object)
    order=[0,1,2]
    for i=2 to 1 step -1
        j=Int(ReefRange(s,0,i+.99999)) : swap=order[i] : order[i]=order[j] : order[j]=swap
    end for
    s.clam={enabled:true,cycle:-1,event:0,released:false,order:order,nextId:s.fish.Count(),births:0,bubbles:[]}
    for i=0 to 11
        s.clam.bubbles.Push({born:0#-1000#,x:1080#,speed:45#+i*2#,phase:i*2.399963#,scale:.25+(i mod 4)*.07})
    end for
    s.bioluminescence=[]
    for i=0 to 23
        angle=i*2.399963#
        if i<12
            s.bioluminescence.Push({x:803#+Cos(angle)*86#,y:447#+Sin(angle)*77#,size:.35+(i mod 3)*.08,phase:angle})
        else
            s.bioluminescence.Push({x:1810#+Cos(angle)*69#,y:842#+Sin(angle)*32#,size:.38,phase:angle})
        end if
    end for
end sub

sub ReefClamStep(s as object)
    if s.clam=invalid then return
    c=s.clam
    if not c.enabled then return
    cycle=Int((s.time+7#)/47#) : q=ReefWrap(s.time+7#,47#)
    if cycle<>c.cycle
        c.cycle=cycle : c.event=c.order[cycle mod 3] : c.released=false
        if c.event=2 and (s.fish.Count()>=12 or c.births>=4) then c.event=0
    end if
    if q<16# or q>=22# or c.released then return
    if c.event=1
        for i=0 to c.bubbles.Count()-1
            e=c.bubbles[i] : e.born=s.time+i*.14 : e.x=1080#+ReefRange(s,-26#,26#)
        end for
        c.released=true
    else if c.event=2
        if ReefClamBaby(s) then c.released=true
    else
        c.released=true
    end if
end sub

function ReefClamBaby(s as object) as boolean
    if s.fish.Count()=0 then return false
    parent=s.fish[s.clam.births mod s.fish.Count()]
    f={} : f.Append(parent)
    f.id=s.clam.nextId : f.size=.34 : f.x=1080# : f.y=948# : f.z=.97
    f.homeZ=.94 : f.heading=0# : f.pitch=0# : f.yawVelocity=0# : f.yawAcceleration=0#
    f.speed=f.sp.speed*.30 : f.speedAcceleration=0# : f.acceleration=12#
    f.vx=0# : f.vy=0# : f.vz=0# : f.desiredVx=0# : f.desiredVy=0# : f.desiredVz=0#
    f.tx=1260# : f.ty=760# : f.tz=.94 : f.state="Exploring" : f.stateTime=0# : f.duration=12# : f.schooling=false
    f.route=[] : f.routeIndex=0 : f.routeCheckAt=0# : f.routeVisits=0
    f.probe={} : f.candidate={} : f.trafficProbe={}
    f.renderPose=invalid : f.swimPose=invalid : f.screenPose=invalid : f.renderView=invalid : f.bodyView=invalid
    f.phase=ReefRange(s,0,6.283185307#) : f.finPhase=ReefRange(s,0,6.283185307#)
    f.steeringHeading=0# : f.avoidance=0# : f.progressTime=0# : f.recoveryUntil=0# : f.recoveryCount=0
    if ReefCoralBlocked(s,f,f,f) or ReefFishBlocked(s,f,f,f,false) then return false
    f.progressX=f.x : f.progressY=f.y : f.progressZ=f.z
    ReefSavePose(f)
    s.fish.Push(f) : s.clam.births=s.clam.births+1 : s.clam.nextId=s.clam.nextId+1
    return true
end function
