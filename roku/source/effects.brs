sub ReefEffectsInit(s as object)
    ' Fixed pools: no accumulation, texture loads, or spawning allocations at runtime.
    for i = 0 to 71
        bubble = i >= 48
        s.effects.Push({ x: ReefRange(s, 0, 2048), y: ReefRange(s, 0, 1080), z: ReefRandom(s), phase: ReefRange(s, 0, 6.283), speed: ReefRange(s, 2, 9), bubble: bubble, age: ReefRange(s, 0, 12), active: i })
    end for
    for each e in s.effects
        e.previousX = e.x : e.previousY = e.y
    end for
end sub

sub ReefEffectsStep(s as object, dt as double)
    for each e in s.effects
        e.previousX = e.x : e.previousY = e.y
        e.recycled = false
        e.phase = ReefWrap(e.phase + dt * 0.4, 6.283185307)
        e.x = e.x + (2 + e.z * 5 + Sin(e.phase) * 2) * dt
        if e.bubble
            e.age = e.age + dt
            e.y = e.y - (25 + e.speed * 3 + e.age * 0.4) * dt
            if e.y < 38
                e.y = 1040 + ReefRange(s, 0, 200)
                e.x = 1440 + ReefRange(s, -25, 25)
                e.age = 0
                e.recycled = true
            end if
        else
            e.y = e.y + e.speed * dt
            if e.y > 1090
                e.y = -10 : e.x = ReefRange(s, 0, 2048)
                e.recycled = true
            end if
        end if
        if e.x > 2058
            e.x = -10
            e.recycled = true
        end if
        if e.recycled
            e.previousX = e.x : e.previousY = e.y
        end if
    end for
end sub

' Returns dark-blue and warm-pink overlay alpha. Automatic thresholds are data-configurable.
function ReefLighting(hour as double, mode as string, dawn as double, dusk as double) as object
    day = 1# : warm = 0#
    if mode = "Sunset" then warm = 1
    if mode = "Dusk" then day = 0.52 : warm = 0.55
    if mode = "Moonlight" then day = 0.12
    if mode = "Automatic"
        rise = ReefEase((hour - dawn) / 1.5)
        set = 1 - ReefEase((hour - dusk) / 1.5)
        day = 0.12 + 0.88 * rise * set
        warm = ReefClamp(1 - Abs(hour - (dusk + 0.6)) / 1.4, 0, 1)
    end if
    return [day, warm, (1 - day) * 150, warm * 38]
end function

sub ReefLightingStep(s as object, hour as double, dt as double)
    target = ReefLighting(hour, s.settings.lighting, s.cfg.dawn, s.cfg.dusk)
    if s.frames = 0 then s.lighting = target
    for i = 0 to 3
        s.lighting[i] = s.lighting[i] + (target[i] - s.lighting[i]) * ReefClamp(dt / 20, 0, 1)
    end for
end sub

sub ReefQualitySample(s as object, seconds as double, frameCount as integer)
    if seconds <= 0 then return
    s.fps = frameCount / seconds
    if s.settings.quality <> "Auto" then return
    if s.renderFps = invalid then s.renderFps = 60#
    if s.pacingPressure = invalid then s.pacingPressure = 0#
    if s.renderFps = 60 and s.fps < 45
        s.pacingPressure = s.pacingPressure + seconds
        if s.pacingPressure >= 12
            ' Lock to an even 30Hz cadence rather than oscillating between frame caps.
            s.renderFps = 30#
            s.adaptation = 0#
        end if
    else
        s.pacingPressure = ReefMax(0#, s.pacingPressure - seconds)
    end if
    if s.fps < 25
        s.adaptation = s.adaptation + seconds
    else
        s.adaptation = ReefClamp(s.adaptation - seconds, 0, 60)
    end if
    if s.adaptation >= 12 then s.quality = ReefClamp(s.quality - 0.08, 0.3, 1) : s.adaptation = 6
    if s.fps > 29 and s.adaptation = 0 then s.quality = ReefClamp(s.quality + 0.02, 0.3, 1)
end sub

function ReefBubbleScale(z as double) as double
    ' 32px source rings yield 13-28px bubbles, versus the former 5-12px specks.
    return 0.42 + ReefClamp(z, 0, 1) * 0.45
end function

function ReefSurface(t as double) as object
    ' One phase drives both the moving surface and refracted sand highlights.
    phase = ReefWrap(ReefWrap(t, 8#) * 4#, 32#)
    first = Int(phase)
    return { first: first, second: (first + 1) mod 32, blend: phase - first }
end function

function ReefEffectPose(e as object, alpha as double) as object
    return {x:e.previousX + (e.x - e.previousX) * alpha, y:e.previousY + (e.y - e.previousY) * alpha}
end function
