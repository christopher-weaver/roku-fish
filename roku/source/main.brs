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
    renderer = ReefRenderer(screen, settings)
    assets = ReefLoadAssets(s,renderer.fractionalFish)
    ' Release initialization garbage before starting the animation clock.
    RunGarbageCollector()
    timer = CreateObject("roTimespan")
    last = 0# : nextFrame = 0# : sampleAt = 0# : localAt = -2#
    hour = 12# : profile=ReefNewFrameProfile() : lastGC=0#-10000# : pacing=invalid
    gcPendingApp=false : gcPendingGeneral=false
    clockOffsetMs=0#
    while true
        nowMs = CDbl(timer.TotalMilliseconds())
        elapsed = (nowMs - last) / 1000#
        ' Restart the 32-bit millisecond clock daily, before it can overflow.
        if nowMs >= 86400000#
            clockOffsetMs=clockOffsetMs+nowMs
            timer.Mark() : nowMs = 0# : last = 0# : nextFrame = 0# : sampleAt = 0# : localAt = -2# : profile=ReefNewFrameProfile()
            s.sampleFrames=0
            lastGC=0#-10000#
        end if
        last = nowMs
        if nowMs / 1000# - localAt >= 1
            date.Mark() : date.ToLocalTime()
            hour = date.GetHours() + date.GetMinutes() / 60# + date.GetSeconds() / 3600#
            minute = date.GetMinutes().ToStr()
            if Len(minute) < 2 then minute = "0" + minute
            s.clockText = date.GetHours().ToStr() + ":" + minute
            localAt = nowMs / 1000#
        end if
        beforeSim=s.time
        ReefAdvance(s, elapsed)
        ' The camera follows the display clock even if physics catch-up is capped.
        s.camera=ReefCamera((clockOffsetMs+nowMs)/1000#,settings.camera,s.cfg.camera)
        ReefLightingStep(s, hour, elapsed)
        updateDone=CDbl(timer.TotalMilliseconds())
        ticks=Int((s.time-beforeSim)*30#+.5)
        ReefRender(renderer, s, assets)
        drawDone=CDbl(timer.TotalMilliseconds())
        ' The double-buffered swap paces 60Hz directly. The 30Hz mode waits
        ' before submission; sleeping after a swap can miss the next refresh.
        pacing = ReefFrameSchedule(drawDone, nextFrame, s.renderFps,pacing)
        nextFrame = pacing.deadline
        if pacing.sleepMs > 0 then Sleep(pacing.sleepMs)
        waitDone=CDbl(timer.TotalMilliseconds())
        screen.SwapBuffers()
        swapDone=CDbl(timer.TotalMilliseconds())
        s.frames = s.frames + 1 : s.sampleFrames = s.sampleFrames + 1
        msg = port.GetMessage()
        while msg <> invalid
            kind = Type(msg)
            ' The OS normally dismisses this context. If an input event arrives, exit immediately.
            if kind = "roUniversalControlEvent" then return
            if kind = "roDeviceInfoEvent" or kind = "roAppMemoryNotificationEvent"
                profile.memoryEvents=profile.memoryEvents+1
                if kind="roAppMemoryNotificationEvent"
                    gcPendingApp=ReefMemoryPressure(kind,msg.GetInfo())
                else
                    gcPendingGeneral=ReefMemoryPressure(kind,msg.GetInfo())
                end if
            end if
            msg = port.GetMessage()
        end while
        if (gcPendingApp or gcPendingGeneral) and swapDone-lastGC>=10000#
            print "Deep Reef: collecting under memory pressure"
            s.quality=.3 : RunGarbageCollector() : lastGC=CDbl(timer.TotalMilliseconds())
            gcPendingApp=false : gcPendingGeneral=false
        end if
        finished=CDbl(timer.TotalMilliseconds())
        ReefProfileFrame(profile,updateDone-nowMs,drawDone-updateDone,waitDone-drawDone,swapDone-waitDone,finished-swapDone,finished-nowMs,ticks)
        if finished-sampleAt>=4000
            busy=ReefProfileMs(profile.updateMs+profile.drawMs+profile.eventsMs,profile.frames)
            swap=ReefProfileMs(profile.swapMs,profile.frames)
            ReefQualitySample(s,(finished-sampleAt)/1000#,s.sampleFrames,busy,swap)
            report=ReefProfileSummary(profile,s,renderer)
            report.uptime_seconds=Int((clockOffsetMs+finished)/1000#)
            report.asset_memory=s.assetMemory
            if s.memoryProbeSupported<>false
                try
                    report.memory_percent=monitor.app.GetMemoryLimitPercent()
                    report.available_memory_kb=monitor.app.GetChannelAvailableMemory()
                catch error
                    s.memoryProbeSupported=false
                end try
            end if
            print "Deep Reef FPS=";s.fps;" quality=";s.quality
            print "Deep Reef PERF ";FormatJson(report)
            s.perfText="U "+Int(report.update_ms).ToStr()+" D "+Int(report.draw_ms).ToStr()+" S "+Int(report.swap_ms).ToStr()+" E "+Int(report.events_ms).ToStr()+" ms"
            s.perfText=s.perfText+" N "+report.fish.ToStr()
            if report.memory_percent<>invalid then s.perfText=s.perfText+" M "+report.memory_percent.ToStr()+"%"
            sampleAt=finished : s.sampleFrames=0 : profile=ReefNewFrameProfile()
        end if
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
