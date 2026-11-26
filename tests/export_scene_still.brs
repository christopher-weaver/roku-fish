sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occupancy=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    s=ReefWorld(ReefValidateSettings(invalid),species,occupancy,47831)
    for tick=1 to 90
        ReefAdvance(s,1#/60#)
    end for
    s.camera=ReefCamera(1.5,s.settings.camera,s.cfg.camera)
    ExportFrame(s)
end sub
sub ExportFrame(s as object)
    frame={time:s.time,displayTime:s.displayTime,camera:s.camera,fish:[],effects:[],clam:{event:s.clam.event,released:s.clam.released,enabled:s.clam.enabled,escape:s.clam.escape,opening:ReefClamDisplayOpening(s),bubbles:s.clam.bubbles},bioluminescence:s.bioluminescence}
    for fishIndex=0 to s.fish.Count()-1
        f=s.fish[fishIndex]
        pose=ReefSwimPose(ReefDisplayPose(f,s.renderAlpha),f.sp,f.speed)
        p=ReefProjection(pose,s.camera)
        frame.fish.Push({id:f.id,emerging:f.emerging,name:f.name,x:f.x,y:f.y,z:pose.z,sx:p.x,sy:p.y,scale:p.scale,heading:pose.heading,pitch:pose.pitch,phase:pose.phase,finPhase:pose.finPhase,size:f.size,speed:f.speed,vx:f.vx,vy:f.vy,vz:f.vz,yawVelocity:f.yawVelocity,state:f.state})
    end for
    for each e in s.effects
        pose=ReefEffectPose(e,s.renderAlpha)
        frame.effects.Push({x:pose.x,y:pose.y,z:e.z,bubble:e.bubble,active:e.active,phase:e.phase})
    end for
    if s.time<0 then frame.time=-1#
    print "FRAME ";FormatJson(frame)
end sub
