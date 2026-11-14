sub Main()
    prefs=ReefValidateSettings(invalid)
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occ=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    s=ReefWorld(prefs,species,occ,47831)
    for tick=0 to 59
        ReefAdvance(s,1#/30#)
        for i=0 to s.fish.Count()-1
            f=s.fish[i]
            if ReefCoralBlocked(s,f,f,f) then print "FAIL coral footprint ";i : return
            pose=ReefDisplayPose(f,0.5)
            if ReefCoralBlocked(s,f,pose,pose) then print "FAIL interpolated footprint ";i : return
            if f.x<0 or f.x>2048 or f.z<0 or f.z>1 then print "FAIL bounds" : return
        end for
    end for
    print "PASS targeted collision check: 60 physics ticks, 18 fish, all physical/interpolated footprints clear of the connected reef, fan and anemone"
end sub
