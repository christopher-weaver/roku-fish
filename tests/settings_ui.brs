sub Main()
    m.top = {preferences:ReefValidateSettings(invalid), closeRequested:false, nodes:{}, currentDesignResolution:{width:1280,height:720}, FindNode:SettingsFindNode, SetFocus:SettingsSetFocus}
    m.top.nodes.layout = {scale:[1,1]}
    m.top.nodes.highlight = {translation:[125,240]}
    m.top.nodes.rows = {}
    for i=0 to 10
        m.top.nodes["label"+i.ToStr()] = {text:""}
        m.top.nodes["value"+i.ToStr()] = {text:""}
    end for
    init()
    if Abs(m.top.nodes.layout.scale[0]-2/3)>0.00001 or Abs(m.top.nodes.layout.scale[1]-2/3)>0.00001 then print "FAIL HD menu scale" : return
    m.top.currentDesignResolution={width:1920,height:1080}
    init()
    if m.top.nodes.layout.scale[0]<>1 or m.top.nodes.layout.scale[1]<>1 then print "FAIL FHD menu scale" : return
    print "PASS complete settings layout fits HD and FHD resolutions"
    for i=0 to 10
        if Len(m.labels[i].text)=0 then print "FAIL empty settings label ";i : return
    end for
    for i=0 to 8
        if Len(m.values[i].text)=0 then print "FAIL empty settings value ";i : return
    end for
    print "PASS all setting labels, values and actions have visible text"
    original=m.top.preferences.lighting
    handled=onKeyEvent("right",true)
    if not handled or m.top.preferences.lighting=original then print "FAIL setting edit" : return
    print "PASS remote edits preferences"
    handled=onKeyEvent("up",true)
    if m.index<>10 then print "FAIL navigation wrap" : return
    handled=onKeyEvent("OK",true)
    if not m.top.closeRequested then print "FAIL Done exit" : return
    print "PASS Done requests screen closure"
    m.top.closeRequested=false
    handled=onKeyEvent("back",false)
    if handled or m.top.closeRequested then print "FAIL key release" : return
    handled=onKeyEvent("back",true)
    if not handled or not m.top.closeRequested then print "FAIL Back exit" : return
    print "PASS Back requests screen closure and consumes the key"
    m.top.closeRequested=false : m.index=9
    handled=onKeyEvent("OK",true)
    if m.top.preferences.lighting<>original or m.top.closeRequested then print "FAIL restore defaults" : return
    print "PASS Restore Defaults preserves the open settings screen"
end sub
function SettingsFindNode(id as string) as object
    return m.nodes[id]
end function
sub SettingsSetFocus(focus as boolean)
end sub
