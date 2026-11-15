sub Main()
    tank=ParseJson(ReadAsciiFile("pkg:/scenes/tank.json"))
    moving=0
    for index=0 to tank.formations.Count()-1
        f=tank.formations[index]
        if f.motion<>invalid
            moving=moving+1
            extent=f.rootY-f.y
            root=ReefMarineBand(3.1,f,extent,1#)
            if Abs(root.dx)>0.0000001 or Abs(root.dy)>0.0000001 or Abs(root.sx-1)>0.0000001 or Abs(root.sy-1)>0.0000001 then print "FAIL unpinned root" : return
            maxMotion=0#
            for frame=0 to 119
                time=frame/60#
                for y=0 to f.frameHeight-1 step 8
                    h=ReefMin(8#,f.frameHeight-y)
                    a=ReefMarineBand(time,f,y,h) : b=ReefMarineBand(time+1#/60#,f,y,h)
                    motion=Abs(a.dx-b.dx)+Abs(a.dy-b.dy)+f.frameWidth*Abs(a.sx-b.sx)*.5
                    maxMotion=ReefMax(maxMotion,motion)
                    if motion>.15 then print "FAIL marine motion step ";f.id;motion : return
                    if Abs(a.dx)+f.frameWidth*Abs(a.sx-1)*.5>f.motion.clearance then print "FAIL marine envelope" : return
                    if a.sx<=0 or a.sy<=0 then print "FAIL reflected marine part" : return
                    if y+h<f.frameHeight
                        nextBand=ReefMarineBand(time,f,y+h,8#)
                        if Abs(y+a.dy+h*a.sy-(y+h+nextBand.dy))>.0001 then print "FAIL detached band boundary ";f.id;y;time;Abs(y+a.dy+h*a.sy-(y+h+nextBand.dy));a.dy;a.sy;nextBand.dy : return
                    end if
                end for
            end for
            first=ReefMarineBand(0#,f,0#,8#) : later=ReefMarineBand(2#,f,0#,8#)
            if Abs(first.dx-later.dx)<.2 then print "FAIL static fingers" : return
            print "PASS continuous root-pinned ";f.id;" branches/tentacles; maximum 60Hz step ";maxMotion
        end if
    end for
    if moving<>2 then print "FAIL missing marine rig" : return
end sub
