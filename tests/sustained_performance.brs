' Four minutes at the real fixed rate, maximum selected density, no clock jumps.
sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occ=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    s=ReefWorld(ReefValidateSettings({density:"High"}),species,occ,47831)
    for block=0 to 11
        ReefStabilityWindow(s)
        routes=0 : keys=0 : count=s.fish.Count()
        if count>12 or s.effects.Count()<>72 or s.clam.bubbles.Count()<>12 then print "FAIL growing population/effect pools" : return
        for i=0 to count-1
            f=s.fish[i] : routes=routes+f.route.Count() : keys=keys+f.Count()
            if f.route.Count()>s.navigation.nodes.Count() then print "FAIL accumulating route history" : return
            if ReefCoralBlocked(s,f,f,f) or ReefFishBlocked(s,f,f,f,false) then print "FAIL sustained collision safety" : return
        end for
        print "STABILITY ";FormatJson({seconds:s.time,fish:count,effects:s.effects.Count(),route_entries:routes,fish_fields:keys,births:s.clam.births})
    end for
    print "PASS four-minute High-density production ticks; bounded populations, particles, routes and fish fields"
end sub
sub ReefStabilityWindow(s as object)
    for tick=1 to 600
        ReefStep(s,1#/30#)
    end for
end sub
