sub ReefChooseTarget(s as object, f as object)
    f.stateTime = 0#
    r = ReefRandom(s)
    f.duration = ReefRange(s, 10, 30)
    f.tx = ReefRange(s, 220, 1820)
    f.ty = ReefRange(s, 180, 790)
    f.tz = ReefRange(s, 0.12, 0.94)
    f.state = "Cruising"
    if r < 0.28 then f.state = "Exploring"
    if r < 0.13
        f.state = "Hovering"
        f.tx = f.x + ReefRange(s, -35, 35)
        f.ty = f.y + ReefRange(s, -20, 20)
        f.tz = f.z
        f.duration = ReefRange(s, 4, 9)
    end if
    if f.name = "royal_gramma" and r > 0.72
        f.state = "Hiding"
        f.tx = 1600 : f.ty = 700 : f.tz = 0.28
    end if
    if f.name = "ocellaris_clownfish" and r < 0.78
        f.tx = ReefRange(s, 280, 620)
        f.ty = ReefRange(s, 620, 830)
        f.tz = ReefRange(s, 0.83, 0.97)
        f.state = "Exploring"
    end if
    if f.schooling then f.state = "Schooling"
end sub

sub ReefFishStep(s as object, f as object, dt as double)
    f.stateTime = f.stateTime + dt
    dx = f.tx - f.x : dy = f.ty - f.y : dz = (f.tz - f.z) * 800
    if f.stateTime > f.duration or (dx * dx + dy * dy + dz * dz < 2500 and f.state <> "Hovering")
        ReefChooseTarget(s, f)
        dx = f.tx - f.x : dy = f.ty - f.y : dz = (f.tz - f.z) * 800
    end if
    neighbors = ReefNeighbors(s, f)
    dx = dx * 0.4 + neighbors.x : dy = dy * 0.4 + neighbors.y : dz = dz * 0.4 + neighbors.z
    f.wander = ReefWrap(f.wander + dt * 0.17, 6.283185307)
    dx = dx + Cos(f.wander) * 16
    dz = dz + Sin(f.wander * 1.31) * 18
    ' Soft walls begin far enough away to allow a full, speed-limited arc turn.
    wall = false
    if f.x < 240 then dx = dx + (240 - f.x) * 4 : wall = true
    if f.x > 1808 then dx = dx - (f.x - 1808) * 4 : wall = true
    if f.z < 0.18 then dz = dz + (0.18 - f.z) * 2600 : wall = true
    if f.z > 0.88 then dz = dz - (f.z - 0.88) * 2600 : wall = true
    if f.y < 180 then dy = dy + (180 - f.y) * 5
    if f.y > 820 then dy = dy - (f.y - 820) * 5
    probe = {x:f.x + f.vx * 2, y:f.y + f.vy * 2, z:f.z + f.vz * 2}
    avoiding = ReefCoralBlocked(s, f, f, probe)
    if avoiding
        ' Begin a gradual arc and ascent before the footprint reaches the reef.
        dy = dy - 260
        closest = 0.48
        if Abs(f.z - 0.78) < Abs(f.z - 0.48) then closest = 0.78
        if f.z < closest
            dz = dz - 240
        else
            dz = dz + 240
        end if
        f.ty = ReefClamp(f.y - 120, 180, 700)
        wall = true
    end if
    desired = ReefAngle(dx, dz)
    turn = ReefAngleDelta(f.heading, desired)
    targetYawVelocity = ReefClamp(turn * 1.8, -f.turnRate, f.turnRate)
    f.yawVelocity = f.yawVelocity + ReefClamp(targetYawVelocity - f.yawVelocity, -1.4 * dt, 1.4 * dt)
    f.heading = ReefWrap(f.heading + f.yawVelocity * dt, 6.283185307)
    desiredSpeed = f.sp.speed * s.motion
    if f.state = "Hovering" then desiredSpeed = desiredSpeed * 0.12
    if Abs(turn) > 1.1 then desiredSpeed = desiredSpeed * 0.55
    if neighbors.alarm then desiredSpeed = desiredSpeed * 1.18
    ' Never exceed the configured acceleration, even when night / settings change.
    if (f.x < 120 and Cos(f.heading) < 0) or (f.x > 1928 and Cos(f.heading) > 0) or (f.z < 0.08 and Sin(f.heading) < 0) or (f.z > 0.94 and Sin(f.heading) > 0) then desiredSpeed = 0
    if avoiding then desiredSpeed = desiredSpeed * 0.55
    f.targetSpeed = desiredSpeed
    f.speed = f.speed + ReefClamp(desiredSpeed - f.speed, -f.acceleration * dt, f.acceleration * dt)
    f.desiredVx = Cos(f.heading) * f.speed
    f.desiredVz = Sin(f.heading) * f.speed / 800
    f.desiredVy = ReefClamp(dy * 0.08, -f.speed * 0.22, f.speed * 0.22)
    f.vx = f.desiredVx : f.vz = f.desiredVz
    f.vy = f.vy + ReefClamp(f.desiredVy - f.vy, -8 * dt, 8 * dt)
    candidate = {x:f.x + f.vx * dt, y:f.y + f.vy * dt, z:f.z + f.vz * dt}
    if ReefCoralBlocked(s, f, f, candidate)
        ' Slide along the plane instead of letting any part of the fish enter it.
        candidate.z = f.z
        f.vz = 0
        if ReefCoralBlocked(s, f, f, candidate)
            candidate.x = f.x
            f.vx = 0
            if ReefCoralBlocked(s, f, f, candidate)
                candidate.y = f.y
                f.vy = 0
            end if
        end if
        wall = true
    end if
    f.x = candidate.x : f.y = candidate.y : f.z = candidate.z
    ' Emergency wall brake is continuous (no wrapping / teleporting).
    f.pitch = f.pitch + (ReefClamp(-f.vy / 35, -0.22, 0.22) - f.pitch) * dt * 2
    f.phase = ReefWrap(f.phase + dt * f.sp.beat * 6.283185307 * (0.3 + f.speed / f.sp.speed * 0.7), 6.283185307)
    finBeat = 1.5
    if f.sp.finBeat <> invalid then finBeat = f.sp.finBeat
    f.finPhase = ReefWrap(f.finPhase + dt * finBeat * f.finRate * 6.283185307 * (0.7 + f.speed / f.sp.speed * 0.3), 6.283185307)
    if wall and f.state <> "Hiding" then f.state = "Avoidance"
    if not wall and Abs(turn) > 0.7 and f.state = "Cruising" then f.state = "Turning"
end sub
