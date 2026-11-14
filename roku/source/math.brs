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
