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
        ExportFrame(s)
        ReefAdvance(s,0.1)
    end for
end sub
sub ExportFrame(s as object)
    frame={time:s.time,displayTime:s.displayTime,camera:s.camera,fish:[],effects:[]}
    for each f in s.fish
        pose=ReefDisplayPose(f,s.renderAlpha)
        p=ReefProjection(pose,s.camera)
        frame.fish.Push({id:f.id,name:f.name,x:f.x,y:f.y,z:f.z,sx:p.x,sy:p.y,scale:p.scale,heading:pose.heading,pitch:pose.pitch,phase:pose.phase,finPhase:pose.finPhase,size:f.size,state:f.state})
    end for
    for each e in s.effects
        pose=ReefEffectPose(e,s.renderAlpha)
        frame.effects.Push({x:pose.x,y:pose.y,z:e.z,bubble:e.bubble,active:e.active})
    end for
    print "FRAME ";FormatJson(frame)
end sub
