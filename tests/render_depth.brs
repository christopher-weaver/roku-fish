' Exercise production draw ordering and view weights without claiming GPU pixels.
sub Main()
    prefs=ReefValidateSettings({density:"Low",particles:"Off",bubbles:"Off"})
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    s=ReefWorld(prefs,species,invalid,91)
    while s.fish.Count()>3
        s.fish.Pop()
    end while
    depths=[0.16,0.55,0.94]
    a={plate:{normal:"water"},fish:{},fins:{},tails:{},formations:[],surfaceShadows:[],eel:{normal:"eel"},cave:{normal:"cave"},eelErase:{normal:"erase"},surface:[],caustics:[],ray:{normal:"ray"}}
    for i=0 to 2
        f=s.fish[i] : f.z=depths[i] : f.x=900# : f.y=400# : f.heading=3.14 : f.phase=0# : f.finPhase=0.3
        ReefSavePose(f)
        body=[] : fins=[] : tails=[]
        for j=0 to f.sp.frames.Count()-1
            body.Push({normal:"body:"+f.name})
        end for
        for j=0 to f.sp.finFrames.Count()-1
            fins.Push({normal:"fin:"+f.name})
        end for
        for j=0 to f.sp.tailFrames.Count()-1
            tails.Push({normal:"tail:"+f.name})
        end for
        a.tails[f.name]=tails
        a.fish[f.name]=body : a.fins[f.name]=fins
    end for
    for i=0 to s.cfg.formations.Count()-1
        views=[]
        for view=0 to s.cfg.formations[i].frames-1
            views.Push({normal:"reef:"+s.cfg.formations[i].id})
        end for
        a.formations.Push(views)
        shadows=[]
        if s.cfg.formations[i].surfaceShadow<>invalid
            for phase=0 to 31
                shadows.Push({normal:"shadow:"+s.cfg.formations[i].id})
            end for
        end if
        a.surfaceShadows.Push(shadows)
    end for
    screen={calls:[],SetAlphaEnable:RenderAlpha,Clear:RenderClear,DrawScaledObject:RenderScaled,DrawObject:RenderObject}
    r={screen:screen,scale:1#,rotation:false,fractionalPan:false,fractionalFish:false,placement:{}}
    ReefRender(r,s,a)
    order={} : count={} : blends=0 : reflected=0
    for i=0 to screen.calls.Count()-1
        call=screen.calls[i] : order[call.source]=i
        if not count.DoesExist(call.source) then count[call.source]=0
        count[call.source]=count[call.source]+1
        if call.source="water" and call.tint<>&hFFFFFFFF then print "FAIL water plate tinted" : return
        if Left(call.source,5)="body:"
            if call.alpha>0 and call.alpha<255 then blends=blends+1
            if call.sx<0 then reflected=reflected+1
        end if
    end for
    if order["body:"+s.fish[0].name]>=order["reef:sea-fan"] then print "FAIL rear fish ordering" : return
    if order["body:"+s.fish[1].name]<=order["reef:connected-reef"] or order["body:"+s.fish[1].name]>=order["reef:foreground-reef"] then print "FAIL mid-ground fish ordering" : return
    if order["body:"+s.fish[2].name]<=order["reef:sea-anemone"] then print "FAIL front fish ordering" : return
    for i=0 to 2
        name=s.fish[i].name
        if count["body:"+name]<>1 or count["fin:"+name]<>1 or count["tail:"+name]<>1 then print "FAIL body or fin view blend" : return
    end for
    if count["reef:sea-fan"]<>1 or count["reef:sea-anemone"]<>1 then print "FAIL marine object fragmented" : return
    if count.DoesExist("net") then print "FAIL water darkening overlay" : return
    if count["shadow:connected-reef"]<>2 or count["shadow:foreground-reef"]<>2 then print "FAIL surface shadow drawing" : return
    if order["shadow:connected-reef"]>=order["body:"+s.fish[1].name] then print "FAIL surface/actor shadow order" : return
    if order["eel"]>=order["reef:connected-reef"] then print "FAIL eel tunnel occlusion" : return
    if blends<>0 or reflected<>0 then print "FAIL blend alpha or reflection ";blends;reflected : return
    print "PASS production renderer interleaves rear, middle and front fish with connected reef layers and rendered marine life; exactly one opaque body, one separate tail and one fin per fish, positive scales only"
end sub
sub RenderAlpha(enabled as boolean)
end sub
sub RenderClear(color as integer)
end sub
function RenderScaled(x as integer,y as integer,sx as float,sy as float,source as dynamic,tint as integer) as boolean
    m.calls.Push({source:source,sx:sx,alpha:tint and 255,tint:tint})
    return true
end function

function RenderObject(x as integer,y as integer,source as dynamic,tint as integer) as boolean
    m.calls.Push({source:source,sx:1#,alpha:tint and 255,tint:tint})
    return true
end function
