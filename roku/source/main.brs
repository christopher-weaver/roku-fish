' Native, standalone screensaver. There is intentionally no Main / RunUserInterface.
sub RunScreenSaver()
    settings = ReefLoadSettings()
    port = CreateObject("roMessagePort")
    screen = invalid
    if settings.quality <> "Performance" then screen = CreateObject("roScreen", true, 1920, 1080)
    if screen = invalid then screen = CreateObject("roScreen", true, 1280, 720)
    if screen = invalid
        print "Deep Reef: display initialization failed"
        return
    end if
    screen.SetMessagePort(port)
    monitor = ReefMemoryMonitor(port)
    species = ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occupancy = ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    if species = invalid then return
    date = CreateObject("roDateTime")
    ' Seed changes between sessions; all random state is private and reproducible in tests.
    seed = date.AsSeconds() mod 2147483646
    if seed <= 0 then seed = 47831
    s = ReefWorld(settings, species, occupancy, seed)
    assets = ReefLoadAssets(s)
    renderer = ReefRenderer(screen, settings)
    timer = CreateObject("roTimespan")
    last = 0# : nextFrame = 0# : sampleAt = 0# : localAt = -2#
    hour = 12#
    while true
        nowMs = CDbl(timer.TotalMilliseconds())
        ' Restart the 32-bit millisecond clock daily, before it can overflow.
        if nowMs >= 86400000#
            timer.Mark() : nowMs = 0# : last = 0# : nextFrame = 0# : sampleAt = 0# : localAt = -2#
        end if
        elapsed = (nowMs - last) / 1000#
        last = nowMs
        if nowMs / 1000# - localAt >= 1
            date.Mark() : date.ToLocalTime()
            hour = date.GetHours() + date.GetMinutes() / 60# + date.GetSeconds() / 3600#
            minute = date.GetMinutes().ToStr()
            if Len(minute) < 2 then minute = "0" + minute
            s.clockText = date.GetHours().ToStr() + ":" + minute
            localAt = nowMs / 1000#
        end if
        ReefStep(s, elapsed)
        ReefLightingStep(s, hour, elapsed)
        ReefRender(renderer, s, assets)
        screen.SwapBuffers()
        s.frames = s.frames + 1 : s.sampleFrames = s.sampleFrames + 1
        if nowMs - sampleAt >= 4000
            ReefQualitySample(s, (nowMs - sampleAt) / 1000#, s.sampleFrames)
            print "Deep Reef FPS="; s.fps; " quality="; s.quality
            sampleAt = nowMs : s.sampleFrames = 0
        end if
        msg = port.GetMessage()
        while msg <> invalid
            kind = Type(msg)
            ' The OS normally dismisses this context. If an input event arrives, exit immediately.
            if kind = "roUniversalControlEvent" then return
            if kind = "roDeviceInfoEvent" or kind = "roAppMemoryNotificationEvent"
                s.quality = 0.3
                RunGarbageCollector()
            end if
            msg = port.GetMessage()
        end while
        nextFrame = nextFrame + 1000# / 30#
        current = CDbl(timer.TotalMilliseconds())
        if nextFrame < current - 34 then nextFrame = current
        remaining = Int(nextFrame - current)
        if remaining > 0 then Sleep(remaining)
    end while
end sub

' Held for the context lifetime. These are the documented memory-monitor interfaces.
' This helper adapts the guarded initialization pattern in Reef Glass (Apache-2.0).
function ReefMemoryMonitor(port as object) as object
    mon = { device: CreateObject("roDeviceInfo"), app: CreateObject("roAppMemoryMonitor") }
    try
        mon.device.SetMessagePort(port)
        mon.device.EnableLowGeneralMemoryEvent(true)
    catch error
        print "Deep Reef: general memory notifications unavailable"
    end try
    try
        mon.app.SetMessagePort(port)
        mon.app.EnableMemoryWarningEvent(true)
    catch error
        print "Deep Reef: app memory notifications unavailable"
    end try
    return mon
end function
