sub ReefChooseTarget(s as object, f as object)
    f.stateTime = 0#
    f.route = [] : f.routeIndex = 0
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
    if f.schooling then f.state = "Schooling"
    if s.navigation <> invalid and f.state <> "Hovering" then ReefPlanRoute(s, f)

end sub

sub ReefFishStep(s as object, f as object, dt as double)
    f.stateTime = f.stateTime + dt
    ReefFollowRoute(s, f)
    dx = f.tx - f.x : dy = f.ty - f.y : dz = (f.tz - f.z) * 800
    if (f.route.Count() = 0 and f.stateTime > f.duration) or (dx * dx + dy * dy + dz * dz < 3600 and f.state <> "Hovering" and f.routeIndex >= f.route.Count() - 1)
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
    if f.y < 100 then dy = dy + (100 - f.y) * 5
    if f.y > 820 then dy = dy - (f.y - 820) * 5
    probe = {x:f.x + f.vx * 5, y:f.y + f.vy * 5, z:f.z + f.vz * 5}
    avoiding = ReefCoralBlocked(s, f, f, probe)
    pressure = 0#
    if avoiding then pressure = 1#
    f.avoidance = f.avoidance + (pressure - f.avoidance) * ReefClamp(dt * 2, 0, 1)
    ' Follow clearance-tested routes around each formation instead of always
    ' repelling from two depth planes and forcing every fish upward.
    if avoiding
        wall = true
        if f.route.Count() > 0
            waypoint = s.navigation.nodes[f.route[f.routeIndex]]
            dx = (waypoint.x - f.x) * 0.65
            dy = (waypoint.y - f.y) * 0.65
            dz = (waypoint.z - f.z) * 800 * 0.65
        end if
    end if
    desired = ReefAngle(dx, dz)
    turn = ReefAngleDelta(f.heading, desired)
    ' Damped steering with bounded angular acceleration and jerk.
    ' An opposite goal cannot instantly reverse the turn direction.
    targetYawVelocity = ReefClamp(turn * 1.15, -f.turnRate, f.turnRate)
    desiredYawAcceleration = ReefClamp((targetYawVelocity - f.yawVelocity) * 2.8, -0.65, 0.65)
    f.yawAcceleration = f.yawAcceleration + ReefClamp(desiredYawAcceleration - f.yawAcceleration, -1.2 * dt, 1.2 * dt)
    f.yawVelocity = ReefClamp(f.yawVelocity + f.yawAcceleration * dt, -f.turnRate, f.turnRate)
    f.heading = ReefWrap(f.heading + f.yawVelocity * dt, 6.283185307)
    desiredSpeed = f.sp.speed * s.motion
    if f.state = "Hovering" then desiredSpeed = desiredSpeed * 0.12
    horizontalDistance = Sqr(dx * dx + dz * dz)
    desiredSpeed = desiredSpeed * ReefClamp(horizontalDistance / (Abs(dy) * 1.3 + 40), 0.06, 1)
    desiredSpeed = desiredSpeed * (1 - 0.45 * ReefEase((Abs(turn) - 0.6) / 1.2))
    if neighbors.alarm then desiredSpeed = desiredSpeed * 1.18
    ' Never exceed the configured acceleration, even when night / settings change.
    if (f.x < 120 and Cos(f.heading) < 0) or (f.x > 1928 and Cos(f.heading) > 0) or (f.z < 0.08 and Sin(f.heading) < 0) or (f.z > 0.94 and Sin(f.heading) > 0) then desiredSpeed = 0
    desiredSpeed = desiredSpeed * (1 - f.avoidance)^2
    f.targetSpeed = desiredSpeed
    desiredAcceleration = ReefClamp((desiredSpeed - f.speed) * 2, -f.acceleration, f.acceleration)
    f.speedAcceleration = f.speedAcceleration + ReefClamp(desiredAcceleration - f.speedAcceleration, -38 * dt, 38 * dt)
    f.speed = ReefClamp(f.speed + f.speedAcceleration * dt, 0, f.sp.speed * 1.3 * 1.18)
    f.desiredVx = Cos(f.heading) * f.speed
    f.desiredVz = Sin(f.heading) * f.speed / 800
    f.desiredVy = ReefClamp(dy * 0.15, -f.sp.speed * s.motion * 0.33, f.sp.speed * s.motion * 0.33)
    f.vx = f.desiredVx : f.vz = f.desiredVz
    f.vy = f.vy + ReefClamp(f.desiredVy - f.vy, -8 * dt, 8 * dt)
    candidate = {x:f.x + f.vx * dt, y:f.y + f.vy * dt, z:f.z + f.vz * dt}
    if ReefCoralBlocked(s, f, f, candidate)
        ' Final swept-volume safety guard; normal motion is planned around the reef.
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
    if wall and f.state <> "Hiding" and f.state <> "Hovering" then f.state = "Avoidance"
    if not wall and Abs(turn) > 0.7 and f.state = "Cruising" then f.state = "Turning"
end sub


' Destinations are linked by a small offline clearance graph. All fish visits
' are indexed: Roku shares ifEnum cursors between nested behavior calls.
sub ReefPlanRoute(s as object, f as object)
    nodes = s.navigation.nodes
    if nodes.Count() = 0 then return
    start = -1 : best = 1e12
    ' Nearest reachable node, not just the nearest point on the other side of rock.
    for index = 0 to nodes.Count() - 1
        node = nodes[index]
        distance = (node.x-f.x)^2 + (node.y-f.y)^2 + ((node.z-f.z)*800)^2
        if distance < best
            if not ReefCoralBlocked(s, f, f, node) then best = distance : start = index
        end if
    end for
    if start < 0 then return
    wantRear = ReefRandom(s) < 0.32
    if f.name = "royal_gramma" then wantRear = ReefRandom(s) < 0.65
    if f.name = "ocellaris_clownfish" then wantRear = ReefRandom(s) < 0.12
    wantedZ = 0.94
    if wantRear then wantedZ = 0.12
    wantedX = ReefRange(s, 220, 1810) : wantedY = ReefRange(s, 280, 780)
    if f.name = "ocellaris_clownfish" then wantedX = ReefRange(s, 900, 1350) : wantedY = ReefRange(s, 650, 800)
    goal = start : best = 1e12
    for index = 0 to nodes.Count() - 1
        node = nodes[index]
        distance = (node.x-wantedX)^2 + (node.y-wantedY)^2 + ((node.z-wantedZ)*1800)^2
        if distance < best then best = distance : goal = index
    end for
    queue = [start] : visited = {} : previous = {}
    visited[start.ToStr()] = true : head = 0
    while head < queue.Count()
        index = queue[head] : head = head + 1
        if index = goal then exit while
        edges = nodes[index].edges
        for edgeIndex = 0 to edges.Count() - 1
            nextIndex = edges[edgeIndex] : key = nextIndex.ToStr()
            if not visited.DoesExist(key)
                visited[key] = true : previous[key] = index : queue.Push(nextIndex)
            end if
        end for
    end while
    reverse = [goal] : index = goal
    while index <> start
        index = previous[index.ToStr()]
        if index = invalid then return
        reverse.Push(index)
    end while
    f.route = []
    for index = reverse.Count() - 1 to 0 step -1
        f.route.Push(reverse[index])
    end for
    f.routeIndex = 0 : f.routeVisits = f.routeVisits + 1
    f.state = "Reef exploring"
    if wantRear then f.state = "Reef sheltering"
    f.duration = 180#
    ReefFollowRoute(s, f)
end sub

sub ReefFollowRoute(s as object, f as object)
    if f.route.Count() = 0 then return
    nodes = s.navigation.nodes
    node = nodes[f.route[f.routeIndex]]
    distance = (node.x-f.x)^2 + (node.y-f.y)^2 + ((node.z-f.z)*800)^2
    if distance < 75^2 and f.routeIndex < f.route.Count()-1
        nextNode = nodes[f.route[f.routeIndex+1]]
        if not ReefCoralBlocked(s, f, f, nextNode) then f.routeIndex = f.routeIndex + 1
    end if
    ' String-pull visible waypoints. This rounds open-water corners without
    ' cutting through branches at an occlusion transition.
    if distance < 120^2
        for index = f.route.Count()-1 to f.routeIndex+1 step -1
            if not ReefCoralBlocked(s, f, f, nodes[f.route[index]])
                f.routeIndex = index
                exit for
            end if
        end for
    end if
    node = nodes[f.route[f.routeIndex]]
    f.tx = node.x : f.ty = node.y : f.tz = node.z
end sub
