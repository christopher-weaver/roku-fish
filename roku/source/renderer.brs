function ReefRenderer(screen as object, settings as object) as object
    r = { screen: screen, scale: screen.GetWidth() / 1920.0, rotation: false, font: invalid }
    features = screen.GetGraphicsFeatures()
    if features <> invalid and features.full_rotation = true then r.rotation = true
    fonts = CreateObject("roFontRegistry")
    r.font = fonts.GetDefaultFont(Int(24 * r.scale), false, false)
    return r
end function

sub ReefDraw(r as object, x as double, y as double, sx as double, sy as double, bmp as dynamic, tint as integer)
    if bmp = invalid then return
    r.screen.DrawScaledObject(Int(x * r.scale), Int(y * r.scale), sx * r.scale, sy * r.scale, bmp, tint)
end sub

sub ReefDrawFish(r as object, s as object, a as object, f as object)
    frames = a.fish[f.name]
    if frames = invalid then return
    p = ReefProjection(f, s.camera)
    if p.x < -200 or p.x > 2120 then return
    yaw = Int(ReefWrap(f.heading, 6.283185307) * 16 / 6.283185307 + 0.5) mod 16
    pose = Int((Sin(f.phase) + 1) * 1.49)
    index = yaw * 3 + pose
    scale = p.scale * f.sp.length / f.sp.renderLength * f.size
    haze = 1 - f.z
    tint = ReefRGBA(Int(255 - haze * 65), Int(247 - haze * 32), 255, 255)
    if s.settings.lighting = "Sunset" then tint = ReefRGBA(255, Int(239 - haze * 25), Int(240 - haze * 10), 255)
    if r.rotation
        angle = f.pitch * 57.29578
        if Cos(f.heading) < 0 then angle = -angle
        r.screen.DrawTransformedObject(Int(p.x * r.scale), Int(p.y * r.scale), angle, scale * r.scale, scale * r.scale, frames[index], tint)
    else
        ReefDraw(r, p.x, p.y, scale, scale, frames[index], tint)
    end if
end sub

sub ReefDrawEffects(r as object, s as object, a as object, lo as double, hi as double)
    particles = 24 : bubbles = 6
    if s.settings.particles = "Off" then particles = 0
    if s.settings.particles = "Medium" then particles = 48
    if s.settings.bubbles = "Off" then bubbles = 0
    if s.settings.bubbles = "Medium" then bubbles = 12
    for each e in s.effects
        if e.z >= lo and e.z < hi
            if e.bubble
                if e.active - 48 < bubbles
                    alpha = Int(ReefClamp((e.y - 38) / 50, 0, 1) * 150)
                    ReefDraw(r, e.x - s.camera * (0.6 + e.z * 0.4), e.y, 0.24 + e.z * 0.34, 0.24 + e.z * 0.34, a.bubble, ReefRGBA(255, 237, 238, alpha))
                end if
            else if e.active < particles
                ' Fade optional particles smoothly as Auto quality responds to frame measurements.
                opacity = ReefClamp((s.quality * particles - e.active) / 4, 0, 1)
                if opacity > 0 then ReefDraw(r, e.x - s.camera * (0.4 + e.z * 0.6), e.y, 0.25 + e.z * 0.4, 0.25 + e.z * 0.4, a.mote, ReefRGBA(255, 231, 224, Int(105 * opacity)))
            end if
        end if
    end for
end sub

sub ReefDrawCaustics(r as object, s as object, a as object)
    n = a.caustics.Count()
    if n = 0 then return
    phase = ReefWrap(s.time * 0.8, n)
    first = Int(phase) : blend = phase - first
    for j = 0 to 1
        opacity = 1 - blend
        if j = 1 then opacity = blend
        bmp = a.caustics[(first + j) mod n]
        for k = 0 to 3
            ReefDraw(r, k * 620 - 120 - s.camera * 0.2 + Sin(s.time * 0.06) * 18, 720, 1.65, 0.9, bmp, ReefRGBA(255, 228, 200, Int(opacity * 82 * s.quality * s.lighting[0])))
        end for
    end for
end sub

sub ReefRender(r as object, s as object, a as object)
    screen = r.screen
    screen.SetAlphaEnable(false)
    screen.Clear(&h182A42FF)
    ReefDraw(r, -s.camera, -36, 1, 1, a.plate, &hFFFFFFFF)
    screen.SetAlphaEnable(true)
    ReefDrawCaustics(r, s, a)
    ' Stable insertion sort of references, not copied fish. Persistent list has bounded length.
    if s.sorted = invalid then s.sorted = []
    s.sorted.Clear()
    for each f in s.fish
        s.sorted.Push(f)
        j = s.sorted.Count() - 1
        while j > 0
            if s.sorted[j - 1].z <= f.z then exit while
            s.sorted[j] = s.sorted[j - 1] : j = j - 1
        end while
        s.sorted[j] = f
    end for
    ReefDrawEffects(r, s, a, 0, 0.48)
    i = 0
    while i < s.sorted.Count()
        if s.sorted[i].z >= 0.48 then exit while
        ReefDrawFish(r, s, a, s.sorted[i]) : i = i + 1
    end while
    ReefDraw(r, -s.camera, 124, 1, 1, a.mid, &hFFFFFFFF)
    while i < s.sorted.Count()
        if s.sorted[i].z >= 0.78 then exit while
        ReefDrawFish(r, s, a, s.sorted[i]) : i = i + 1
    end while
    ReefDraw(r, -s.camera, 124, 1, 1, a.front, &hFFFFFFFF)
    if a.coral.Count() > 0
        phase = ReefWrap(s.time / 5.5, 3)
        first = Int(phase) : blend = phase - first
        ReefDraw(r, 375 - s.camera, 569, 1, 1, a.coral[first], ReefRGBA(255, 255, 255, Int(255 * (1 - blend))))
        ReefDraw(r, 375 - s.camera, 569, 1, 1, a.coral[(first + 1) mod 3], ReefRGBA(255, 255, 255, Int(255 * blend)))
    end if
    while i < s.sorted.Count()
        ReefDrawFish(r, s, a, s.sorted[i]) : i = i + 1
    end while
    ReefDrawEffects(r, s, a, 0.48, 1.01)
    for k = 0 to 2
        ReefDraw(r, 150 + k * 590 + Sin(s.time * 0.07 + k) * 24 - s.camera * 0.25, -70, 2.0, 1.8, a.ray, ReefRGBA(255, 223, 210, Int((65 + 18 * Sin(s.time * 0.13 + k)) * s.lighting[0])))
    end for
    if s.lighting[2] > 0 then screen.DrawRect(0, 0, screen.GetWidth(), screen.GetHeight(), ReefRGBA(8, 16, 57, Int(s.lighting[2])))
    if s.lighting[3] > 0 then screen.DrawRect(0, 0, screen.GetWidth(), screen.GetHeight(), ReefRGBA(241, 105, 108, Int(s.lighting[3])))
    if s.settings.clock = "On" then screen.DrawText(s.clockText, Int(1660 * r.scale), Int(970 * r.scale), &hF6DFD4B0, r.font)
    if s.settings.fps = "On" then screen.DrawText(Int(s.fps).ToStr() + " FPS", Int(110 * r.scale), Int(95 * r.scale), &hF6DFD4D0, r.font)
end sub
