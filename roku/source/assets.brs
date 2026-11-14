' Every texture is loaded once. Missing decorative assets become transparent; fish can be skipped.
function ReefBitmap(path as string) as dynamic
    bitmap = CreateObject("roBitmap", path)
    if bitmap = invalid then print "Deep Reef: could not load "; path
    return bitmap
end function

function ReefLoadAssets(s as object) as object
    warm = s.settings.lighting = "Sunset"
    suffix = ""
    plate = "water-day.webp"
    if warm then suffix = "-sunset" : plate = "water-sunset.webp"
    a = { plate: ReefBitmap("pkg:/images/" + plate), mid: ReefBitmap("pkg:/images/reef-mid" + suffix + ".webp"), front: ReefBitmap("pkg:/images/reef-front" + suffix + ".webp"), mote: ReefBitmap("pkg:/images/mote.png"), bubble: ReefBitmap("pkg:/images/bubble.png"), ray: ReefBitmap("pkg:/images/ray.png"), coral: [], caustics: [], fish: {}, fins: {}, surface: [] }
    a.waveConfig = ParseJson(ReadAsciiFile("pkg:/scenes/waves.json"))
    surface = ReefBitmap("pkg:/images/surface-waves.png")
    sand = ReefBitmap("pkg:/images/sand-caustics.png")
    if a.waveConfig <> invalid
        for i = 0 to a.waveConfig.frames - 1
            if surface <> invalid
                cfg = a.waveConfig.surface
                reg = CreateObject("roRegion", surface, (i mod cfg.columns) * cfg.width, Int(i / cfg.columns) * cfg.height, cfg.width, cfg.height)
                reg.SetScaleMode(1)
                a.surface.Push(reg)
            end if
            if sand <> invalid
                cfg = a.waveConfig.sand
                reg = CreateObject("roRegion", sand, (i mod cfg.columns) * cfg.width, Int(i / cfg.columns) * cfg.height, cfg.width, cfg.height)
                reg.SetScaleMode(1)
                a.caustics.Push(reg)
            end if
        end for
    end if
    b = ReefBitmap("pkg:/images/soft-coral" + suffix + ".png")
    if b <> invalid
        for i = 0 to 2
            a.coral.Push(CreateObject("roRegion", b, i * 350, 0, 350, 370))
        end for
    end if
    for each name in s.species
        sp = s.species[name]
        b = ReefBitmap(sp.image)
        if b <> invalid
            frames = []
            for each frame in sp.frames
                reg = CreateObject("roRegion", b, frame.x, frame.y, frame.w, frame.h)
                reg.SetPretranslation(-frame.anchorX, -frame.anchorY)
                if s.settings.quality <> "Performance" then reg.SetScaleMode(1)
                frames.Push(reg)
            end for
            a.fish[name] = frames
        end if
        b = ReefBitmap(sp.finImage)
        if b <> invalid
            frames = []
            for each frame in sp.finFrames
                reg = CreateObject("roRegion", b, frame.x, frame.y, frame.w, frame.h)
                reg.SetPretranslation(-frame.anchorX, -frame.anchorY)
                if s.settings.quality <> "Performance" then reg.SetScaleMode(1)
                frames.Push(reg)
            end for
            a.fins[name] = frames
        end if
    end for
    return a
end function
