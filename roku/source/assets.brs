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
    water=ReefBitmap("pkg:/images/"+plate)
    a = { plate: ReefLayer(water), formations: [], netShadows: [], mote: ReefLayer(ReefBitmap("pkg:/images/mote.png")), bubble: ReefLayer(ReefBitmap("pkg:/images/bubble.png")), ray: ReefLayer(ReefBitmap("pkg:/images/ray.png")), caustics: [], fish: {}, fins: {}, tails: {}, sandShadows: [], surface: [] }
    a.waveConfig = ParseJson(ReadAsciiFile("pkg:/scenes/waves.json"))
    surface = ReefBitmap("pkg:/images/surface-waves.png")
    shadow = ReefBitmap("pkg:/images/sand-wave-shadows.png")
    sand = ReefBitmap("pkg:/images/sand-caustics.png")
    if a.waveConfig <> invalid
        for i = 0 to a.waveConfig.frames - 1
            if surface <> invalid
                cfg = a.waveConfig.surface
                a.surface.Push(ReefLayer(surface, (i mod cfg.columns) * cfg.width, Int(i / cfg.columns) * cfg.height, cfg.width, cfg.height))
            end if
            if shadow <> invalid
                cfg = a.waveConfig.shadow
                a.sandShadows.Push(ReefLayer(shadow, (i mod cfg.columns) * cfg.width, Int(i / cfg.columns) * cfg.height, cfg.width, cfg.height))
            end if
            if sand <> invalid
                cfg = a.waveConfig.sand
                a.caustics.Push(ReefLayer(sand, (i mod cfg.columns) * cfg.width, Int(i / cfg.columns) * cfg.height, cfg.width, cfg.height))
            end if
        end for
    end if
    for index = 0 to s.cfg.formations.Count() - 1
        cfg = s.cfg.formations[index]
        views=[] : pages=[]
        if cfg.animation<>invalid
            for pageIndex=0 to cfg.images.Count()-1
                pages.Push(ReefBitmap(cfg.images[pageIndex]))
            end for
            for pose=0 to cfg.frames-1
                pageIndex=Int(pose/cfg.animation.framesPerPage)
                local=pose mod cfg.animation.framesPerPage
                x=cfg.animation.gutter+(local mod cfg.columns)*cfg.animation.strideX
                y=cfg.animation.gutter+Int(local/cfg.columns)*cfg.animation.strideY
                views.Push(ReefLayer(pages[pageIndex],x,y,cfg.frameWidth,cfg.frameHeight))
            end for
        else
            bitmap=ReefBitmap(cfg.image)
            for view=0 to cfg.frames-1
                views.Push(ReefLayer(bitmap,(view mod cfg.columns)*cfg.frameWidth,Int(view/cfg.columns)*cfg.frameHeight,cfg.frameWidth,cfg.frameHeight))
            end for
        end if
        a.formations.Push(views)
    end for
    eel=ReefBitmap("pkg:/images/cave-eel.webp")
    if eel<>invalid then a.eel=ReefFishFrames(eel,[{x:0,y:0,w:114,h:140,anchorX:57,anchorY:140}],s.settings.quality)[0]
    a.cave=ReefLayer(ReefBitmap("pkg:/images/cave-interior.png"))
    a.eelErase=ReefLayer(water,680,907,190,245)
    net=ReefBitmap("pkg:/images/wave-net.webp")
    if net<>invalid
        for i=0 to 31
            a.netShadows.Push(ReefLayer(net,(i mod 8)*132+2,Int(i/8)*132+2,128,128))
        end for
    end if
    ' Load only the unique species present at this density.
    for fishIndex=0 to s.fish.Count()-1
        name=s.fish[fishIndex].name
        sp = s.species[name]
        b = ReefBitmap(sp.image)
        if b <> invalid then a.fish[name] = ReefFishFrames(b,sp.frames,s.settings.quality)
        b = ReefBitmap(sp.tailImage)
        if b <> invalid then a.tails[name] = ReefFishFrames(b,sp.tailFrames,s.settings.quality)
        b = ReefBitmap(sp.finImage)
        if b <> invalid then a.fins[name] = ReefFishFrames(b,sp.finFrames,s.settings.quality)
    end for
    return a
end function

' Two immutable regions share one bitmap; no second texture is allocated.
function ReefLayer(bitmap as dynamic, x = 0 as integer, y = 0 as integer, width = -1 as integer, height = -1 as integer) as dynamic
    if bitmap = invalid then return invalid
    if width < 0 then width = bitmap.GetWidth()
    if height < 0 then height = bitmap.GetHeight()
    normal = CreateObject("roRegion", bitmap, x, y, width, height)
    if normal=invalid then return invalid
    normal.SetScaleMode(1)
    return {normal:normal}
end function


function ReefFishFrames(bitmap as object, metadata as object, quality as string) as object
    frames = [] : cache = {}
    for index = 0 to metadata.Count()-1
        frame = metadata[index]
        key = frame.x.ToStr()+":"+frame.y.ToStr()
        if not cache.DoesExist(key)
            reg = CreateObject("roRegion",bitmap,frame.x,frame.y,frame.w,frame.h)
            reg.SetPretranslation(0-Int(frame.anchorX),0-Int(frame.anchorY))
            if quality <> "Performance" then reg.SetScaleMode(1)
            fractional = CreateObject("roRegion",bitmap,frame.x,frame.y,frame.w,frame.h)
            fractional.SetPretranslation(4096-Int(frame.anchorX),4096-Int(frame.anchorY))
            fractional.SetScaleMode(1)
            cache[key] = {normal:reg,fractional:fractional,offsetX:Int(frame.anchorX)-frame.anchorX,offsetY:Int(frame.anchorY)-frame.anchorY}
        end if
        frames.Push(cache[key])
    end for
    return frames
end function
