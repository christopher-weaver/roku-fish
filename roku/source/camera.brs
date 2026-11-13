' Coordinates are 1920x1080 design pixels. z=0 rear wall, z=1 front glass.
function ReefCamera(t as double, mode as string) as double
    if mode = "Off" then return 64#
    amplitude = 12# : period = 480#
    if mode = "Slow" then amplitude = 48# : period = 360#
    return 64# + amplitude * Sin(ReefWrap(t, period) * 6.283185307 / period)
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
