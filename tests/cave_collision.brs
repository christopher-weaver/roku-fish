sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    s=ReefWorld(ReefValidateSettings({density:"Low"}),species,ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json")),42)
    if s.occupancy.volumes.Count()<>1 then print "FAIL cave exclusion missing" : return
    checks=0
    for each name in species
        f={sp:species[name],size:1.12}
        inside={x:779#,y:809#,z:.48}
        if not ReefCaveBlocked(s,f,inside,inside) then print "FAIL cave interior spawn permitted" : return
        if not ReefCoralBlocked(s,f,inside,inside) then print "FAIL cave bypasses coral guard" : return
        left={x:300#,y:809#,z:.48} : right={x:1200#,y:809#,z:.48}
        if not ReefCaveBlocked(s,f,left,right) then print "FAIL cave swept crossing permitted" : return
        if not ReefCaveBlocked(s,f,right,left) then print "FAIL reverse cave sweep permitted" : return
        rear={x:779#,y:809#,z:.02} : front={x:779#,y:809#,z:.98}
        if not ReefCaveBlocked(s,f,rear,front) then print "FAIL cave depth crossing permitted" : return
        if ReefCaveBlocked(s,f,front,front) then print "FAIL clear front lane closed" : return
        if ReefCaveBlocked(s,f,rear,rear) then print "FAIL clear rear lane closed" : return
        f.x=779# : f.y=809# : f.z=.48
        ReefSafeSpawn(s,f)
        if ReefCoralBlocked(s,f,f,f) then print "FAIL cave safe spawn" : return
        checks=checks+1
    end for
    print "PASS cave interior, forward/reverse swept entry, depth entry and safe spawn blocked for ";checks;" fish; clear front/rear lanes preserved"
end sub
