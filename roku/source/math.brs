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
    result.widthScale=width/species.viewWidths[nearest] : result.width=width : result.sourceWidth=species.viewWidths[nearest]
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

' Nonuniform, true mesh angles give four times the head-on rotation detail.
function ReefBodyView(heading as double, species as object, result = invalid as dynamic) as object
    if species.bodyAngles=invalid then return ReefFishView(heading,species,result)
    angle=ReefWrap(heading,6.283185307)
    angles=species.bodyAngles : last=angles.Count()-1
    lo=0 : hi=last
    while lo<hi
        mid=Int((lo+hi+1)/2)
        if angles[mid]<=angle then lo=mid else hi=mid-1
    end while
    first=lo : second=(first+1) mod angles.Count()
    upper=angles[second]
    if second=0 then upper=6.283185307
    blend=ReefClamp((angle-angles[first])/(upper-angles[first]),0,1)
    nearest=first
    if blend>=0.5 then nearest=second
    width=species.bodyViewWidths[first]+(species.bodyViewWidths[second]-species.bodyViewWidths[first])*blend
    if result=invalid then result={}
    result.index=nearest : result.first=first : result.second=second : result.blend=blend
    result.width=width : result.sourceWidth=species.bodyViewWidths[nearest]
    return result
end function


' Spatially dense complete mesh poses. No strip transforms or large anchors.
function ReefMarineFrame(time as double,formation as object) as integer
    phase=ReefWrap(time,formation.animation.period)*6.283185307/formation.animation.period
    return Int((Sin(phase)+1#)*.5*(formation.animation.count-1)+.5)
end function

function ReefSmoother(v as double) as double
    v=ReefClamp(v,0#,1#)
    return v*v*v*(v*(v*6#-15#)+10#)
end function

function ReefEelPose(time as double,result=invalid as dynamic) as object
    t=ReefWrap(time+15#,31#) : peek=0#
    if t>=7# and t<14# then peek=ReefSmoother((t-7#)/7#)
    if t>=14# and t<20# then peek=1#
    if t>=20# and t<28# then peek=1#-ReefSmoother((t-20#)/8#)
    if result=invalid then result={}
    lift=ReefSmoother((peek-.62)/.38)
    result.peek=peek : result.x=812#-39#*peek
    result.y=875#-30#*lift : result.z=0#-124#+404#*peek
    result.angle=0#
    return result
end function

' Broad, feathered caustic bands projected on a plane tilted away from camera.
' Matching offline surface masks prevent any application to open-water pixels.
function ReefSurfaceShade(x as double,y as double,time as double) as double
    depth=ReefMax(.135,(y+180#)/1332#)
    u=(x-1024#)/(240#*depth) : v=0#-3.3/depth
    p=ReefWrap(time,8#)*6.283185307/8#
    a=Sin(6.283185307*u+.85*Sin(6.283185307*v+p)+p)
    b=Sin(6.283185307*v+.70*Sin(6.283185307*u-p)-p)
    alpha=72#*(.60*Exp(0#-a*a/.34)+.40*Exp(0#-b*b/.55))
    return 1#-alpha/255#
end function

function ReefEelFrame(time as double) as integer
    pose=ReefEelPose(time)
    if pose.peek<.999999 then return Int(pose.peek*64#+.5)
    q=ReefWrap(time+15#,31#)
    cycle=Int((time+15#)/31#)
    funny=0#
    if cycle mod 2=0 then funny=ReefEelPulse(q,17.2,19.6)
    expressionIndex=Int(funny*16#+.5)
    if expressionIndex>0 then return 80+expressionIndex
    mouth=ReefEelPulse(q,14.5,16.9)
    return 64+Int(mouth*16#+.5)
end function

function ReefEelPulse(q as double,first as double,last as double) as double
    t=(q-first)/(last-first)
    if t<=0# or t>=1# then return 0#
    return ReefSmoother(1#-Abs(2#*t-1#))
end function

' Subtle head-anchored 3D body sway, synchronized with the caudal beat.
' Only the display pose changes; collision envelopes include the full motion.
function ReefSwimPose(pose as object,sp as object,speed as dynamic,result=invalid as dynamic) as object
    if result=invalid then result={}
    effort=.6
    if speed<>invalid then effort=ReefClamp(speed/sp.speed,0#,1#)
    yaw=Sin(pose.phase)*(.018+.024*effort)
    roll=Sin(pose.phase-.65)*(.006+.010*effort)
    heading=pose.heading+yaw : anchor=sp.length*.18
    result.x=pose.x+(Cos(pose.heading)-Cos(heading))*anchor
    result.z=pose.z+(Sin(pose.heading)-Sin(heading))*anchor/800#
    result.y=pose.y+roll*anchor*Abs(Cos(pose.heading))*Cos(pose.heading)
    result.heading=heading : result.pitch=ReefClamp(pose.pitch+roll*Cos(pose.heading),0#-.22,.22)
    result.phase=pose.phase : result.finPhase=pose.finPhase
    return result
end function
