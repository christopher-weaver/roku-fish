sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    names=["copperband_butterflyfish","blue_tang","emperor_angelfish"]
    for n=0 to names.Count()-1
        name=names[n] : sp=species[name] : ReefTailRigInit(sp)
        a={fish:{},tails:{},fins:{},turnCores:{}}
        a.fish[name]=ReefFishFrames({part:"body",file:sp.image},sp.frames,"High",true,true)
        a.tails[name]=ReefFishFrames({part:"tail",file:sp.tailImage},sp.tailFrames,"High",false,true)
        a.fins[name]=ReefFishFrames({part:"fin",file:sp.finImage},sp.finFrames,"High",false,true)
        if sp.turnCoreFrames<>invalid then a.turnCores[name]=ReefFishFrames({part:"body",file:sp.turnCoreImage},sp.turnCoreFrames,"High",false,true)
        s={camera:64#,displayTime:0#,lighting:[1#,0#,0#,0#],settings:{lighting:"Sunset"}}
        for tick=0 to 180
            screen={draws:[],DrawTransformedObject:JointCapture}
            r={screen:screen,scale:1#,canvasOffset:0#,rotation:true,fractionalFish:true,placement:{}}
            f={name:name,sp:sp,size:1#,speed:sp.speed,renderPose:{x:900#,y:400#,z:.7,heading:tick/57.295779513#,pitch:.2,phase:0#,finPhase:.3,yawVelocity:.3}}
            ReefDrawFish(r,s,a,f)
            print "TURN ";FormatJson({name:name,tick:tick,p:f.screenPose,heading:f.swimPose.heading,draws:screen.draws})
        end for
    end for
end sub
function JointRegion(bitmap as object,x as integer,y as integer,w as integer,h as integer) as object
    return {part:bitmap.part,file:bitmap.file,x:x,y:y,w:w,h:h,SetPretranslation:JointTranslate,SetScaleMode:JointScale}
end function
sub JointTranslate(x as integer,y as integer)
    m.px=x : m.py=y
end sub
sub JointScale(mode as integer)
end sub
function JointCapture(x as integer,y as integer,angle as float,sx as float,sy as float,source as object,tint as integer) as boolean
        m.draws.Push({x:x,y:y,angle:angle,sx:sx,sy:sy,part:source.part,file:source.file,cropX:source.x,cropY:source.y,w:source.w,h:source.h,px:source.px,py:source.py,alpha:tint and 255,rgba:tint})
    return true
end function
