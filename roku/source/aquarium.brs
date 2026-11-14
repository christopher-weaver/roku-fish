function ReefWorld(settings as object, species as object, occupancy as dynamic, seed as integer) as object
    s = { rng: seed * 1#, fish: [], settings: settings, species: species, occupancy: occupancy, time: 0#, camera: 64#, accumulator: 0#, renderAlpha: 0#, effects: [], quality: 1#, fps: 60#, renderFps: 60#, pacingPressure: 0#, clockText: "", frames: 0, sampleFrames: 0, sampleTime: 0#, adaptation: 0#, lastHour: -1#, lighting: [0#,0#,0#,0#], tint: &hFFFFFFFF }
    if s.rng <= 0 then s.rng = 1#
    s.cfg = ParseJson(ReadAsciiFile("pkg:/scenes/tank.json"))
    if s.cfg = invalid then s.cfg = {speciesOrder: species.Keys(), populations: {Low:12,Medium:18,High:24}, occlusionDepths:[0.48,0.78], dawn:7#,dusk:18.5}
    s.camera = ReefCamera(0#, settings.camera, s.cfg.camera)
    names = s.cfg.speciesOrder
    count = s.cfg.populations[settings.density]
    if settings.quality = "Performance"
        s.quality = 0.5 : s.renderFps = 30#
    end if
    s.motion = 1#
    if settings.movement = "Calm" then s.motion = 0.65
    if settings.movement = "Active" then s.motion = 1.3
    for i = 0 to count - 1
        index = i mod names.Count()
        if i >= 12 and i mod 2 = 0 then index = names.Count() - 1
        name = names[index]
        sp = species[name]
        if sp <> invalid
            f = { id: i, name: name, sp: sp, x: ReefRange(s, 150, 1900), y: ReefRange(s, 180, 780), z: ReefRange(s, 0.16, 0.95), tx: 1024#, ty: 460#, tz: 0.5, vx: 0#, vy: 0#, vz: 0#, desiredVx: 0#, desiredVy: 0#, desiredVz: 0#, heading: ReefRange(s, -3.14, 3.14), pitch: 0#, speed: 0#, phase: ReefRange(s, 0, 6.283), size: ReefRange(s, 0.86, 1.12), state: "Cruising", stateTime: 0#, duration: ReefRange(s, 8, 22), turnRate: ReefRange(s, 0.32, 0.55), acceleration: 19#, targetSpeed: sp.speed, wander: ReefRange(s, 0, 6.283), schooling: sp.school }
            if name = "ocellaris_clownfish" then f.x = 410 + i * 9 : f.y = 740 : f.z = 0.85
            f.speed = sp.speed * 0.6
            f.yawVelocity = 0#
            f.finPhase = ReefRange(s, 0, 6.283185307)
            f.finRate = ReefRange(s, 0.85, 1.15)
            ReefSafeSpawn(s, f)
            ReefChooseTarget(s, f)
            ReefSavePose(f)
            s.fish.Push(f)
        end if
    end for
    ReefEffectsInit(s)
    return s
end function

sub ReefStep(s as object, elapsed as double)
    dt = ReefClamp(elapsed, 0, 0.1)
    s.time = s.time + dt
    ' Bound the phase clock daily; no loss of per-frame precision in indefinite sessions.
    if s.time > 86400# then s.time = s.time - 86400#
    s.camera = ReefCamera(s.time, s.settings.camera, s.cfg.camera)
    ' Roku shares one ifEnum cursor per object. Never enumerate the fish array across
    ' a call that also inspects that array (the neighbor scan used to stop this after fish 0).
    for fishIndex = 0 to s.fish.Count() - 1
        f = s.fish[fishIndex]
        ReefSavePose(f)
        ReefFishStep(s, f, dt)
    end for
    ReefEffectsStep(s, dt)
end sub

sub ReefSavePose(f as object)
    f.previousX = f.x : f.previousY = f.y : f.previousZ = f.z
    f.previousHeading = f.heading : f.previousPitch = f.pitch
    f.previousPhase = f.phase : f.previousFinPhase = f.finPhase
end sub

' Fixed simulation ticks and interpolation keep motion independent of frame/vsync jitter.
sub ReefAdvance(s as object, elapsed as double)
    tick = 1# / 30#
    s.accumulator = s.accumulator + ReefClamp(elapsed, 0, 0.1)
    while s.accumulator + 0.000000001# >= tick
        ReefStep(s, tick)
        s.accumulator = s.accumulator - tick
    end while
    s.accumulator = ReefClamp(s.accumulator, 0, tick)
    s.renderAlpha = s.accumulator / tick
    s.camera = ReefCamera(s.time - tick + s.accumulator, s.settings.camera, s.cfg.camera)
end sub
