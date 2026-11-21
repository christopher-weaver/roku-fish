sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occ=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    s=ReefWorld(ReefValidateSettings(invalid),species,occ,47831) : s.clam.enabled=false
    start=[] : distance=[] : bounds=[]
    for i=0 to s.fish.Count()-1
        f=s.fish[i] : start.Push(f.x) : distance.Push(0#) : bounds.Push({lo:f.x,hi:f.x})
    end for
    for tick=1 to 360
        for i=0 to s.fish.Count()-1
            start[i]=s.fish[i].x
        end for
        ReefStep(s,1#/30#)
        for i=0 to s.fish.Count()-1
            f=s.fish[i] : distance[i]=distance[i]+Abs(f.x-start[i])
            bounds[i].lo=ReefMin(bounds[i].lo,f.x) : bounds[i].hi=ReefMax(bounds[i].hi,f.x)
            if ReefCoralBlocked(s,f,f,f) then print "FAIL active fish enters reef or sand" : return
        end for
    end for
    active=0 : across=0
    for i=0 to s.fish.Count()-1
        f=s.fish[i] : span=bounds[i].hi-bounds[i].lo
        print "ACTIVITY ";f.name;" lateral travel=";distance[i];" span=";span
        if distance[i]>120# then active=active+1
        if span>220# then across=across+1
    end for
    if active<6 or across<4 then print "FAIL insufficient side-to-side swimming ";active;across : return
    print "PASS sustained lateral activity over 12 seconds with full reef/floor clearance"
end sub
