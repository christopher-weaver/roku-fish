sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occ=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    s={occupancy:occ,cfg:ParseJson(ReadAsciiFile("pkg:/scenes/tank.json")),rng:47831#}
    ReefCollisionInit(s)
    names=species.Keys()
    for planeIndex=0 to occ.planes.Count()-1
        plane=occ.planes[planeIndex]
        if plane.rowIndex=invalid then print "FAIL missing exact row index" : return
        for sample=0 to 179
            x=ReefRange(s,-120,2100) : y=ReefRange(s,-100,1160)
            w=ReefRange(s,0,900) : h=sample+1#
            expected=ReferenceReefSolidRect(plane.rows,8,x,y,x+w,y+h)
            actual=ReefSolidRect(plane.rows,8,x,y,x+w,y+h,plane.rowIndex)
            if actual<>expected then print "FAIL indexed rectangle ";planeIndex;sample : return
        end for
    end for
    for sample=0 to 599
        sp=species[names[sample mod names.Count()]]
        f={sp:sp,size:ReefRange(s,.2,1.2)}
        a={x:ReefRange(s,50,2000),y:ReefRange(s,30,1060),z:ReefRange(s,.02,.999)}
        b={x:a.x+ReefRange(s,-600,600),y:a.y+ReefRange(s,-400,400),z:ReefClamp(a.z+ReefRange(s,-.4,.4),.02,.999)}
        if sample mod 4=0 then b=a
        expected=ReferenceReefCoralBlocked(s,f,a,b)
        if ReefCoralBlocked(s,f,a,b)<>expected then print "FAIL swept reef equivalence ";sample : return
        other={sp:species[names[(sample+3) mod names.Count()]],size:1#,x:ReefRange(s,50,2000),y:ReefRange(s,30,1060),z:ReefRange(s,.02,.999)}
        other.previousX=other.x+ReefRange(s,-300,300) : other.previousY=other.y+ReefRange(s,-150,150) : other.previousZ=other.z+ReefRange(s,-.2,.2)
        for swept=0 to 1
            expected=ReferenceReefFishPairBlocked(f,a,b,other,swept=1)
            if ReefFishPairBlocked(f,a,b,other,swept=1)<>expected then print "FAIL swept pair equivalence ";sample : return
            f.id=0 : other.id=1 : s.fish=[f,other]
            s.physicsBoundsReady=false
            if ReefFishBlocked(s,f,a,b,swept=1)<>expected then print "FAIL broad phase lost a swept pair ";sample : return
            s.physicsBoundsReady=true
            if ReefFishBlocked(s,f,a,b,swept=1)<>expected then print "FAIL cached broad phase lost a swept pair ";sample : return
            s.physicsBoundsReady=false
        end for
        ' Bounds must refresh on cloned babies, size changes and a species change.
        f.size=.27 : f.sp=other.sp
        if ReefFishRadius(f)<>ReferenceReefFishRadius(f) or ReefFishHeight(f)<>ReferenceReefFishHeight(f) then print "FAIL stale body bounds" : return
    end for
    ' An altered/custom grid must never receive a table for the shipping reef.
    occ.planes[0].rows[0]="#"+Mid(occ.planes[0].rows[0],2)
    occ.planes[0].rowIndex=invalid
    ReefCollisionInit(s)
    if occ.planes[0].rowIndex<>invalid then print "FAIL mismatched grid index" : return
    light={fish:[{id:0,x:500#,y:400#,z:.5,heading:0#,schooling:true,sp:{length:90}},{id:1,x:700#,y:410#,z:.5,heading:0#,schooling:true,sp:{length:90}}]}
    steer=ReefNeighbors(light,light.fish[0])
    if steer.count<>1 then print "FAIL geometry-free schooling bounds" : return
    if ReefCoralBlocked(light,light.fish[0],{x:84#,y:400#,z:.5},light.fish[0])<>true then print "FAIL geometry-free tank limits" : return
    print "PASS exact collision optimization: 1260 rectangles, 600 swept reef paths, 1200 swept/static pairs, 2400 cached/uncached broad-phase paths, 600 cache invalidations, custom-grid fallback"
end sub
