' Production atlas regions and transforms, captured for independent mesh/pixel checks.
sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    names=species.Keys()
    for n=0 to names.Count()-1
        name=names[n] : sp=species[name] : ReefTailRigInit(sp)
        body=ReefFishFrames({part:"body",file:sp.image},sp.frames,"High",true)
        tails=ReefFishFrames({part:"tail",file:sp.tailImage},sp.tailFrames,"High")
        fins=ReefFishFrames({part:"fin",file:sp.finImage},sp.finFrames,"High")
        if n=0
            fractional=ReefFishFrames({part:"body",file:sp.image},[sp.frames[0]],"High",true,true)
            integer=ReefFishFrames({part:"body",file:sp.image},[sp.frames[0]],"High",true,false)
            if fractional[0].normal<>invalid or fractional[0].fractional=invalid then print "FAIL unused normal region retained" : return
            if integer[0].fractional<>invalid or integer[0].normal=invalid then print "FAIL unused fractional region retained" : return
        end if
        sp.Delete("frames") : sp.Delete("tailFrames") : sp.Delete("finFrames")
        a={fish:{},tails:{},fins:{}} : a.fish[name]=body : a.tails[name]=tails : a.fins[name]=fins
        s={camera:64#,displayTime:0#,lighting:[1#,0#,0#,0#],settings:{lighting:"Sunset"}}
        for direction=0 to 7
            heading=direction*6.283185307#/8#+.03
            for phaseIndex=0 to 7
                phase=phaseIndex*6.283185307#/8#+.13
                for resolution=0 to 1
                    for backend=0 to 1
                        screen={draws:[],DrawTransformedObject:JointCapture}
                        outputScale=1#
                        if resolution=1 then outputScale=2#/3#
                        r={screen:screen,scale:outputScale,canvasOffset:64#,rotation:true,fractionalFish:backend=0,placement:{}}
                        f={name:name,sp:sp,size:1#,speed:sp.speed,renderPose:{x:900#,y:400#,z:.7,heading:heading,pitch:.12,phase:phase,finPhase:.3}}
                        ReefDrawFish(r,s,a,f)
                        print "JOINT ";FormatJson({name:name,heading:heading,phase:phase,pitch:.12,scale:outputScale,fractional:backend=0,canvas:64#,p:f.screenPose,view:f.renderView,body:f.bodyView,fishScale:f.screenPose.scale*sp.length/sp.renderLength,draws:screen.draws})
                    end for
                end for
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
    if source.part<>"fin"
        m.draws.Push({x:x,y:y,angle:angle,sx:sx,sy:sy,part:source.part,file:source.file,cropX:source.x,cropY:source.y,w:source.w,h:source.h,px:source.px,py:source.py,alpha:tint and 255})
    end if
    return true
end function
