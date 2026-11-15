sub Main()
    sp=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))["yellow_tang"]
    body=[] : fins=[] : tails=[]
    for i=0 to sp.frames.Count()-1
        body.Push({normal:"body",fractional:"body"})
    end for
    for i=0 to sp.finFrames.Count()-1
        fins.Push({normal:"fin",fractional:"fin"})
    end for
    for i=0 to sp.tailFrames.Count()-1
        tails.Push({normal:"tail",fractional:"tail"})
    end for
    screen={bad:false,calls:0,DrawTransformedObject:UprightCapture}
    r={screen:screen,scale:1#,canvasOffset:0#,rotation:true,fractionalFish:true,placement:{}}
    s={camera:64#,settings:{lighting:"Sunset"}}
    a={fish:{yellow_tang:body},fins:{yellow_tang:fins},tails:{yellow_tang:tails}}
    f={name:"yellow_tang",sp:sp,size:1#}
    for degrees=0 to 360 step 3
        f.renderPose={x:900#,y:400#,z:0.7,heading:degrees/57.295779513#,pitch:Sin(degrees/57.295779513#)*0.22,phase:degrees*0.1,finPhase:degrees*0.2}
        ReefDrawFish(r,s,a,f)
    end for
    if screen.bad or screen.calls<>363 then print "FAIL upright transforms" : return
    print "PASS full-circle pitched fish draw body, tail and fins with positive scales only; no runtime reflections"
    output={calls:[],SetAlphaEnable:PresentAlpha,Clear:PresentClear,DrawScaledObject:PresentCapture,DrawObject:PresentObject}
    s.settings.clock="Off" : s.settings.fps="Off"
    for each scale in [0.6666666667,1#]
        r={output:output,frame:"opaque-frame",outputScale:scale}
        previous=invalid
        for frame=0 to 120
            output.calls=[] : s.camera=ReefCamera(60#+frame/60#,"Slow")
            ReefPresent(r,s)
            first=output.calls[0]
            if first.alpha<>255 then print "FAIL base canvas opacity" : return
            centroid=first.x
            if output.calls.Count()=2
                nextCall=output.calls[1]
                if nextCall.x<>first.x+1 then print "FAIL nonadjacent pan" : return
                centroid=centroid+nextCall.alpha/255#
            end if
            if Abs(centroid+s.camera*scale)>0.002 then print "FAIL pan center" : return
            if previous<>invalid
                if Abs(centroid-previous)>0.04 then print "FAIL pan jump" : return
            end if
            previous=centroid
        end for
    end for
    print "PASS production presentation blends an opaque canvas at adjacent pixels, at HD/FHD, without anchor transforms"
end sub
function UprightCapture(x as integer,y as integer,angle as float,sx as float,sy as float,source as dynamic,tint as integer) as boolean
    if sx<=0 or sy<=0 or Abs(angle)>13 or (tint and 255)<>255 then m.bad=true
    m.calls=m.calls+1
    return true
end function
sub PresentAlpha(enabled as boolean)
end sub
sub PresentClear(color as integer)
end sub
function PresentCapture(x as integer,y as integer,sx as float,sy as float,source as dynamic,tint as integer) as boolean
    m.calls.Push({x:x,alpha:tint and 255})
    return true
end function

function PresentObject(x as integer,y as integer,source as dynamic,tint as integer) as boolean
    m.calls.Push({x:x,alpha:tint and 255})
    return true
end function
