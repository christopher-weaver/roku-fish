sub Main()
    prefs=ReefValidateSettings({density:"Low"})
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occupancy=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    s=ReefWorld(prefs,species,occupancy,9182)
    s.clam.enabled=false
    while s.fish.Count()>6
        s.fish.Pop()
    end while
    bad=0 : maxX=-1# : minX=3000# : minZ=5# : maxZ=-5#
    for i=1 to 36000
        ReefStep(s,0.1)
        for each f in s.fish
            if f.x<0 or f.x>2048 or f.y<80 or f.y>1000 or f.z<0 or f.z>1 then bad=bad+1
            if f.x<minX then minX=f.x
            if f.x>maxX then maxX=f.x
            if f.z<minZ then minZ=f.z
            if f.z>maxZ then maxZ=f.z
        end for
        if i mod 6000=0 then print "SOAK simulated seconds=";i/10;" bounds violations=";bad
    end for
    print "SOAK RESULT violations=";bad;" fish=";s.fish.Count();" effects=";s.effects.Count();" x=";minX;",";maxX;" z=";minZ;",";maxZ
end sub
