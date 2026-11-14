' Every texture is loaded once. Missing decorative assets become transparent; fish can be skipped.
function ReefBitmap(path as string) as dynamic
    bitmap = CreateObject("roBitmap", path)
    if bitmap = invalid then print "Deep Reef: could not load "; path
    return bitmap
end function

function ReefLoadAssets(s as object) as object
    warm = s.settings.lighting = "Sunset"
    plate = "water-day.webp"
    if warm then plate = "water-sunset.webp"
    a = { plate: ReefLayer(ReefBitmap("pkg:/images/" + plate)), mid: ReefLayer(ReefBitmap("pkg:/images/reef-mid.webp")), front: ReefLayer(ReefBitmap("pkg:/images/reef-front.webp")), mote: ReefLayer(ReefBitmap("pkg:/images/mote.png")), bubble: ReefLayer(ReefBitmap("pkg:/images/bubble.png")), ray: ReefLayer(ReefBitmap("pkg:/images/ray.png")), coral: [], caustics: [], fish: {}, fins: {}, surface: [] }
    a.waveConfig = ParseJson(ReadAsciiFile("pkg:/scenes/waves.json"))
    surface = ReefBitmap("pkg:/images/surface-waves.png")
    sand = ReefBitmap("pkg:/images/sand-caustics.png")
    if a.waveConfig <> invalid
        for i = 0 to a.waveConfig.frames - 1
            if surface <> invalid
                cfg = a.waveConfig.surface
                a.surface.Push(ReefLayer(surface, (i mod cfg.columns) * cfg.width, Int(i / cfg.columns) * cfg.height, cfg.width, cfg.height))
            end if
            if sand <> invalid
                cfg = a.waveConfig.sand
                a.caustics.Push(ReefLayer(sand, (i mod cfg.columns) * cfg.width, Int(i / cfg.columns) * cfg.height, cfg.width, cfg.height))
            end if
        end for
    end if
    cfg = s.cfg.softCoral
    b = ReefBitmap(cfg.image)
    if b <> invalid
        for i = 0 to cfg.frames - 1
            a.coral.Push(ReefLayer(b, i * cfg.frameWidth, 0, cfg.frameWidth, cfg.frameHeight))
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

' Two immutable regions share one bitmap; no second texture is allocated.
function ReefLayer(bitmap as dynamic, x = 0 as integer, y = 0 as integer, width = -1 as integer, height = -1 as integer) as dynamic
    if bitmap = invalid then return invalid
    if width < 0 then width = bitmap.GetWidth()
    if height < 0 then height = bitmap.GetHeight()
    normal = CreateObject("roRegion", bitmap, x, y, width, height)
    fractional = CreateObject("roRegion", bitmap, x, y, width, height)
    if normal = invalid or fractional = invalid then return invalid
    normal.SetScaleMode(1)
    fractional.SetScaleMode(1)
    fractional.SetPretranslation(65536, 65536)
    return {normal:normal, fractional:fractional}
end function
