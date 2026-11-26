function ReefRenderer(screen as object, settings as object) as object
    outputScale = screen.GetWidth() / 1920#
    r = {screen:screen, output:screen, scale:outputScale, outputScale:outputScale, rotation:false, font:invalid, placement:{}, canvasOffset:0#, frame:invalid}
    features = screen.GetGraphicsFeatures()
    if features <> invalid and features.full_rotation = true then r.rotation = true
    fonts = CreateObject("roFontRegistry")
    r.font = fonts.GetDefaultFont(Int(24 * outputScale),false,false)
    ' Render once into an opaque overscan canvas, then interpolate two adjacent
    ' integer screen positions. No oversized anchors or scale-rounding pan jumps.
    layout=ReefCanvasLayout(screen.GetWidth(),screen.GetHeight())
    r.canvasWidth=0 : r.canvasHeight=0
    canvas = CreateObject("roBitmap",{width:layout.width,height:layout.height,alphaenable:true})
    if canvas <> invalid
        r.frame = CreateObject("roRegion",canvas,0,0,layout.width,layout.height)
        r.frame.SetScaleMode(1)
        r.screen = canvas : r.scale = layout.scale
        r.canvasWidth=layout.width : r.canvasHeight=layout.height
    end if
    r.fractionalFish = ReefFractionalFishProbe(r.screen,r.rotation)
    print "Deep Reef canvas=";r.canvasWidth;"x";r.canvasHeight;" output=";screen.GetWidth();"x";screen.GetHeight();" fractional fish=";r.fractionalFish
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
    r.waveSinPhase=Sin(pose.phase) : r.waveCosPhase=0#
    if f.sp.swimAxis<>"lateral" then r.waveCosPhase=Cos(pose.phase)
    bodyPosition = (r.waveSinPhase+1)*0.5*(f.sp.poseCount-1)
    tailPosition = (r.waveSinPhase+1)*0.5*(f.sp.tailPoseCount-1)
    if f.sp.swimAxis="lateral" then tailPosition=(1#-r.waveSinPhase)*.5*(f.sp.tailPoseCount-1)
    finPosition = (Sin(pose.finPhase)+1)*0.5*(f.sp.finPoseCount-1)
    scale = p.scale*f.sp.length/f.sp.renderLength*f.size
    haze = 1-pose.z
    red = Int(255-haze*65) : green = Int(247-haze*32) : blue = 255
    if s.settings.lighting = "Sunset" then red=255 : green=Int(239-haze*25) : blue=Int(240-haze*10)
    light=ReefSurfaceShade(pose.x,pose.y+(1-pose.z)*30+36,s.displayTime)
    light=1#-(1#-light)*.30*(.35+.65*s.lighting[0])
    red=Int(red*light) : green=Int(green*light) : blue=Int(blue*light)
    angle = pose.pitch*57.29578
    headingCos=Cos(pose.heading) : r.waveHeadingCos=headingCos : r.waveSign=1#
    if headingCos<0 then angle=0#-angle : r.waveSign=0#-1#
    r.waveBaseCos=Cos(angle/57.295779513#) : r.waveBaseSin=Sin(angle/57.295779513#)
    r.wavePhase=pose.phase : r.waveHeading=pose.heading
    r.waveStanding=f.sp.bodyRenderMode="whole-swim"
    if r.waveStanding
        r.waveAmplitude=f.sp.length*f.size*p.scale*f.sp.bodySwimAmplitude*Abs(headingCos)
        r.waveLateral=f.sp.swimAxis="lateral"
        if r.waveLateral
            r.waveAmplitude=0# : r.waveHeadingSin=0#
            if f.sp.finSwimOffset<>0# then r.waveHeadingSin=Sin(pose.heading)
        end if
        if a.tails[f.name]<>invalid then ReefDrawBoundTail(r,p,f.sp,a.tails[f.name],tailPosition,view,f.bodyView,scale,angle,red,green,blue)
        ReefDrawWholeBody(r,p,f.sp,frames,bodyPosition,f.bodyView,scale,angle,red,green,blue)
    else
        effort=.6
        if f.speed<>invalid then effort=ReefClamp(f.speed/f.sp.speed,0#,1#)
        r.waveAmplitude=f.sp.length*f.size*p.scale*.012*(.25+.75*effort)*Abs(headingCos)
        ReefDrawFishPart(r,p,f.sp,frames,bodyPosition,f.sp.poseCount,f.bodyView,scale,angle,red,green,blue)
    end if
    if not r.waveStanding and a.tails[f.name]<>invalid then ReefDrawFishPart(r,p,f.sp,a.tails[f.name],tailPosition,f.sp.tailPoseCount,view,scale,angle,red,green,blue)
    if a.fins[f.name]<>invalid then ReefDrawFishPart(r,p,f.sp,a.fins[f.name],finPosition,f.sp.finPoseCount,view,scale*f.sp.finTextureScale,angle,red,green,blue)
end sub

 ' Bilinear phase/yaw weights, normalized for source-over with an opaque base.
sub ReefDrawWholeBody(r as object,p as object,sp as object,frames as object,position as double,view as object,scale as double,angle as double,red as integer,green as integer,blue as integer)
    first=Int(position) : second=first+1
    if second>=sp.poseCount then second=first
    phase=position-first : yaw=view.blend
    ' Complete body regions share their position, pitch and tint. Submit them
    ' directly instead of repeating the generic appendage setup for every layer.
    firstBase=view.first*sp.poseCount : secondBase=view.second*sp.poseCount
    firstScale=scale*view.width/sp.bodyViewWidths[view.first]
    secondScale=scale*view.width/sp.bodyViewWidths[view.second]
    tint=ReefRGBA(red,green,blue,0)
    ReefDrawFishRegion(r,p.x,p.y,firstScale,scale,angle,frames[firstBase+first],tint or 255)
    opacity=Int(255#*phase+.5)
    if opacity>0 and second<>first then ReefDrawFishRegion(r,p.x,p.y,firstScale,scale,angle,frames[firstBase+second],tint or opacity)
    denominator=1#-yaw*phase
    opacity=0
    if denominator>.0000001 then opacity=Int(255#*yaw*(1#-phase)/denominator+.5)
    if opacity>0 then ReefDrawFishRegion(r,p.x,p.y,secondScale,scale,angle,frames[secondBase+first],tint or opacity)
    opacity=Int(255#*yaw*phase+.5)
    if opacity>0 then ReefDrawFishRegion(r,p.x,p.y,secondScale,scale,angle,frames[secondBase+second],tint or opacity)
end sub

 ' The caudal root stays fixed while its texture envelope changes at the tip.
sub ReefDrawBoundTail(r as object,p as object,sp as object,frames as object,position as double,view as object,body as object,scale as double,angle as double,red as integer,green as integer,blue as integer)
    ReefTailRigInit(sp)
    pose=Int(position+.5) : index=view.index*sp.tailPoseCount+pose
    region=frames[index] : source=sp.tailSourcePoints[index]
    sx=scale*view.width/view.sourceWidth : sy=scale
    if region.anchorX<>invalid
        warp=ReefAppendageEnvelope(frames,view.index*sp.tailPoseCount,position,sp.tailPoseCount,pose,r.poseWarp)
        if warp<>invalid then r.poseWarp=warp : sx=sx*warp.sx
    end if
    ' Do not scale the neck vertically from a changing crop rectangle.
    a=sp.tailBodyPoints[body.first] : b=sp.tailBodyPoints[body.second]
    if sp.swimAxis="lateral"
        tx=scale*body.width*(a.x+(b.x-a.x)*body.blend+(a.lateral+(b.lateral-a.lateral)*body.blend)*r.waveSinPhase)
        ty=scale*(a.y+(b.y-a.y)*body.blend)
        drawAngle=angle
    else
    shiftA=a.positive*r.waveSinPhase : shiftB=b.positive*r.waveSinPhase
    if r.waveSinPhase<0# then shiftA=0#-a.negative*r.waveSinPhase : shiftB=0#-b.negative*r.waveSinPhase
    tx=scale*body.width*(a.x+(b.x-a.x)*body.blend)
    ty=scale*(a.y+(b.y-a.y)*body.blend+shiftA+(shiftB-shiftA)*body.blend)
    u=a.u+(b.u-a.u)*body.blend
    waveSin=0#-r.waveSinPhase*Sin(u*6.283185307#)
    waveCos=r.waveSinPhase*Cos(u*6.283185307#)
    length=sp.frameW*.9*scale*body.width/body.sourceWidth
    slope=r.waveAmplitude*(2#*u*waveSin-6.283185307#*u*u*waveCos)*(0#-r.waveSign)/length
    drawAngle=ReefClamp(angle-Atn(slope)*57.295779513#,-12.6,12.6)
    end if
    ' Underlap along the model axis, never an artificial vertical swim bend.
    tx=tx+sp.tailRig.overlap*scale*r.waveHeadingCos
    base=angle
    if not r.rotation then base=0# : drawAngle=0#
    if r.fractionalFish then base=Int(base*256#+.5)/256# : drawAngle=Int(drawAngle*256#+.5)/256#
    co=Cos(base/57.295779513#) : sn=Sin(base/57.295779513#)
    originX=p.x : originY=p.y
    if not r.fractionalFish
        ' Match the body's integer origin on graphics backends without subpixels.
        originX=Int((p.x+r.canvasOffset)*r.scale+.5)/r.scale-r.canvasOffset
        originY=Int(p.y*r.scale+.5)/r.scale
    end if
    targetX=originX+co*tx+sn*ty : targetY=originY+co*ty-sn*tx
    if sp.swimAxis<>"lateral" then co=Cos(drawAngle/57.295779513#) : sn=Sin(drawAngle/57.295779513#)
    r.basisAngle=drawAngle : r.basisCos=co : r.basisSin=sn
    x=targetX-co*source.x*sx-sn*source.y*sy
    y=targetY-co*source.y*sy+sn*source.x*sx
    ReefDrawFishRegion(r,x,y,sx,sy,drawAngle,region,ReefRGBA(red,green,blue,255),source)
end sub

sub ReefDrawFishPart(r as object,p as object,sp as object,frames as object,position as double,count as integer,view as object,scale as double,angle as double,red as integer,green as integer,blue as integer,opacity=255 as integer)
    ' Body excludes caudal-tail geometry. One tail and one pectoral image
    ' complete the fish; no crossfades, duplicate anatomy or reflections.
    poseIndex=Int(position+0.5)
    yaw=view.index
    sx=scale*view.width/view.sourceWidth
    region=frames[yaw*count+poseIndex] : tint=ReefRGBA(red,green,blue,opacity)
    if r.waveAmplitude=invalid then r.waveAmplitude=0#
    r.partLength=sp.frameW*.9*sx
    if count=sp.finPoseCount then r.partLength=r.partLength/sp.finTextureScale
    sy=scale : drawPoint=p
    if count>1 and region.anchorX<>invalid and region.wholeSwim<>true
        warp=ReefAppendageEnvelope(frames,yaw*count,position,count,poseIndex,r.poseWarp)
        if warp<>invalid
            r.poseWarp=warp
            if r.warpPoint=invalid then r.warpPoint={}
            dx=warp.dx*sx : dy=warp.dy*sy : co=r.waveBaseCos : sn=r.waveBaseSin
            if co=invalid then co=Cos(angle/57.295779513#) : sn=Sin(angle/57.295779513#)
            r.warpPoint.x=p.x+co*dx+sn*dy : r.warpPoint.y=p.y+co*dy-sn*dx
            drawPoint=r.warpPoint : sx=sx*warp.sx : sy=sy*warp.sy
        end if
    end if
    if sp.swimAxis="lateral" and count=sp.finPoseCount and sp.finSwimOffset<>0#
        if r.lateralFinPoint=invalid then r.lateralFinPoint={}
        r.lateralFinPoint.x=drawPoint.x-r.waveHeadingSin*r.waveSinPhase*sp.finSwimOffset*scale/sp.finTextureScale
        r.lateralFinPoint.y=drawPoint.y : drawPoint=r.lateralFinPoint
    end if
    if region.wholeSwim=true
        ' A complete curved body is one region: there are no interior slice edges.
        ReefDrawFishRegion(r,p.x,p.y,sx,sy,angle,region,tint)
    else if r.waveAmplitude>.15
        ' Fin and caudal patches remain whole and follow the tangent at their
        ' attachment. The complete body remains a single curved image.
        joint=0.20
        if count=sp.tailPoseCount then joint=0.76
        sign=r.waveSign
        if sign=invalid
            sign=1#
            if Cos(r.waveHeading)<0 then sign=0#-1#
        end if
        pivot=(.5-joint)*r.partLength*sign
        if r.finWaveFactors=invalid then r.finWaveFactors=ReefWaveFactors(.20) : r.tailWaveFactors=ReefWaveFactors(.76)
        factors=r.finWaveFactors
        if count=sp.tailPoseCount then factors=r.tailWaveFactors
        ReefDrawWaveRegion(r,drawPoint,sp,sx,sy,angle,region,pivot,tint,factors)
    else
        ReefDrawFishRegion(r,drawPoint.x,drawPoint.y,sx,sy,angle,region,tint)
    end if
end sub

sub ReefDrawWaveRegion(r as object,p as object,sp as object,sx as double,sy as double,angle as double,region as object,pivot as double,tint as integer,factors=invalid as dynamic)
    length=r.partLength : sign=r.waveSign
    if sign=invalid
        sign=1#
        if Cos(r.waveHeading)<0 then sign=0#-1#
    end if
    if factors<>invalid and r.waveSinPhase<>invalid
        u=factors.u
        waveSin=r.waveSinPhase*factors.cosOffset-r.waveCosPhase*factors.sinOffset
        waveCos=r.waveCosPhase*factors.cosOffset+r.waveSinPhase*factors.sinOffset
    else
        u=ReefClamp(.5-sign*pivot/length,0#,1#)
        phase=r.wavePhase-u*6.283185307# : waveSin=Sin(phase) : waveCos=Cos(phase)
    end if
    if r.waveStanding=true
        if factors<>invalid
            waveSin=0#-r.waveSinPhase*factors.sinOffset
            waveCos=r.waveSinPhase*factors.cosOffset
        else
            waveSin=0#-r.waveSinPhase*Sin(u*6.283185307#)
            waveCos=r.waveSinPhase*Cos(u*6.283185307#)
        end if
    end if
    displacement=r.waveAmplitude*u*u*waveSin
    slope=r.waveAmplitude*(2#*u*waveSin-6.283185307#*u*u*waveCos)*(0#-sign)/length
    bend=0#-Atn(slope) : c=1#/Sqr(1#+slope*slope) : sn=(0#-slope)*c
    drawAngle=angle+bend*57.295779513# : unclampedAngle=drawAngle
    if drawAngle< -12.6 then drawAngle=-12.6
    if drawAngle>12.6 then drawAngle=12.6
    if drawAngle<>unclampedAngle
        ' The pivot must use the rotation actually submitted to the screen.
        ' Otherwise a pitched/clamped section slides away from its neighbors.
        relative=(drawAngle-angle)/57.295779513#
        c=Cos(relative) : sn=Sin(relative)
    end if
    dx=pivot*(1#-c) : dy=displacement+sn*pivot
    co=r.waveBaseCos : si=r.waveBaseSin
    if co=invalid then base=angle/57.295779513# : co=Cos(base) : si=Sin(base)
    ReefDrawFishRegion(r,p.x+co*dx+si*dy,p.y+co*dy-si*dx,sx,sy,drawAngle,region,tint)
end sub

sub ReefDrawFishRegion(r as object, x as double, y as double, sx as double, sy as double, angle as double, region as object, tint as integer,root=invalid as dynamic)
    x = x + r.canvasOffset
    if not r.rotation then angle = 0#
    c=invalid : sn=invalid
    if r.fractionalFish
        angle=Int(angle*256#+.5)/256#
    end if
    if r.fractionalFish or region.offsetX<>invalid
        if r.basisAngle<>angle or r.basisCos=invalid
            r.basisAngle=angle : r.basisCos=Cos(angle/57.295779513#) : r.basisSin=Sin(angle/57.295779513#)
        end if
        c=r.basisCos : sn=r.basisSin
    end if
    if region.offsetX<>invalid
        if c=invalid then c=Cos(angle/57.295779513#) : sn=Sin(angle/57.295779513#)
        x=x+c*sx*region.offsetX+sn*sy*region.offsetY
        y=y+c*sy*region.offsetY-sn*sx*region.offsetX
    end if
    if r.fractionalFish
        if root=invalid
            transform = ReefFishTransform(x*r.scale,y*r.scale,sx*r.scale,sy*r.scale,angle,r.placement,c,sn)
        else
            pivotX=root.x : pivotY=root.y
            if region.offsetX<>invalid then pivotX=pivotX-region.offsetX : pivotY=pivotY-region.offsetY
            transform = ReefFishTransform(x*r.scale,y*r.scale,sx*r.scale,sy*r.scale,angle,r.placement,c,sn,pivotX,pivotY)
        end if
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

function ReefRenderSurface(r as object,time as double) as object
    if r.surfaceState=invalid or r.surfaceTime<>time
        r.surfaceState=ReefSurface(time,r.surfaceState) : r.surfaceTime=time
    end if
    return r.surfaceState
end function

sub ReefDrawSurface(r as object, s as object, a as object)
    if a.surface.Count() = 0 then return
    wave = ReefRenderSurface(r,s.displayTime)
    cfg = a.waveConfig.surface
    for pass = 0 to 1
        weight = 1 - wave.blend
        index = wave.first
        if pass = 1 then weight = wave.blend : index = wave.second
        color = ReefRGBA(255, 236, 223, Int(weight * (205 + 50 * s.lighting[0])))
        for tile = 0 to 3
            ReefDraw(r, -1024 + tile * 1024 - s.camera, -8, cfg.scale, 2, a.surface[index], color)
        end for
    end for
end sub

sub ReefDrawCaustics(r as object, s as object, a as object)
    if a.caustics.Count() = 0 then return
    wave = ReefRenderSurface(r,s.displayTime)
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
    wave=ReefRenderSurface(r,s.displayTime) : cfg=a.waveConfig.shadow
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
    if r.eelPose=invalid then r.eelPose={}
    ReefDrawFishRegion(r,cfg.x-s.camera,cfg.y-36,1#,1#,0#,a.eels[ReefEelFrame(s.displayTime,r.eelPose)],ReefRGBA(light,light,light,255))
end sub

sub ReefDrawSurfaceShadow(r as object,s as object,a as object,index as integer,formation as object)
    if a.surfaceShadows=invalid then return
    if a.surfaceShadows[index].Count()=0 then return
    cfg=formation.surfaceShadow : wave=ReefRenderSurface(r,s.displayTime)
    for pass=0 to 1
        weight=1-wave.blend : phase=wave.first
        if pass=1 then weight=wave.blend : phase=wave.second
        ReefDraw(r,cfg.x-s.camera,cfg.y-36#,cfg.scale,cfg.scale,a.surfaceShadows[index][phase],ReefRGBA(255,255,255,Int(weight*255*.65*(.35+.65*s.lighting[0]))))
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
    ReefDrawSurface(r,s,a)
    floorTint=&hFFFFFFFF
    if s.settings.lighting<>"Sunset" then floorTint=&hDDEBFFFF
    if a.floor<>invalid then ReefDraw(r,0#-s.camera,920#-36#,1#,1#,a.floor,floorTint)
    ' Stable insertion sort of references, not copied fish. Persistent list has bounded length.
    if s.sorted = invalid then s.sorted = []
    s.sorted.Clear()
    for fishIndex = 0 to s.fish.Count() - 1
        f = s.fish[fishIndex]
        f.renderPose = ReefDisplayPose(f,s.renderAlpha,f.renderPose)
        if f.emerging<>true
        s.sorted.Push(f)
        j = s.sorted.Count() - 1
        while j > 0
            previousPose = s.sorted[j - 1].renderPose
            currentPose = f.renderPose
            if previousPose.z <= currentPose.z then exit while
            s.sorted[j] = s.sorted[j - 1] : j = j - 1
        end while
        s.sorted[j] = f
        end if
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
        if formation.id="clam" then marineView=Int(ReefClamDisplayOpening(s)*(formation.frames-1)+.5)
        light=1#
        if formation.animation=invalid
            shade=ReefSurfaceShade(formation.x+formation.width*.5,formation.y+formation.height*.45,s.displayTime)
            light=1#-(1#-shade)*.35*(.35+.65*s.lighting[0])
        end if
        red=255 : green=255 : blue=255
        if s.settings.lighting<>"Sunset" then red=221 : green=235
        tint=ReefRGBA(Int(red*light),Int(green*light),Int(blue*light),255)
        ReefDraw(r,formation.x-offset,formation.y-36,formation.width/formation.frameWidth,formation.height/formation.frameHeight,a.formations[formationIndex][marineView],tint)
        ReefDrawSurfaceShadow(r,s,a,formationIndex,formation)
        if formation.id="clam"
            if r.clamBounds=invalid then r.clamBounds={active:false}
            r.clamBounds.active=false
            ReefDrawClamContents(r,s,a)
            if s.clam.baby<>invalid
                if s.clam.baby.emerging=true
                    child=s.clam.baby : ReefDrawFish(r,s,a,child) : p=child.screenPose
                    fishScale=p.scale*child.sp.length/child.sp.renderLength*child.size
                    hw=child.sp.collisionHalfWidth*fishScale+8# : hh=child.sp.collisionHalfHeight*fishScale+8#
                    ReefClamContentBounds(r,p.x-hw,p.y-hh,hw*2#,hh*2#)
                end if
            end if
            if r.clamBounds.active and a.clamFront<>invalid
                sx=formation.width/formation.frameWidth : sy=formation.height/formation.frameHeight : bounds=r.clamBounds
                for each piece in a.clamFront[marineView]
                    x=formation.x-offset+piece.x*sx : y=formation.y-36+piece.y*sy
                    if x<bounds.right and x+piece.w*sx>bounds.left and y<bounds.bottom and y+piece.h*sy>bounds.top
                        ReefDraw(r,x,y,sx,sy,piece.region,tint)
                    end if
                end for
            end if
        end if
        if formation.id="connected-reef" then ReefDrawEel(r,s,a)
    end for
    ReefDrawCaustics(r, s, a)
    ReefDrawSandShadows(r, s, a)
    while i < s.sorted.Count()
        ReefDrawFish(r, s, a, s.sorted[i]) : i = i + 1
    end while
    ReefDrawEffects(r,s,a,previousDepth,1.01,s.cfg.formations.Count())
    rayPhase=ReefWrap(s.displayTime*.07,6.283185307#)
    rayLight=ReefWrap(s.displayTime*.13,6.283185307#)
    for k = 0 to 2
        ReefDraw(r, 150 + k * 590 + Sin(rayPhase + k) * 24 - s.camera * 0.25, -70, 2.0, 1.8, a.ray, ReefRGBA(255, 223, 210, Int((65 + 18 * Sin(rayLight + k)) * s.lighting[0])))
    end for
    if s.lighting[2] > 0 then screen.DrawRect(0, 0, screen.GetWidth(), screen.GetHeight(), ReefRGBA(8, 16, 57, Int(s.lighting[2])))
    if s.lighting[3] > 0 then screen.DrawRect(0, 0, screen.GetWidth(), screen.GetHeight(), ReefRGBA(241, 105, 108, Int(s.lighting[3])))
    ReefDrawBioluminescence(r,s,a)
    if r.output<>invalid then ReefPresent(r,s)
end sub

sub ReefPresent(r as object,s as object)
    screen = r.output
    if r.frame<>invalid
        r.panPhase = ReefPixelPhase(0#-s.camera*r.outputScale,r.panPhase) : phase=r.panPhase
        screen.SetAlphaEnable(false)
        screen.Clear(&h182A42FF)
        ' The canvas is already in output pixels; never rescale it a second time.
        screen.DrawObject(phase.first,0,r.frame,&hFFFFFFFF)
        if phase.blend>0.001
            screen.SetAlphaEnable(true)
            color=ReefRGBA(255,255,255,Int(phase.blend*255+0.5))
            screen.DrawObject(phase.first+1,0,r.frame,color)
        end if
    end if
    screen.SetAlphaEnable(true)
    if s.settings.clock="On" then screen.DrawText(s.clockText,Int(1660*r.outputScale),Int(970*r.outputScale),&hF6DFD4B0,r.font)
    if s.settings.fps="On"
        screen.DrawText(Int(s.fps).ToStr()+" FPS",Int(110*r.outputScale),Int(95*r.outputScale),&hF6DFD4D0,r.font)
        if s.perfText<>invalid then screen.DrawText(s.perfText,Int(110*r.outputScale),Int(125*r.outputScale),&hF6DFD4D0,r.font)
    end if
end sub

sub ReefDrawClamContents(r as object,s as object,a as object)
    if s.clam=invalid then return
    if not s.clam.enabled then return
    if s.clam.event=0 and a.pearl<>invalid
        ' Always present at full opacity; the physical shell reveals it.
        x=1075#-s.camera : y=960#
        ReefDraw(r,x,y,.50,.50,a.pearl,ReefRGBA(255,250,241,255))
        ReefClamContentBounds(r,x,y,20#,20#)
    end if
    if s.clam.event=1 then ReefDrawClamBubbles(r,s,a)
end sub

sub ReefDrawClamBubbles(r as object,s as object,a as object)
    if s.settings.bubbles="Off" or a.bubble=invalid then return
    for each e in s.clam.bubbles
        age=ReefMax(0#,s.displayTime-e.born)
        if not s.clam.released then age=0#
        y=e.originY-age*e.speed
        x=e.x+(Sin(age*1.3+e.phase)-Sin(e.phase))*6#-s.camera
        if y>45#
            alpha=Int(180*ReefClamp((y-45#)/45#,0#,1#))
            ReefDraw(r,x,y,e.scale,e.scale,a.bubble,ReefRGBA(230,250,255,alpha))
            ReefClamContentBounds(r,x,y,e.scale*32#,e.scale*32#)
        end if
    end for
end sub

sub ReefClamContentBounds(r as object,x as double,y as double,w as double,h as double)
    if r.clamBounds=invalid then r.clamBounds={active:false}
    b=r.clamBounds
    if not b.active
        b.left=x : b.top=y : b.right=x+w : b.bottom=y+h : b.active=true
    else
        b.left=ReefMin(b.left,x) : b.top=ReefMin(b.top,y)
        b.right=ReefMax(b.right,x+w) : b.bottom=ReefMax(b.bottom,y+h)
    end if
end sub

sub ReefDrawBioluminescence(r as object,s as object,a as object)
    if a.glow=invalid or s.bioluminescence=invalid then return
    enabled=s.settings.lighting="Night"
    if s.settings.lighting="Automatic" and s.lighting[0]<.24 then enabled=true
    if not enabled then return
    strength=ReefClamp((.30-s.lighting[0])/.24,0#,1#)
    coralPhase=ReefWrap(s.displayTime*.32,6.283185307#)
    for each site in s.bioluminescence
        pulse=.72+.28*Sin(coralPhase+site.phase)
        ReefDraw(r,site.x-s.camera-16#*site.size,site.y-36#-16#*site.size,site.size,site.size,a.glow,ReefRGBA(52,255,202,Int(190*strength*pulse)))
    end for
    if s.settings.particles="Off" then return
    planktonPhase=ReefWrap(s.displayTime*.7,6.283185307#)
    for i=0 to 11
        e=s.effects[i]
        x=e.previousX+(e.x-e.previousX)*s.renderAlpha-s.camera*(.4+e.z*.6)
        y=e.previousY+(e.y-e.previousY)*s.renderAlpha
        pulse=.55+.45*Sin(planktonPhase+e.phase*4#)
        ReefDraw(r,x-5#,y-5#,.32,.32,a.glow,ReefRGBA(70,214,255,Int(170*strength*pulse)))
    end for
end sub
