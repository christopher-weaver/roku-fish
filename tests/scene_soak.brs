' Ten minutes of the shipped close-reef masks and larger principal fish.
sub Main()
    prefs=ReefValidateSettings({density:"Low"})
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occupancy=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    s=ReefWorld(prefs,species,occupancy,9182)
    s.clam.enabled=false
    while s.fish.Count()>6
        s.fish.Pop()
    end while
    bounds=0 : coral=0 : transitions=0 : completed=0
    for tick=1 to 6000
        ReefStep(s,0.1)
        for i=0 to s.fish.Count()-1
            f=s.fish[i]
            if f.x<0 or f.x>2048 or f.y<80 or f.y>1000 or f.z<0 or f.z>1 then bounds=bounds+1
            if ReefCoralBlocked(s,f,f,f) then coral=coral+1
            if (f.previousZ<0.5 and f.z>=0.5) or (f.previousZ>=0.5 and f.z<0.5) then transitions=transitions+1
            if f.routeVisits-1>completed then completed=f.routeVisits-1
        end for
    end for
    if bounds<>0 or coral<>0
        print "FAIL scene soak bounds=";bounds;" coral=";coral
        return
    end if
    if transitions<4 or completed<2 then print "FAIL fish do not explore both sides of reef ";transitions;completed : return
    print "PASS reef interaction: ";transitions;" front/back crossings, maximum completed route visits ";completed
    print "PASS close-reef scene soak: 600 simulated seconds, six enlarged fish, zero boundary or coral intersections"
end sub
