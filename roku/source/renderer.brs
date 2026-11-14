function ReefRenderer(screen as object, settings as object) as object
    r = { screen: screen, scale: screen.GetWidth() / 1920.0, rotation: false, font: invalid, placement: {} }
    features = screen.GetGraphicsFeatures()
    if features <> invalid and features.full_rotation = true then r.rotation = true
    fonts = CreateObject("roFontRegistry")
    r.font = fonts.GetDefaultFont(Int(24 * r.scale), false, false)
    r.fractionalPan = ReefFractionalPanProbe(screen)
    r.fractionalTransform = false
    if not r.fractionalPan
        r.fractionalPan = ReefFractionalPanProbe(screen, true)
        r.fractionalTransform = r.fractionalPan
    end if
    print "Deep Reef fractional pan=";r.fractionalPan;" transformed=";r.fractionalTransform
    r.fractionalFish = ReefFractionalFishProbe(screen, r.rotation)
    print "Deep Reef fractional fish=";r.fractionalFish
    return r
end function

sub ReefDraw(r as object, x as double, y as double, sx as double, sy as double, bmp as dynamic, tint as integer)
    if bmp = invalid then return
    if Type(bmp) = "roAssociativeArray"
        if r.fractionalPan
            transform = ReefLayerTransform(x * r.scale, y * r.scale, sx * r.scale, sy * r.scale, r.placement)
            if r.fractionalTransform
                r.screen.DrawTransformedObject(transform.x, transform.y, 0, transform.sx, transform.sy, bmp.fractional, tint)
            else
                r.screen.DrawScaledObject(transform.x, transform.y, transform.sx, transform.sy, bmp.fractional, tint)
            end if
        else
            r.screen.DrawScaledObject(Int(x * r.scale + 0.5), Int(y * r.scale + 0.5), sx * r.scale, sy * r.scale, bmp.normal, tint)
        end if
    else
        r.screen.DrawScaledObject(Int(x * r.scale + 0.5), Int(y * r.scale + 0.5), sx * r.scale, sy * r.scale, bmp, tint)
    end if
end sub

sub ReefDrawFish(r as object, s as object, a as object, f as object)
    frames = a.fish[f.name]
    if frames = invalid then return
    pose = f.renderPose
    p = ReefProjection(pose, s.camera)
    if p.x < -200 or p.x > 2120 then return
    view = ReefFishView(pose.heading, f.sp)
    bodyPose = Int((Sin(pose.phase) + 1) * 0.5 * (f.sp.poseCount - 1) + 0.5)
    finPose = Int((Sin(pose.finPhase) + 1) * 0.5 * (f.sp.finPoseCount - 1) + 0.5)
    scale = p.scale * f.sp.length / f.sp.renderLength * f.size
    haze = 1 - pose.z
    red = Int(255 - haze * 65) : green = Int(247 - haze * 32) : blue = 255
    if s.settings.lighting = "Sunset" then red = 255 : green = Int(239 - haze * 25) : blue = Int(240 - haze * 10)
    angle = pose.pitch * 57.29578
    if Cos(pose.heading) < 0 then angle = -angle
    finFrames = a.fins[f.name]
    for part = 0 to 1
        for pass = 0 to 1
            yaw = view.first : alpha = 255
            if pass = 1 then yaw = view.second : alpha = Int(view.blend * 255 + 0.5)
            if alpha > 0
                scaleX = scale * view.width / f.sp.viewWidths[yaw]
                index = yaw * f.sp.poseCount + bodyPose
                if f.sp.frames[index].flipX = true then scaleX = -scaleX
                tint = ReefRGBA(red,green,blue,alpha)
                if part = 0
                    ReefDrawFishRegion(r,p.x,p.y,scaleX,scale,angle,frames[index],tint)
                else if finFrames <> invalid
                    index = yaw * f.sp.finPoseCount + finPose
                    ReefDrawFishRegion(r,p.x,p.y,scaleX,scale,angle,finFrames[index],tint)
                end if
            end if
        end for
    end for
end sub

sub ReefDrawFishRegion(r as object, x as double, y as double, sx as double, sy as double, angle as double, region as object, tint as integer)
    if not r.rotation then angle = 0#
    if r.fractionalFish
        transform = ReefFishTransform(x*r.scale,y*r.scale,sx*r.scale,sy*r.scale,angle,r.placement)
        if r.rotation
            r.screen.DrawTransformedObject(transform.x,transform.y,transform.angle,transform.sx,transform.sy,region.fractional,tint)
        else
            r.screen.DrawScaledObject(transform.x,transform.y,transform.sx,transform.sy,region.fractional,tint)
        end if
    else if r.rotation
        r.screen.DrawTransformedObject(Int(x*r.scale+0.5),Int(y*r.scale+0.5),angle,sx*r.scale,sy*r.scale,region.normal,tint)
    else
        r.screen.DrawScaledObject(Int(x*r.scale+0.5),Int(y*r.scale+0.5),sx*r.scale,sy*r.scale,region.normal,tint)
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
            displayX = e.previousX + (e.x - e.previousX) * s.renderAlpha
            displayY = e.previousY + (e.y - e.previousY) * s.renderAlpha
            if e.bubble
                if e.active - 48 < bubbles
                    alpha = Int(ReefClamp((displayY - 38) / 50, 0, 1) * 150)
                    size = ReefBubbleScale(e.z)
                    ReefDraw(r, displayX - s.camera * (0.6 + e.z * 0.4), displayY, size, size, a.bubble, ReefRGBA(255, 237, 238, alpha))
                end if
            else if e.active < particles
                ' Fade optional particles smoothly as Auto quality responds to frame measurements.
                opacity = ReefClamp((s.quality * particles - e.active) / 4, 0, 1)
                if opacity > 0 then ReefDraw(r, displayX - s.camera * (0.4 + e.z * 0.6), displayY, 0.25 + e.z * 0.4, 0.25 + e.z * 0.4, a.mote, ReefRGBA(255, 231, 224, Int(105 * opacity)))
            end if
        end if
    end for
end sub

sub ReefDrawSurface(r as object, s as object, a as object)
    if a.surface.Count() = 0 then return
    wave = ReefSurface(s.displayTime)
    cfg = a.waveConfig.surface
    for pass = 0 to 1
        weight = 1 - wave.blend
        index = wave.first
        if pass = 1 then weight = wave.blend : index = wave.second
        color = ReefRGBA(255, 236, 223, Int(weight * (160 + 75 * s.lighting[0])))
        for tile = 0 to 4
            ReefDraw(r, -512 + tile * 512 - s.camera, -8, cfg.scale, 1, a.surface[index], color)
        end for
    end for
end sub

sub ReefDrawCaustics(r as object, s as object, a as object)
    if a.caustics.Count() = 0 then return
    wave = ReefSurface(s.displayTime)
    cfg = a.waveConfig.sand
    for pass = 0 to 1
        weight = 1 - wave.blend
        index = wave.first
        if pass = 1 then weight = wave.blend : index = wave.second
        ReefDraw(r, cfg.x - s.camera, cfg.y - 36, cfg.scale, cfg.scale, a.caustics[index], ReefRGBA(255, 240, 215, Int(weight * 225 * s.quality * s.lighting[0])))
    end for
end sub

sub ReefRender(r as object, s as object, a as object)
    screen = r.screen
    screen.SetAlphaEnable(false)
    screen.Clear(&h182A42FF)
    ReefDraw(r, -s.camera, -36, 1, 1, a.plate, &hFFFFFFFF)
    screen.SetAlphaEnable(true)
    ' Stable insertion sort of references, not copied fish. Persistent list has bounded length.
    if s.sorted = invalid then s.sorted = []
    s.sorted.Clear()
    for fishIndex = 0 to s.fish.Count() - 1
        f = s.fish[fishIndex]
        f.renderPose = ReefDisplayPose(f, s.renderAlpha)
        s.sorted.Push(f)
        j = s.sorted.Count() - 1
        while j > 0
            previousPose = s.sorted[j - 1].renderPose
            currentPose = f.renderPose
            if previousPose.z <= currentPose.z then exit while
            s.sorted[j] = s.sorted[j - 1] : j = j - 1
        end while
        s.sorted[j] = f
    end for
    i = 0 : previousDepth = 0#
    reefTint = &hFFFFFFFF
    if s.settings.lighting <> "Sunset" then reefTint = &hDDEBFFFF
    for formationIndex = 0 to s.cfg.formations.Count() - 1
        formation = s.cfg.formations[formationIndex]
        ReefDrawEffects(r, s, a, previousDepth, formation.z)
        previousDepth = formation.z
        while i < s.sorted.Count()
            pose = s.sorted[i].renderPose
            if pose.z >= formation.z then exit while
            ReefDrawFish(r, s, a, s.sorted[i]) : i = i + 1
        end while
        offset = 64 + (s.camera - 64) * formation.parallax
        sway = 0# : widthScale = 1#
        if formation.id = "white-crown"
            sway = Sin(ReefWrap(s.displayTime,18#)*6.283185307/18#) * 0.7
            widthScale = 1 + sway * 0.0015
        end if
        ReefDraw(r, formation.x - offset + sway - formation.width*(widthScale-1)*0.5, formation.y - 36, widthScale, 1, a.formations[formationIndex], reefTint)
    end for
    ReefDrawCaustics(r, s, a)
    while i < s.sorted.Count()
        ReefDrawFish(r, s, a, s.sorted[i]) : i = i + 1
    end while
    ReefDrawEffects(r, s, a, previousDepth, 1.01)
    for k = 0 to 2
        ReefDraw(r, 150 + k * 590 + Sin(s.displayTime * 0.07 + k) * 24 - s.camera * 0.25, -70, 2.0, 1.8, a.ray, ReefRGBA(255, 223, 210, Int((65 + 18 * Sin(s.displayTime * 0.13 + k)) * s.lighting[0])))
    end for
    ReefDrawSurface(r, s, a)
    if s.lighting[2] > 0 then screen.DrawRect(0, 0, screen.GetWidth(), screen.GetHeight(), ReefRGBA(8, 16, 57, Int(s.lighting[2])))
    if s.lighting[3] > 0 then screen.DrawRect(0, 0, screen.GetWidth(), screen.GetHeight(), ReefRGBA(241, 105, 108, Int(s.lighting[3])))
    if s.settings.clock = "On" then screen.DrawText(s.clockText, Int(1660 * r.scale), Int(970 * r.scale), &hF6DFD4B0, r.font)
    if s.settings.fps = "On" then screen.DrawText(Int(s.fps).ToStr() + " FPS", Int(110 * r.scale), Int(95 * r.scale), &hF6DFD4D0, r.font)
end sub
