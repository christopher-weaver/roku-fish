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
