sub Main()
    ' Prove the host adapter reproduces Roku's shared enumeration pointer.
    values=[1,2,3] : visits=0
    for each outer in values
        visits=visits+1
        for each inner in values
            value=inner
        end for
    end for
    if visits<>1 then print "FAIL native enumeration adapter" : return
    print "PASS native shared-cursor behavior reproduced"
    prefs=ReefValidateSettings(invalid)
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occupancy=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    s=ReefWorld(prefs,species,occupancy,47831)
    before=[]
    for i=0 to s.fish.Count()-1
        f=s.fish[i] : before.Push({x:f.x,y:f.y,z:f.z,phase:f.phase})
    end for
    ReefStep(s,1#/30#)
    updated=0 : animated=0
    for i=0 to s.fish.Count()-1
        f=s.fish[i]
        if f.x<>before[i].x or f.y<>before[i].y or f.z<>before[i].z then updated=updated+1
        if f.phase<>before[i].phase then animated=animated+1
    end for
    print "Fish updated=";updated;" animated=";animated;" expected=";s.fish.Count()
    if updated<>s.fish.Count() or animated<>s.fish.Count()
        print "FAIL every fish must advance on Roku"
        return
    end if
    print "PASS every fish advances with native cursor semantics"
    for each density in ["Low","Medium","High"]
        prefs=ReefValidateSettings({density:density})
        world=ReefWorld(prefs,species,occupancy,1900000001)
        seen={}
        if world.fish.Count()<>world.cfg.populations[density] then print "FAIL population" : return
        for i=0 to world.fish.Count()-1
            name=world.fish[i].name
            if seen.DoesExist(name) then print "FAIL repeated species" : return
            seen[name]=true
        end for
        for frame=0 to 29
            previous=[]
            for i=0 to world.fish.Count()-1
                f=world.fish[i] : previous.Push({phase:f.phase,fin:f.finPhase})
            end for
            ReefAdvance(world,1#/30#)
            for i=0 to world.fish.Count()-1
                if world.fish[i].phase=previous[i].phase or world.fish[i].finPhase=previous[i].fin
                    print "FAIL fish animation starvation at ";density;" frame ";frame;" fish ";i
                    return
                end if
            end for
        end for
        print "PASS all body and pectoral phases advance at ";density;" density"
    end for
end sub
