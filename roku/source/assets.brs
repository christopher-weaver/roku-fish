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
    a = { plate: ReefBitmap("pkg:/images/" + plate), mid: ReefBitmap("pkg:/images/reef-mid" + suffix + ".png"), front: ReefBitmap("pkg:/images/reef-front" + suffix + ".png"), mote: ReefBitmap("pkg:/images/mote.png"), bubble: ReefBitmap("pkg:/images/bubble.png"), ray: ReefBitmap("pkg:/images/ray.png"), coral: [], caustics: [], fish: {} }
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
                reg.SetPretranslation(-sp.frameW / 2, -sp.frameH / 2)
                frames.Push(reg)
            end for
            a.fish[name] = frames
        end if
    end for
    return a
end function
