sub RunScreenSaverSettings()
    screen = CreateObject("roSGScreen")
    if screen = invalid then return
    port = CreateObject("roMessagePort")
    screen.SetMessagePort(port)
    monitor = ReefMemoryMonitor(port)
    scene = screen.CreateScene("ReefSettings")
    if scene = invalid then return
    scene.ObserveField("preferences", port)
    scene.ObserveField("closeRequested", port)
    scene.preferences = ReefLoadSettings()
    screen.Show()
    scene.SetFocus(true)
    while true
        msg = Wait(100, port)
        ' Poll as well as observing: closing must not depend on a queued field notification.
        if scene.closeRequested
            ReefSaveSettings(scene.preferences)
            screen.Close()
            return
        end if
        kind = Type(msg)
        if kind = "roSGScreenEvent"
            if msg.IsScreenClosed() then return
        else if kind = "roSGNodeEvent"
            field = msg.GetField()
            if field = "preferences" then ReefSaveSettings(scene.preferences)
            if field = "closeRequested" and scene.closeRequested
                ReefSaveSettings(scene.preferences)
                screen.Close()
                return
            end if
        end if
    end while
end sub
