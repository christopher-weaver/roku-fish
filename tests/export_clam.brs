sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occ=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    s=ReefWorld(ReefValidateSettings(invalid),species,occ,47831)
    s.clam.order=[2,0,1] : s.renderAlpha=1#
    ReefClamStep(s) : ExportClamPose(s)
    s.time=6# : s.clam.lastTime=6# : ReefClamStep(s) : ExportClamPose(s)
    for i=1 to 46
        ReefSavePose(s.clam.baby)
        s.time=6#+i*.1 : ReefClamStep(s)
        if i=20 or i=46 then ExportClamPose(s)
    end for
end sub
sub ExportClamPose(s as object)
    s.displayTime=s.time : s.camera=ReefCamera(s.time,s.settings.camera,s.cfg.camera)
    ExportFrame(s)
end sub
sub ExportFrame(s as object)
    frame={time:s.time-60#,displayTime:s.displayTime,camera:s.camera,fish:[],effects:[],clam:{event:s.clam.event,enabled:s.clam.enabled,escape:s.clam.escape,opening:ReefClamDisplayOpening(s),bubbles:s.clam.bubbles},bioluminescence:s.bioluminescence}
    for each f in s.fish
        pose=ReefSwimPose(ReefDisplayPose(f,s.renderAlpha),f.sp,f.speed)
        p=ReefProjection(pose,s.camera)
        frame.fish.Push({id:f.id,emerging:f.emerging,name:f.name,x:f.x,y:f.y,z:pose.z,sx:p.x,sy:p.y,scale:p.scale,heading:pose.heading,pitch:pose.pitch,phase:pose.phase,finPhase:pose.finPhase,size:f.size,speed:f.speed,state:f.state})
    end for
    for each e in s.effects
        pose=ReefEffectPose(e,s.renderAlpha)
        frame.effects.Push({x:pose.x,y:pose.y,z:e.z,bubble:e.bubble,active:e.active,phase:e.phase})
    end for
    if s.time<0 then frame.time=-1#
    print "FRAME ";FormatJson(frame)
end sub
