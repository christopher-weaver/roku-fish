' Safe contact with the numerical guard must still allow an escape.
sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    a={id:0,sp:species.copperband_butterflyfish,size:1#,x:650#,y:350#,z:.94}
    b={id:1,sp:species.mandarin_dragonet,size:1#,x:650#,y:350#,z:.94}
    aa=ReefFishBounds(a) : bb=ReefFishBounds(b)
    radius=aa.radius+bb.radius+4# : height=aa.height+bb.height+4#
    for axis=0 to 2
        b.x=a.x : b.y=a.y : b.z=a.z
        if axis=0 then b.x=a.x+radius+.0099999#
        if axis=1 then b.z=a.z-(radius+.0099999#)/800#
        if axis=2 then b.y=a.y+height+.0099999#
        b.previousX=b.x : b.previousY=b.y : b.previousZ=b.z
        escape={x:a.x,y:a.y,z:a.z} : inward={x:a.x,y:a.y,z:a.z}
        if axis=0 then escape.x=a.x-1# : inward.x=a.x+1#
        if axis=1 then escape.z=a.z+.001 : inward.z=a.z-.001
        if axis=2 then escape.y=a.y-1# : inward.y=a.y+1#
        if ReefFishPairBlocked(a,a,a,b,false) then print "FAIL fixture overlaps real body" : return
        if not ReefFishPairBlocked(a,a,a,b) then print "FAIL stationary spawn loses buffer" : return
        if ReefFishPairBlocked(a,a,escape,b) then print "FAIL contact blocks separating escape axis ";axis : return
        if not ReefFishPairBlocked(a,a,inward,b) then print "FAIL contact permits approach axis ";axis : return
        if axis=0
            tangent={x:a.x,y:a.y-1#,z:a.z}
            if ReefFishPairBlocked(a,a,tangent,b) then print "FAIL vertical contact escape" : return
            b.previousX=b.x+1# : b.x=b.x-1#
            if not ReefFishPairBlocked(a,a,escape,b) then print "FAIL ignores approaching neighbor sweep" : return
        end if
        if axis=2
            tangent={x:a.x-1#,y:a.y,z:a.z}
            if ReefFishPairBlocked(a,a,tangent,b) then print "FAIL horizontal contact escape along vertical buffer" : return
        end if
    end for
    b.x=a.x+radius-.1 : b.y=a.y : b.z=a.z
    b.previousX=b.x : b.previousY=b.y : b.previousZ=b.z
    if not ReefFishPairBlocked(a,a,{x:a.x-2#,y:a.y,z:a.z},b) then print "FAIL actual overlap accepted" : return
    print "PASS contact releases lateral, depth and vertical escapes; inward motion, moving-neighbor contact, actual overlap and stationary spawn buffer remain guarded"
end sub
