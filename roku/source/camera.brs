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

function ReefDisplayPose(f as object, alpha as double) as object
    pose = { x: f.previousX + (f.x - f.previousX) * alpha, y: f.previousY + (f.y - f.previousY) * alpha, z: f.previousZ + (f.z - f.previousZ) * alpha }
    pose.heading = f.previousHeading + ReefAngleDelta(f.previousHeading, f.heading) * alpha
    pose.pitch = f.previousPitch + (f.pitch - f.previousPitch) * alpha
    pose.phase = f.previousPhase + ReefAngleDelta(f.previousPhase, f.phase) * alpha
    pose.finPhase = f.previousFinPhase + ReefAngleDelta(f.previousFinPhase, f.finPhase) * alpha
    return pose
end function

function ReefProjection(f as object, camera as double) as object
    scale = 0.56 + 0.44 * f.z
    return { x: 1024 + (f.x - 1024) * scale - camera * scale, y: 480 + (f.y - 480) * scale + (1 - f.z) * 70, scale: scale }
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
    if s.occupancy = invalid then return false
    planes = s.occupancy.planes
    if planes = invalid then return false
    radius = f.sp.bodyThickness * f.sp.length * f.size / 1728# + 0.012
    for planeIndex = 0 to planes.Count() - 1
        plane = planes[planeIndex]
        lo = ReefMin(fromPose.z, toPose.z) - radius
        hi = ReefMax(fromPose.z, toPose.z) + radius
        if hi >= plane.z - plane.halfDepth and lo <= plane.z + plane.halfDepth
            first = ReefProjection(fromPose, 0#) : last = ReefProjection(toPose, 0#)
            scale = ReefMax(first.scale, last.scale) * f.sp.length / f.sp.renderLength * f.size
            hw = (f.sp.collisionHalfWidth + f.sp.collisionHalfHeight * 0.22) * scale + 8
            hh = (f.sp.collisionHalfHeight + f.sp.collisionHalfWidth * 0.22) * scale + 8
            ' Reef coordinates are screen + camera, while fish have depth parallax.
            ' Reserve the whole camera sweep, so panning cannot push a fish into rock.
            x0 = ReefMin(first.x + 8 * (1 - first.scale), last.x + 8 * (1 - last.scale)) - hw
            x1 = ReefMax(first.x + 120 * (1 - first.scale), last.x + 120 * (1 - last.scale)) + hw
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
    for each lane in [0.30, 0.63, 0.95]
        candidate = {x:f.x, y:f.y, z:lane}
        distance = Abs(lane - original)
        if distance < best and not ReefCoralBlocked(s, f, candidate, candidate)
            chosen = lane : best = distance
        end if
    end for
    f.z = chosen
end sub
