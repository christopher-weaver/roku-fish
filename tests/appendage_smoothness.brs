sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json")) : checked=0
    for each name in species
        sp=species[name]
        for part=0 to 1
            frames=sp.tailFrames : count=sp.tailPoseCount
            if part=1 then frames=sp.finFrames : count=sp.finPoseCount
            for yaw=0 to 63 step 4
                for pose=0 to count-2
                    boundary=pose+.5
                    a=ReefAppendageEnvelope(frames,yaw*count,boundary-.00001,count,pose)
                    b=ReefAppendageEnvelope(frames,yaw*count,boundary+.00001,count,pose+1)
                    if a<>invalid and b<>invalid
                        fa=frames[yaw*count+pose] : fb=frames[yaw*count+pose+1]
                        if Abs((a.dx-fa.anchorX*a.sx)-(b.dx-fb.anchorX*b.sx))>.01 then print "FAIL appendage left edge jumps" : return
                        if Abs((a.dy-fa.anchorY*a.sy)-(b.dy-fb.anchorY*b.sy))>.01 then print "FAIL appendage top edge jumps" : return
                        if Abs(fa.w*a.sx-fb.w*b.sx)>.01 or Abs(fa.h*a.sy-fb.h*b.sy)>.01 then print "FAIL appendage extent jumps" : return
                        if a.sx<=0 or a.sy<=0 or b.sx<=0 or b.sy<=0 then print "FAIL appendage reflection" : return
                        checked=checked+1
                    end if
                end for
            end for
        end for
    end for
    if checked<400 then print "FAIL insufficient animated envelope checks" : return
    print "PASS ";checked;" tail/pectoral pose boundaries preserve continuous edges and dimensions using single positive-scale images"
end sub
