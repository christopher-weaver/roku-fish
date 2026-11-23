' Capture production section regions/transforms for an independent coverage check.
sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    names=species.Keys()
    for n=0 to names.Count()-1
        sp=species[names[n]]
        for direction=0 to 1
            yaw=0
            if direction=1 then yaw=Int(sp.bodyYawCount/2)
            frame=sp.frames[yaw]
            frames=ReefFishFrames({},[frame],"High",8,sp.frameW*.9)
            for resolution=0 to 1
                outputScale=1#
                if resolution=1 then outputScale=2#/3#
                for phase=0 to 11
                    screen={draws:[],DrawTransformedObject:SeamCapture}
                    r={screen:screen,scale:outputScale,canvasOffset:0#,rotation:true,fractionalFish:false,partLength:sp.frameW*.9,waveAmplitude:sp.renderLength*.012,waveSign:1#,waveBaseCos:1#,waveBaseSin:0#,wavePhase:phase*6.283185307#/12#}
                    r.waveHeading=direction*3.141592654#
                    if direction=1 then r.waveSign=0#-1#
                    r.waveSinPhase=Sin(r.wavePhase) : r.waveCosPhase=Cos(r.wavePhase)
                    for band=0 to 7
                        strip=frames[0].bands[band] : factors=strip.waveForward
                        if direction=1 then factors=strip.waveReverse
                        ReefDrawWaveRegion(r,{x:500.25,y:300.25},sp,1#,1#,0#,strip,strip.centerX,&hFFFFFFFF,factors)
                    end for
                    print "SEAM ";FormatJson({name:names[n],phase:r.wavePhase,sign:r.waveSign,amplitude:r.waveAmplitude,length:r.partLength,scale:outputScale,w:frame.w,h:frame.h,ax:frame.anchorX,ay:frame.anchorY,draws:screen.draws})
                end for
            end for
        end for
    end for
end sub
function SeamRegion(bitmap as object,x as integer,y as integer,w as integer,h as integer) as object
    return {w:w,h:h,SetPretranslation:SeamTranslate,SetScaleMode:SeamScale}
end function
sub SeamTranslate(x as integer,y as integer)
    m.px=x : m.py=y
end sub
sub SeamScale(mode as integer)
end sub
function SeamCapture(x as integer,y as integer,angle as float,sx as float,sy as float,source as object,tint as integer) as boolean
    m.draws.Push({x:x,y:y,angle:angle,sx:sx,sy:sy,w:source.w,h:source.h,px:source.px,py:source.py})
    return true
end function
