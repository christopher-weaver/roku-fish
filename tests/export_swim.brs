sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    names=["blue_tang","emperor_angelfish"]
    for n=0 to 1
        name=names[n] : sp=species[name] : ReefTailRigInit(sp)
        body=ReefFishFrames({part:"body",file:sp.image},sp.frames,"High",true,true)
        tails=ReefFishFrames({part:"tail",file:sp.tailImage},sp.tailFrames,"High",false,true)
        fins=ReefFishFrames({part:"fin",file:sp.finImage},sp.finFrames,"High",false,true)
        a={fish:{},tails:{},fins:{}} : a.fish[name]=body : a.tails[name]=tails : a.fins[name]=fins
        s={camera:64#,displayTime:0#,lighting:[1#,0#,0#,0#],settings:{lighting:"Sunset"}}
        for view=0 to 4
            heading=0# : yawVelocity=0#
            if view=1 then heading=.6
            if view=2 then heading=1.570796327#
            if view=3 then heading=.6 : yawVelocity=.24
            if view=4 then heading=.6 : yawVelocity=-.24
            for tick=0 to 35
                screen={draws:[],DrawTransformedObject:JointCapture}
                r={screen:screen,scale:1#,canvasOffset:0#,rotation:true,fractionalFish:true,placement:{}}
                f={name:name,sp:sp,size:.9,speed:sp.speed,renderPose:{x:900.25,y:400.25,z:.7,heading:heading,pitch:0#,phase:tick*6.283185307#/36#,finPhase:.4,yawVelocity:yawVelocity}}
                ReefDrawFish(r,s,a,f)
                print "SWIM ";FormatJson({name:name,view:view,tick:tick,p:f.screenPose,draws:screen.draws})
            end for
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
        m.draws.Push({x:x,y:y,angle:angle,sx:sx,sy:sy,part:source.part,file:source.file,cropX:source.x,cropY:source.y,w:source.w,h:source.h,px:source.px,py:source.py,alpha:tint and 255})
    return true
end function
