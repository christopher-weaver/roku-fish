sub Main()
    prefs=ReefValidateSettings(invalid)
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occupancy=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    s=ReefWorld(prefs,species,occupancy,47831)
    highPrefs=ReefValidateSettings({density:"High"})
    highWorld=ReefWorld(highPrefs,species,occupancy,47831)
    highWorld.time=-1#
    ExportFrame(highWorld)
    for i=0 to 600
        if i mod 10=0 then ExportFrame(s)
        ReefStep(s,0.1)
    end for
end sub
sub ExportFrame(s as object)
    frame={time:s.time,camera:s.camera,fish:[],effects:[]}
    for each f in s.fish
        p=ReefProjection(f,s.camera)
        frame.fish.Push({id:f.id,name:f.name,x:f.x,y:f.y,z:f.z,sx:p.x,sy:p.y,scale:p.scale,heading:f.heading,pitch:f.pitch,phase:f.phase,size:f.size,state:f.state})
    end for
    for each e in s.effects
        frame.effects.Push(e)
    end for
    print "FRAME ";FormatJson(frame)
end sub
