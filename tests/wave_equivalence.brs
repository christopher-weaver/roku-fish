sub Main()
    screen={x:0,y:0,angle:0#,DrawTransformedObject:WaveCapture}
    r={screen:screen,scale:1#,canvasOffset:0#,rotation:true,fractionalFish:false,placement:{},partLength:280#,waveAmplitude:3.7}
    p={x:900.123,y:400.456} : sp={} : region={normal:"body"}
    checks=0
    for form=0 to 1
        r.waveStanding=form=1
        for each angle in [-12.6,0#,8.9]
            r.waveBaseCos=Cos(angle/57.295779513#) : r.waveBaseSin=Sin(angle/57.295779513#)
            for each heading in [.35,3.45]
                r.waveHeading=heading : sign=1#
                if Cos(heading)<0 then sign=0#-1#
                for phase=0 to 15
                    r.wavePhase=phase*.4188790205
                    for pivot=0-140 to 140 step 35
                        u=.5-sign*pivot/r.partLength
                        d=ReefBodyWave(u,r.wavePhase,r.waveAmplitude)
                        slope=ReefBodyWaveSlope(u,r.wavePhase,r.waveAmplitude)*(0#-sign)/r.partLength
                        if r.waveStanding=true
                            d=r.waveAmplitude*u*u*(0#-Sin(r.wavePhase)*Sin(u*6.283185307#))
                            slope=r.waveAmplitude*(2#*u*(0#-Sin(r.wavePhase)*Sin(u*6.283185307#))-6.283185307#*u*u*Sin(r.wavePhase)*Cos(u*6.283185307#))*(0#-sign)/r.partLength
                        end if
                        bend=0#-Atn(slope)
                        expectedAngle=ReefClamp(angle+bend*57.295779513#,-12.6,12.6)
                        relative=(expectedAngle-angle)/57.295779513#
                        c=Cos(relative) : sn=Sin(relative)
                        dx=pivot*(1#-c) : dy=d+sn*pivot
                        base=angle/57.295779513# : co=Cos(base) : si=Sin(base)
                        expectedX=Int(p.x+co*dx+si*dy+.5) : expectedY=Int(p.y+co*dy-si*dx+.5)
                        expectedAngle=ReefClamp(angle+bend*57.295779513#,-12.6,12.6)
                        r.waveSinPhase=Sin(r.wavePhase) : r.waveCosPhase=Cos(r.wavePhase)
                        factors=ReefWaveFactors(u)
                        ReefDrawWaveRegion(r,p,sp,1#,1#,angle,region,pivot,&hFFFFFFFF,factors)
                        if screen.x<>expectedX or screen.y<>expectedY or Abs(screen.angle-expectedAngle)>.00001 then print "FAIL optimized body transform differs" : return
                        checks=checks+1
                    end for
                end for
            end for
        end for
    end for
    print "PASS ";checks;" traveling/standing S-curve attachment transforms preserve pivots at ordinary and clamped pitch angles"
end sub
function WaveCapture(x as integer,y as integer,angle as float,sx as float,sy as float,source as dynamic,tint as integer) as boolean
    m.x=x : m.y=y : m.angle=angle : return true
end function
