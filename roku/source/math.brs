' Deep Reef — original deterministic simulation helpers. Double precision PRNG arithmetic.
function ReefClamp(v as double, lo as double, hi as double) as double
    if v < lo then return lo
    if v > hi then return hi
    return v
end function

function ReefWrap(v as double, period as double) as double
    return v - Int(v / period) * period
end function

function ReefRandom(s as object) as double
    v = s.rng * 48271#
    s.rng = v - Int(v / 2147483647#) * 2147483647#
    return (s.rng - 1#) / 2147483646#
end function

function ReefRange(s as object, lo as double, hi as double) as double
    return lo + ReefRandom(s) * (hi - lo)
end function

function ReefAngle(x as double, z as double) as double
    if Abs(x) < 0.00001
        if z >= 0 then return 1.570796327#
        return -1.570796327#
    end if
    a = Atn(z / x)
    if x < 0 then a = a + 3.141592654
    return a * 1#
end function

function ReefAngleDelta(a as double, b as double) as double
    return ReefWrap(b - a + 3.141592654, 6.283185307) - 3.141592654
end function

function ReefEase(v as double) as double
    v = ReefClamp(v, 0, 1)
    return v * v * (3 - 2 * v)
end function

function ReefRGBA(r as integer, g as integer, b as integer, a as integer) as integer
    if r > 127 then r = r - 256
    return r * &h1000000 + g * &h10000 + b * &h100 + a
end function

function ReefMin(a as double, b as double) as double
    if a < b then return a
    return b
end function

function ReefMax(a as double, b as double) as double
    if a > b then return a
    return b
end function

function ReefFrameSchedule(nowMs as double, deadline as double, fps as double) as object
    deadline = deadline + 1000# / fps
    if deadline < nowMs then deadline = nowMs
    ' A double-buffered swap supplies native display pacing at 60Hz.
    ' Only the 30Hz mode needs an extra wait; leave GPU submission headroom.
    delay = 0
    if fps < 59 then delay = Int(ReefMax(0#, deadline - nowMs - 8#))
    return {deadline:deadline, sleepMs:delay}
end function

' Match the silhouette width continuously between densely sampled mesh views.
' The texture selects a 5.625-degree view, but its apparent width no longer pops
' each time the atlas index changes. Tail motion remains independent.
function ReefFishView(heading as double, species as object, result = invalid as dynamic) as object
    position = ReefWrap(heading, 6.283185307) * species.yawCount / 6.283185307
    first = Int(position) mod species.yawCount
    second = (first + 1) mod species.yawCount
    nearest = Int(position + 0.5) mod species.yawCount
    blend = position - Int(position)
    width = species.viewWidths[first] + (species.viewWidths[second] - species.viewWidths[first]) * blend
    if result=invalid then result={}
    result.index=nearest : result.first=first : result.second=second : result.blend=blend
    result.widthScale=width/species.viewWidths[nearest] : result.width=width
    return result
end function


' Floating scales carry the small remainder lost by integer draw coordinates.
' A shorter anchor bounds rotated float32 error and shape stretch for fish.
function ReefFishTransform(x as double, y as double, sx as double, sy as double, angle as double, result = invalid as dynamic) as object
    anchor = 4096#
    angle = Int(angle * 256 + 0.5) / 256#
    c = Cos(angle / 57.295779513#) : sn = Sin(angle / 57.295779513#)
    px = Int(x - anchor * (c * sx + sn * sy))
    py = Int(y - anchor * (c * sy - sn * sx))
    dx = x - px - anchor * (c * sx + sn * sy)
    dy = y - py - anchor * (c * sy - sn * sx)
    if result = invalid then result = {}
    result.x = px : result.y = py : result.angle = angle
    result.sx = sx + (c * dx - sn * dy) / anchor
    result.sy = sy + (sn * dx + c * dy) / anchor
    return result
end function

function ReefFishPixelsValid(pixels as object) as boolean
    if pixels.Count() <> 1536 then return false
    for channel = 0 to 3
        totalA = 0# : totalB = 0# : weightedA = 0# : weightedB = 0#
        for column = 0 to 23
            a = pixels[(4 * 24 + column) * 4 + channel]
            b = pixels[(11 * 24 + column) * 4 + channel]
            totalA = totalA + a : totalB = totalB + b
            weightedA = weightedA + column * a : weightedB = weightedB + column * b
        end for
        if totalA >= 128 and totalB >= 128
            centerA = weightedA / totalA : centerB = weightedB / totalB
            movement = Abs(centerB - centerA)
            if ReefMin(centerA,centerB) > 7.5 and ReefMax(centerA,centerB) < 11 and movement > 0.12 and movement < 0.45 then return true
        end if
    end for
    return false
end function


' Integer neighbor positions and their weight. Scale precision cannot amplify
' these offsets: even a quantized scale leaves the pan's pixel centroid smooth.
function ReefPixelPhase(x as double) as object
    first = Int(x)
    return {first:first,blend:x-first}
end function
