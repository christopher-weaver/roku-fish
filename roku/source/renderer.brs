function ReefRenderer(screen as object, settings as object) as object
    outputScale = screen.GetWidth() / 1920#
    r = {screen:screen, output:screen, scale:outputScale, outputScale:outputScale, rotation:false, font:invalid, placement:{}, canvasOffset:0#, frame:invalid}
    features = screen.GetGraphicsFeatures()
    if features <> invalid and features.full_rotation = true then r.rotation = true
    fonts = CreateObject("roFontRegistry")
    r.font = fonts.GetDefaultFont(Int(24 * outputScale),false,false)
    ' Render once into an opaque overscan canvas, then interpolate two adjacent
    ' integer screen positions. No oversized anchors or scale-rounding pan jumps.
    canvas = CreateObject("roBitmap",{width:2048,height:1080,alphaenable:true})
    if canvas <> invalid
        r.frame = CreateObject("roRegion",canvas,0,0,2048,1080)
        r.frame.SetScaleMode(1)
        r.screen = canvas : r.scale = 1#
    end if
    r.fractionalFish = ReefFractionalFishProbe(r.screen,r.rotation)
    print "Deep Reef opaque pan canvas=";(r.frame<>invalid);" fractional fish=";r.fractionalFish
    return r
end function

sub ReefDraw(r as object, x as double, y as double, sx as double, sy as double, bmp as dynamic, tint as integer)
    if bmp = invalid then return
    region = bmp
    if Type(bmp) = "roAssociativeArray" then region = bmp.normal
    targetX=Int((x+r.canvasOffset)*r.scale+0.5)
    targetY=Int(y*r.scale+0.5)
    if Abs(sx*r.scale-1)<0.000001 and Abs(sy*r.scale-1)<0.000001
        r.screen.DrawObject(targetX,targetY,region,tint)
    else
        r.screen.DrawScaledObject(targetX,targetY,sx*r.scale,sy*r.scale,region,tint)
    end if
end sub

sub ReefDrawFish(r as object, s as object, a as object, f as object)
    frames = a.fish[f.name]
    if frames = invalid then return
    f.swimPose=ReefSwimPose(f.renderPose,f.sp,f.speed,f.swimPose)
    pose = f.swimPose
    f.screenPose = ReefProjection(pose,s.camera,f.screenPose)
    p = f.screenPose
    if p.x < -200 or p.x > 2120 then return
    f.renderView = ReefFishView(pose.heading,f.sp,f.renderView)
    view = f.renderView
    f.bodyView=ReefBodyView(pose.heading,f.sp,f.bodyView)
    bodyPosition = (Sin(pose.phase)+1)*0.5*(f.sp.poseCount-1)
    tailPosition = (Sin(pose.phase)+1)*0.5*(f.sp.tailPoseCount-1)
    finPosition = (Sin(pose.finPhase)+1)*0.5*(f.sp.finPoseCount-1)
    scale = p.scale*f.sp.length/f.sp.renderLength*f.size
    haze = 1-pose.z
    red = Int(255-haze*65) : green = Int(247-haze*32) : blue = 255
    if s.settings.lighting = "Sunset" then red=255 : green=Int(239-haze*25) : blue=Int(240-haze*10)
    light=ReefSurfaceShade(pose.x,pose.y+(1-pose.z)*30+36,s.displayTime)
    light=1#-(1#-light)*.30*(.35+.65*s.lighting[0])
    red=Int(red*light) : green=Int(green*light) : blue=Int(blue*light)
    angle = pose.pitch*57.29578
    if Cos(pose.heading)<0 then angle=0#-angle
    ReefDrawFishPart(r,p,f.sp,frames,bodyPosition,f.sp.poseCount,f.bodyView,scale,angle,red,green,blue)
    if a.tails[f.name]<>invalid then ReefDrawFishPart(r,p,f.sp,a.tails[f.name],tailPosition,f.sp.tailPoseCount,view,scale,angle,red,green,blue)
    if a.fins[f.name]<>invalid then ReefDrawFishPart(r,p,f.sp,a.fins[f.name],finPosition,f.sp.finPoseCount,view,scale*f.sp.finTextureScale,angle,red,green,blue)
end sub

sub ReefDrawFishPart(r as object,p as object,sp as object,frames as object,position as double,count as integer,view as object,scale as double,angle as double,red as integer,green as integer,blue as integer)
    ' Body excludes caudal-tail geometry. One tail and one pectoral image
    ' complete the fish; no crossfades, duplicate anatomy or reflections.
    poseIndex=Int(position+0.5)
    yaw=view.index
    sx=scale*view.width/view.sourceWidth
    ReefDrawFishRegion(r,p.x,p.y,sx,scale,angle,frames[yaw*count+poseIndex],ReefRGBA(red,green,blue,255))
end sub

sub ReefDrawFishRegion(r as object, x as double, y as double, sx as double, sy as double, angle as double, region as object, tint as integer)
    x = x + r.canvasOffset
    if not r.rotation then angle = 0#
    if region.offsetX<>invalid
        c=Cos(angle/57.295779513#) : sn=Sin(angle/57.295779513#)
        x=x+c*sx*region.offsetX+sn*sy*region.offsetY
        y=y+c*sy*region.offsetY-sn*sx*region.offsetX
    end if
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

sub ReefDrawEffects(r as object, s as object, a as object, lo as double, hi as double, band = -1 as integer)
    particles = 24 : bubbles = 6
    if s.settings.particles = "Off" then particles = 0
    if s.settings.particles = "Medium" then particles = 48
    if s.settings.bubbles = "Off" then bubbles = 0
    if s.settings.bubbles = "Medium" then bubbles = 12
    effects = s.effects
    if band>=0 and s.effectBands<>invalid then effects=s.effectBands[band]
    for each e in effects
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

sub ReefDrawSandShadows(r as object, s as object, a as object)
    if a.sandShadows=invalid then return
    if a.sandShadows.Count()=0 then return
    wave=ReefSurface(s.displayTime) : cfg=a.waveConfig.shadow
    for pass=0 to 1
        weight=1-wave.blend : index=wave.first
        if pass=1 then weight=wave.blend : index=wave.second
        ReefDraw(r,cfg.x-s.camera,cfg.y-36,cfg.scale,cfg.scale,a.sandShadows[index],ReefRGBA(255,255,255,Int(weight*255*(0.25+0.75*s.lighting[0]))))
    end for
end sub

sub ReefDrawEel(r as object,s as object,a as object)
    if a.eels=invalid then return
    cfg=a.eelConfig
    shade=ReefSurfaceShade(773#,858#,s.displayTime)
    light=Int(255*(1#-(1#-shade)*.30*(.35+.65*s.lighting[0])))
    ' Cave walls, closed rear chamber, and the animal were depth-tested together.
    ReefDrawFishRegion(r,cfg.x-s.camera,cfg.y-36,1#,1#,0#,a.eels[ReefEelFrame(s.displayTime)],ReefRGBA(light,light,light,255))
end sub

sub ReefDrawSurfaceShadow(r as object,s as object,a as object,index as integer,formation as object)
    if a.surfaceShadows=invalid then return
    if a.surfaceShadows[index].Count()=0 then return
    cfg=formation.surfaceShadow : wave=ReefSurface(s.displayTime)
    for pass=0 to 1
        weight=1-wave.blend : phase=wave.first
        if pass=1 then weight=wave.blend : phase=wave.second
        ReefDraw(r,0#-s.camera,0#-36#,cfg.scale,cfg.scale,a.surfaceShadows[index][phase],ReefRGBA(255,255,255,Int(weight*255*.65*(.35+.65*s.lighting[0]))))
    end for
end sub

sub ReefRender(r as object, s as object, a as object)
    screen = r.screen
    r.canvasOffset = 0#
    if r.frame<>invalid then r.canvasOffset=s.camera
    screen.SetAlphaEnable(false)
    screen.Clear(&h182A42FF)
    ReefDraw(r, -s.camera, -36, 1, 1, a.plate, &hFFFFFFFF)
    screen.SetAlphaEnable(true)
    floorTint=&hFFFFFFFF
    if s.settings.lighting<>"Sunset" then floorTint=&hDDEBFFFF
    if a.floor<>invalid then ReefDraw(r,0#-s.camera,920#-36#,1#,1#,a.floor,floorTint)
    ' Stable insertion sort of references, not copied fish. Persistent list has bounded length.
    if s.sorted = invalid then s.sorted = []
    s.sorted.Clear()
    for fishIndex = 0 to s.fish.Count() - 1
        f = s.fish[fishIndex]
        f.renderPose = ReefDisplayPose(f,s.renderAlpha,f.renderPose)
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
        ReefDrawEffects(r,s,a,previousDepth,formation.z,formationIndex)
        previousDepth = formation.z
        while i < s.sorted.Count()
            pose = s.sorted[i].renderPose
            if pose.z >= formation.z then exit while
            ReefDrawFish(r, s, a, s.sorted[i]) : i = i + 1
        end while
        offset = 64 + (s.camera - 64) * formation.parallax
        marineView=0
        if formation.animation<>invalid then marineView=ReefMarineFrame(s.displayTime,formation)
        light=ReefSurfaceShade(formation.x+formation.width*.5,formation.y+formation.height*.45,s.displayTime)
        strength=.35
        if formation.animation<>invalid then strength=1#
        light=1#-(1#-light)*strength*(.35+.65*s.lighting[0])
        red=255 : green=255 : blue=255
        if s.settings.lighting<>"Sunset" then red=221 : green=235
        tint=ReefRGBA(Int(red*light),Int(green*light),Int(blue*light),255)
        ReefDraw(r,formation.x-offset,formation.y-36,formation.width/formation.frameWidth,formation.height/formation.frameHeight,a.formations[formationIndex][marineView],tint)
        ReefDrawSurfaceShadow(r,s,a,formationIndex,formation)
        if formation.id="connected-reef" then ReefDrawEel(r,s,a)
    end for
    ReefDrawCaustics(r, s, a)
    ReefDrawSandShadows(r, s, a)
    while i < s.sorted.Count()
        ReefDrawFish(r, s, a, s.sorted[i]) : i = i + 1
    end while
    ReefDrawEffects(r,s,a,previousDepth,1.01,s.cfg.formations.Count())
    for k = 0 to 2
        ReefDraw(r, 150 + k * 590 + Sin(s.displayTime * 0.07 + k) * 24 - s.camera * 0.25, -70, 2.0, 1.8, a.ray, ReefRGBA(255, 223, 210, Int((65 + 18 * Sin(s.displayTime * 0.13 + k)) * s.lighting[0])))
    end for
    ReefDrawSurface(r, s, a)
    if s.lighting[2] > 0 then screen.DrawRect(0, 0, screen.GetWidth(), screen.GetHeight(), ReefRGBA(8, 16, 57, Int(s.lighting[2])))
    if s.lighting[3] > 0 then screen.DrawRect(0, 0, screen.GetWidth(), screen.GetHeight(), ReefRGBA(241, 105, 108, Int(s.lighting[3])))
    if r.output<>invalid then ReefPresent(r,s)
end sub

sub ReefPresent(r as object,s as object)
    screen = r.output
    if r.frame<>invalid
        phase = ReefPixelPhase(0#-s.camera*r.outputScale)
        screen.SetAlphaEnable(false)
        screen.Clear(&h182A42FF)
        if r.outputScale=1
            screen.DrawObject(phase.first,0,r.frame,&hFFFFFFFF)
        else
            screen.DrawScaledObject(phase.first,0,r.outputScale,r.outputScale,r.frame,&hFFFFFFFF)
        end if
        if phase.blend>0.001
            screen.SetAlphaEnable(true)
            color=ReefRGBA(255,255,255,Int(phase.blend*255+0.5))
            if r.outputScale=1
                screen.DrawObject(phase.first+1,0,r.frame,color)
            else
                screen.DrawScaledObject(phase.first+1,0,r.outputScale,r.outputScale,r.frame,color)
            end if
        end if
    end if
    screen.SetAlphaEnable(true)
    if s.settings.clock="On" then screen.DrawText(s.clockText,Int(1660*r.outputScale),Int(970*r.outputScale),&hF6DFD4B0,r.font)
    if s.settings.fps="On" then screen.DrawText(Int(s.fps).ToStr()+" FPS",Int(110*r.outputScale),Int(95*r.outputScale),&hF6DFD4D0,r.font)
end sub
