' Every texture is loaded once. Missing decorative assets become transparent; fish can be skipped.
function ReefBitmap(path as string) as dynamic
    bitmap = CreateObject("roBitmap", path)
    if bitmap = invalid then print "Deep Reef: could not load "; path
    return bitmap
end function

function ReefLoadAssets(s as object) as object
    warm = s.settings.lighting = "Sunset"
    suffix = ""
    plate = "water-day.jpg"
    if warm then suffix = "-sunset" : plate = "water-sunset.jpg"
    a = { plate: ReefBitmap("pkg:/images/" + plate), mid: ReefBitmap("pkg:/images/reef-mid" + suffix + ".webp"), front: ReefBitmap("pkg:/images/reef-front" + suffix + ".webp"), mote: ReefBitmap("pkg:/images/mote.png"), bubble: ReefBitmap("pkg:/images/bubble.png"), ray: ReefBitmap("pkg:/images/ray.png"), coral: [], caustics: [], fish: {}, fins: {}, surface: [], dapple: [] }
    a.dappleConfig = ParseJson(ReadAsciiFile("pkg:/scenes/dapple.json"))
    dapple = ReefBitmap("pkg:/images/sun-dapple.png")
    if dapple <> invalid and a.dappleConfig <> invalid
        for frameIndex = 0 to a.dappleConfig.frames - 1
            patches = []
            for patch = 0 to a.dappleConfig.positions.Count() - 1
                reg = CreateObject("roRegion", dapple, patch * 128, frameIndex * 96, 128, 96)
                reg.SetScaleMode(1)
                patches.Push(reg)
            end for
            a.dapple.Push(patches)
        end for
    end if
    surface = ReefBitmap("pkg:/images/surface-ripples.png")
    if surface <> invalid
        for i = 0 to 11
            a.surface.Push(CreateObject("roRegion", surface, (i mod 4) * 512, Int(i / 4) * 80, 512, 80))
        end for
    end if
    b = ReefBitmap("pkg:/images/soft-coral" + suffix + ".png")
    if b <> invalid
        for i = 0 to 2
            a.coral.Push(CreateObject("roRegion", b, i * 350, 0, 350, 370))
        end for
    end if
    for i = 0 to 7
        b = ReefBitmap("pkg:/images/caustic-" + i.ToStr() + ".png")
        if b <> invalid then a.caustics.Push(b)
    end for
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
