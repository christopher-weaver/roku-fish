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
    a = { plate: ReefLayer(ReefBitmap("pkg:/images/" + plate)), formations: [], marineBands: [], marineBandHeights: [], mote: ReefLayer(ReefBitmap("pkg:/images/mote.png")), bubble: ReefLayer(ReefBitmap("pkg:/images/bubble.png")), ray: ReefLayer(ReefBitmap("pkg:/images/ray.png")), caustics: [], fish: {}, fins: {}, tails: {}, sandShadows: [], surface: [] }
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
        bitmap=ReefBitmap(cfg.image) : views=[]
        for view=0 to cfg.frames-1
            views.Push(ReefLayer(bitmap,(view mod cfg.columns)*cfg.frameWidth,Int(view/cfg.columns)*cfg.frameHeight,cfg.frameWidth,cfg.frameHeight))
        end for
        a.formations.Push(views)
        bands=[] : bandHeight=8
        if cfg.motion<>invalid
            bandHeight=cfg.motion.bandHeight
            if s.settings.quality="Performance" then bandHeight=bandHeight*2
            for view=0 to cfg.frames-1
                metadata=[] : bandY=0
                while bandY<cfg.frameHeight
                    height=Int(ReefMin(bandHeight,cfg.frameHeight-bandY))
                    metadata.Push({x:(view mod cfg.columns)*cfg.frameWidth,y:Int(view/cfg.columns)*cfg.frameHeight+bandY,w:cfg.frameWidth,h:height,anchorX:cfg.frameWidth/2#,anchorY:0#})
                    bandY=bandY+height
                end while
                bands.Push(ReefFishFrames(bitmap,metadata,s.settings.quality))
            end for
        end if
        a.marineBands.Push(bands) : a.marineBandHeights.Push(bandHeight)
    end for
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
