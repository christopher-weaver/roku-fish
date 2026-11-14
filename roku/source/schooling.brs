' Separation for every species; alignment and cohesion only for chromis.
function ReefNeighbors(s as object, f as object) as object
    steer = { x: 0#, y: 0#, z: 0#, hx: 0#, hz: 0#, cx: 0#, cy: 0#, cz: 0#, count: 0, alarm: false }
    ' Indexed access is safe even when the caller is visiting this same array.
    for neighborIndex = 0 to s.fish.Count() - 1
        other = s.fish[neighborIndex]
        if other.id <> f.id
            dx = f.x - other.x : dy = f.y - other.y : dz = (f.z - other.z) * 800
            distance = dx * dx + dy * dy + dz * dz
            if distance < 8100 and distance > 0.001
                k = (90 - Sqr(distance)) / Sqr(distance)
                steer.x = steer.x + dx * k * 1.4
                steer.y = steer.y + dy * k * 1.4
                steer.z = steer.z + dz * k * 1.4
                if other.sp.length > 160 and f.schooling then steer.alarm = true
            end if
            if f.schooling and other.schooling and distance < 160000
                steer.cx = steer.cx + other.x
                steer.cy = steer.cy + other.y
                steer.cz = steer.cz + other.z
                steer.hx = steer.hx + Cos(other.heading)
                steer.hz = steer.hz + Sin(other.heading)
                steer.count = steer.count + 1
            end if
        end if
    end for
    if steer.count > 0
        steer.x = steer.x + (steer.cx / steer.count - f.x) * 0.12 + steer.hx / steer.count * 16
        steer.y = steer.y + (steer.cy / steer.count - f.y) * 0.14
        steer.z = steer.z + (steer.cz / steer.count - f.z) * 90 + steer.hz / steer.count * 14
    end if
    return steer
end function
