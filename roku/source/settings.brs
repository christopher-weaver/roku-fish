sub RunScreenSaverSettings()
    screen = CreateObject("roSGScreen")
    if screen = invalid then return
    port = CreateObject("roMessagePort")
    screen.SetMessagePort(port)
    monitor = ReefMemoryMonitor(port)
    scene = screen.CreateScene("ReefSettings")
    if scene = invalid then return
    scene.ObserveField("preferences", port)
    scene.ObserveField("done", port)
    scene.preferences = ReefLoadSettings()
    screen.Show()
    while true
        msg = Wait(0, port)
        kind = Type(msg)
        if kind = "roSGScreenEvent"
            if msg.IsScreenClosed() then return
        else if kind = "roSGNodeEvent"
            field = msg.GetField()
            if field = "preferences" then ReefSaveSettings(scene.preferences)
            if field = "done" then screen.Close() : return
        end if
    end while
end sub
