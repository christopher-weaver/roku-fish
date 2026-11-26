sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occ=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    s=ReefWorld(ReefValidateSettings({density:"Low"}),species,occ,42)
    footingWorld={cfg:{},occupancy:{cell:8,planes:[]}}
    for i=0 to occ.planes.Count()-1
        if occ.planes[i].id="grounded-rock-base" then footingWorld.occupancy.planes.Push(occ.planes[i])
    end for
    count=0
    for each name in species
        f={sp:species[name],size:1.12}
        high={x:900#,y:650#,z:.12} : buried={x:900#,y:1100#,z:.94}
        if ReefFloorBlocked(s,f,high,high) then print "FAIL clear water blocked" : return
        if not ReefFloorBlocked(s,f,buried,buried) then print "FAIL buried body allowed" : return
        if not ReefCoralBlocked(s,f,high,buried) then print "FAIL ground sweep allowed" : return
        ' The fuller copperband needs a few more pixels above the sand.
        ' Preserve the ground guard rather than accepting its old buried pose.
        rear={x:900#,y:920#,z:.12} : front={x:900#,y:910#,z:.98}
        if not ReefFloorBlocked(s,f,rear,rear) then print "FAIL rear fish beneath sand" : return
        if ReefFloorBlocked(s,f,front,front) then print "FAIL clear front floor lane blocked" : return
        if name="copperband_butterflyfish"
            oldPose={x:900#,y:920#,z:.98}
            if not ReefFloorBlocked(s,f,oldPose,oldPose) then print "FAIL wider copperband clips into sand" : return
        end if
        rock={x:900#,y:930#,z:.58}
        if not ReefCoralBlocked(footingWorld,f,rock,rock) then print "FAIL fish under reef footing" : return
        count=count+1
    end for
    print "PASS textured ground plane, swept ground entry and solid reef footings protect all ";count;" species; front swimming lane remains clear"
end sub
