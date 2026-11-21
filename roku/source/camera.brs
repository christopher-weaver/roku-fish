' Coordinates are 1920x1080 design pixels. z=0 rear wall, z=1 front glass.
function ReefCamera(t as double, mode as string, config = invalid as dynamic) as double
    if mode = "Off" then return 64#
    amplitude = 40# : period = 180#
    if mode = "Slow" then amplitude = 56# : period = 240#
    if config <> invalid and config[mode] <> invalid
        amplitude = config[mode].amplitude : period = config[mode].period
    end if
    return 64# - amplitude * Cos(ReefWrap(t, period) * 6.283185307 / period)
end function

function ReefDisplayPose(f as object, alpha as double, pose = invalid as dynamic) as object
    if pose=invalid then pose={}
    pose.x=f.previousX+(f.x-f.previousX)*alpha
    pose.y=f.previousY+(f.y-f.previousY)*alpha
    pose.z=f.previousZ+(f.z-f.previousZ)*alpha
    delta = ReefAngleDelta(f.previousHeading, f.heading)
    ' Cubic heading interpolation keeps angular velocity continuous at 30Hz ticks.
    a2 = alpha * alpha : a3 = a2 * alpha
    pose.heading = f.previousHeading + delta * (3*a2-2*a3)
    pose.heading = pose.heading + (a3-2*a2+alpha) * f.previousYawVelocity / 30# + (a3-a2) * f.yawVelocity / 30#
    pose.pitch = f.previousPitch + (f.pitch - f.previousPitch) * alpha
    pose.phase = f.previousPhase + ReefAngleDelta(f.previousPhase, f.phase) * alpha
    pose.finPhase = f.previousFinPhase + ReefAngleDelta(f.previousFinPhase, f.finPhase) * alpha
    return pose
end function

function ReefProjection(f as object, camera as double, result = invalid as dynamic) as object
    scale = 0.70 + 0.30 * f.z
    if result=invalid then result={}
    result.x=f.x-camera*scale : result.y=f.y+(1-f.z)*30 : result.scale=scale
    return result
end function

function ReefSolid(s as object, x as double, y as double) as boolean
    if s.occupancy = invalid then return false
    col = Int(x / s.occupancy.cell)
    row = Int((y + 36) / s.occupancy.cell)
    if row < 0 or row >= s.occupancy.rows.Count() then return false
    line = s.occupancy.rows[row]
    if col < 0 or col >= Len(line) then return false
    return Mid(line, col + 1, 1) = "#"
end function

' Fish footprints include every yaw, tail and fin pose plus the maximum pitch.
' Test the swept rectangle, not just the center at a depth-plane crossing.
function ReefCoralBlocked(s as object, f as object, fromPose as object, toPose as object) as boolean
    if ReefSurfaceBlocked(s,f,fromPose,toPose) then return true
    if ReefFloorBlocked(s,f,fromPose,toPose) then return true
    if s.occupancy = invalid then return false
    if ReefCaveBlocked(s,f,fromPose,toPose) then return true
    planes = s.occupancy.planes
    if planes = invalid then return false
    radius = f.sp.bodyThickness * f.sp.length * f.size / 1728# + 0.012
    lo=ReefMin(fromPose.z,toPose.z)-radius : hi=ReefMax(fromPose.z,toPose.z)+radius
    for planeIndex = 0 to planes.Count() - 1
        plane = planes[planeIndex]
        if hi >= plane.z - plane.halfDepth and lo <= plane.z + plane.halfDepth
            s.collisionFirst=ReefProjection(fromPose,0#,s.collisionFirst)
            s.collisionLast=ReefProjection(toPose,0#,s.collisionLast)
            first=s.collisionFirst : last=s.collisionLast
            scale = ReefMax(first.scale, last.scale) * f.sp.length / f.sp.renderLength * f.size
            hw = (f.sp.collisionHalfWidth + f.sp.collisionHalfHeight * 0.22) * scale + 8
            hh = (f.sp.collisionHalfHeight + f.sp.collisionHalfWidth * 0.22) * scale + 8
            ' Reef coordinates are screen + camera, while fish have depth parallax.
            ' Reserve the whole camera sweep, so panning cannot push a fish into rock.
            parallax = 1#
            if plane.parallax <> invalid then parallax = plane.parallax
            firstPan = ReefMin(8 * (parallax - first.scale), 120 * (parallax - first.scale))
            lastPan = ReefMin(8 * (parallax - last.scale), 120 * (parallax - last.scale))
            x0 = ReefMin(first.x + firstPan, last.x + lastPan) + 64 * (1 - parallax) - hw
            firstPan = ReefMax(8 * (parallax - first.scale), 120 * (parallax - first.scale))
            lastPan = ReefMax(8 * (parallax - last.scale), 120 * (parallax - last.scale))
            x1 = ReefMax(first.x + firstPan, last.x + lastPan) + 64 * (1 - parallax) + hw
            y0 = ReefMin(first.y, last.y) + 36 - hh
            y1 = ReefMax(first.y, last.y) + 36 + hh
            if ReefSolidRect(plane.rows, s.occupancy.cell, x0, y0, x1, y1) then return true
        end if
    end for
    return false
end function

function ReefSolidRect(rows as object, cell as integer, x0 as double, y0 as double, x1 as double, y1 as double) as boolean
    top = Int(ReefClamp(Int(y0 / cell), 0, rows.Count() - 1))
    bottom = Int(ReefClamp(Int(y1 / cell), 0, rows.Count() - 1))
    left = Int(ReefClamp(Int(x0 / cell), 0, Len(rows[0]) - 1))
    right = Int(ReefClamp(Int(x1 / cell), 0, Len(rows[0]) - 1))
    if x1 < 0 or y1 < 0 or x0 >= Len(rows[0]) * cell or y0 >= rows.Count() * cell then return false
    for rowIndex = top to bottom
        found = Instr(left + 1, rows[rowIndex], "#")
        if found > 0 and found <= right + 1 then return true
    end for
    return false
end function

sub ReefSafeSpawn(s as object, f as object)
    if not ReefCoralBlocked(s, f, f, f) then return
    original = f.z : best = 10# : chosen = 0.3
    for each lane in [0.12, 0.94]
        candidate = {x:f.x, y:f.y, z:lane}
        distance = Abs(lane - original)
        if distance < best and not ReefCoralBlocked(s, f, candidate, candidate)
            chosen = lane : best = distance
        end if
    end for
    ' A deeply emerged eel can occupy both usual depth lanes. Relocate a
    ' blocked initial spawn to the nearest pre-cleared navigation node.
    if best=10# and s.navigation<>invalid
        selected=invalid : nearest=1e20
        for nodeIndex=0 to s.navigation.nodes.Count()-1
            node=s.navigation.nodes[nodeIndex]
            distance=(node.x-f.x)^2+(node.y-f.y)^2+((node.z-f.z)*800#)^2
            if distance<nearest and not ReefCoralBlocked(s,f,node,node)
                selected=node : nearest=distance
            end if
        end for
        if selected<>invalid
            f.x=selected.x : f.y=selected.y : f.z=selected.z
            return
        end if
    end if
    f.z = chosen
end sub

' A swept body against the cave's solid reserved volume. The resident moray is
' not in s.fish; spawning, planning and final free-swimmer guards all use this.
function ReefCaveBlocked(s as object,f as object,a as object,b as object) as boolean
    if s.occupancy.volumes=invalid then return false
    scale=(.70+.30*ReefMax(a.z,b.z))*f.sp.length/f.sp.renderLength*f.size
    hw=(f.sp.collisionHalfWidth+f.sp.collisionHalfHeight*.22)*scale+26#
    hh=(f.sp.collisionHalfHeight+f.sp.collisionHalfWidth*.22)*scale+12#
    depth=f.sp.bodyThickness*f.sp.length*f.size/1728#+.012
    for volumeIndex=0 to s.occupancy.volumes.Count()-1
        v=s.occupancy.volumes[volumeIndex]
        possible=ReefMax(a.z,b.z)+depth>=v.z-v.halfDepth and ReefMin(a.z,b.z)-depth<=v.z+v.halfDepth
        possible=possible and ReefMax(a.x,b.x)+hw>=v.x-v.halfWidth and ReefMin(a.x,b.x)-hw<=v.x+v.halfWidth
        possible=possible and ReefMax(a.y,b.y)+hh>=v.y-v.halfHeight and ReefMin(a.y,b.y)-hh<=v.y+v.halfHeight
        if possible
            enter=0# : leave=1# : hit=true
            for axis=0 to 2
                start=a.x : delta=b.x-a.x : low=v.x-v.halfWidth-hw : high=v.x+v.halfWidth+hw
                if axis=1 then start=a.y : delta=b.y-a.y : low=v.y-v.halfHeight-hh : high=v.y+v.halfHeight+hh
                if axis=2 then start=a.z : delta=b.z-a.z : low=v.z-v.halfDepth-depth : high=v.z+v.halfDepth+depth
                if Abs(delta)<.0000001
                    if start<low or start>high then hit=false
                else
                    t0=(low-start)/delta : t1=(high-start)/delta
                    enter=ReefMax(enter,ReefMin(t0,t1))
                    leave=ReefMin(leave,ReefMax(t0,t1))
                end if
            end for
            if hit and enter<=leave then return true
        end if
    end for
    return false
end function

' The fish's whole pitched body must remain above the ridged 3D floor.
' A linear floor plane and a swept maximum body envelope need both endpoints.
function ReefFloorBlocked(s as object,f as object,a as object,b as object) as boolean
    if s.cfg=invalid then return false
    floor=s.cfg.floor
    if floor=invalid then return false
    scale=(.70+.30*ReefMax(a.z,b.z))*f.sp.length/f.sp.renderLength*f.size
    hh=(f.sp.collisionHalfHeight+f.sp.collisionHalfWidth*.22)*scale+12#
    radius=f.sp.bodyThickness*f.sp.length*f.size/1728#+.012
    firstCeiling=floor.baseY+floor.slope*(a.z-radius)-floor.ridgeClearance-hh
    lastCeiling=floor.baseY+floor.slope*(b.z-radius)-floor.ridgeClearance-hh
    return a.y>firstCeiling or b.y>lastCeiling
end function

' Bound every posed fish below the thin surface layer, including pitched fins.
function ReefSurfaceBlocked(s as object,f as object,a as object,b as object) as boolean
    if s.cfg=invalid then return false
    if s.cfg.waterline=invalid then return false
    scale=(.70+.30*ReefMax(a.z,b.z))*f.sp.length/f.sp.renderLength*f.size
    hh=(f.sp.collisionHalfHeight+f.sp.collisionHalfWidth*.22)*scale+12#
    firstTop=a.y+(1#-a.z)*30#-hh
    lastTop=b.y+(1#-b.z)*30#-hh
    return ReefMin(firstTop,lastTop)<s.cfg.waterline.clearanceY
end function
