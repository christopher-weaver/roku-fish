sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occ=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    high=ReefWorld(ReefValidateSettings({density:"High"}),species,occ,47831)
    high.time=-1# : ExportFrame(high)
    s=ReefWorld(ReefValidateSettings(invalid),species,occ,47831)
    s.time=60# : s.displayTime=60# : s.camera=ReefCamera(60#,"Slow",s.cfg.camera)
    for tick=0 to 30
        ExportFrame(s)
        ReefAdvance(s,0.1)
    end for
end sub
sub ExportFrame(s as object)
    frame={time:s.time-60#,displayTime:s.displayTime,camera:s.camera,fish:[],effects:[]}
    for each f in s.fish
        pose=ReefDisplayPose(f,s.renderAlpha)
        p=ReefProjection(pose,s.camera)
        frame.fish.Push({id:f.id,name:f.name,x:f.x,y:f.y,z:pose.z,sx:p.x,sy:p.y,scale:p.scale,heading:pose.heading,pitch:pose.pitch,phase:pose.phase,finPhase:pose.finPhase,size:f.size,state:f.state})
    end for
    for each e in s.effects
        pose=ReefEffectPose(e,s.renderAlpha)
        frame.effects.Push({x:pose.x,y:pose.y,z:e.z,bubble:e.bubble,active:e.active})
    end for
    if s.time<0 then frame.time=-1#
    print "FRAME ";FormatJson(frame)
end sub
