sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    s=ReefWorld(ReefValidateSettings(invalid),species,invalid,47831)
    screen={calls:[],DrawScaledObject:ContentCapture,DrawObject:ContentObject}
    r={screen:screen,scale:1#,canvasOffset:0#,clamBounds:{active:false}}
    a={pearl:{normal:"pearl"},bubble:{normal:"bubble"}}
    s.clam.event=0 : s.clam.released=false
    for timeIndex=0 to 2
        s.displayTime=timeIndex*2# : screen.calls=[]
        ReefDrawClamContents(r,s,a)
        if screen.calls.Count()<>1 or screen.calls[0].alpha<>255 then print "FAIL pearl must exist at full opacity before opening" : return
    end for
    s.clam.event=1 : screen.calls=[] : s.displayTime=0#
    ReefDrawClamContents(r,s,a)
    if screen.calls.Count()<>12 then print "FAIL bubble cluster not prepared inside closed shell" : return
    start=screen.calls[0] : e=s.clam.bubbles[0]
    s.clam.released=true : e.born=0# : screen.calls=[]
    ReefDrawClamContents(r,s,a)
    if screen.calls[0].x<>start.x or screen.calls[0].y<>start.y then print "FAIL bubble teleports when shell releases it" : return
    s.displayTime=1# : screen.calls=[] : ReefDrawClamContents(r,s,a)
    if screen.calls[0].y>=start.y then print "FAIL contained bubble does not rise" : return
    print "PASS pearl and the same bubble cluster exist before opening, use shell occlusion instead of fading, and release without position jumps"
end sub
function ContentCapture(x as integer,y as integer,sx as float,sy as float,source as dynamic,tint as integer) as boolean
    m.calls.Push({x:x,y:y,source:source,alpha:tint and 255}) : return true
end function
function ContentObject(x as integer,y as integer,source as dynamic,tint as integer) as boolean
    m.calls.Push({x:x,y:y,source:source,alpha:tint and 255}) : return true
end function
