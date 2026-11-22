sub Main()
    hd=ReefCanvasLayout(1280,720) : fhd=ReefCanvasLayout(1920,1080)
    if hd.width<>1365 or hd.height<>720 or Abs(hd.scale-2#/3#)>.000001 then print "FAIL 720p canvas remains oversized" : return
    if fhd.width<>2048 or fhd.height<>1080 or fhd.scale<>1# then print "FAIL FHD canvas changed" : return
    p=ReefNewFrameProfile()
    ReefProfileFrame(p,2#,3#,4#,5#,6#,20#,1)
    ReefProfileFrame(p,4#,7#,0#,11#,0#,22#,3)
    p.memoryEvents=2
    s={fps:8#,renderFps:60#,settings:{quality:"High"},fish:[{},{}]}
    r={canvasWidth:2048,canvasHeight:1080,outputScale:1#,fractionalFish:true}
    data=ReefProfileSummary(p,s,r)
    if data.update_ms<>3# or data.draw_ms<>5# or data.wait_ms<>2# or data.swap_ms<>8# or data.events_ms<>3# then print "FAIL frame stage averages" : return
    if data.ticks_per_frame<>2# or data.max_update_ms<>4# or data.max_draw_ms<>7# or data.max_swap_ms<>11# or data.max_events_ms<>6# or data.max_frame_ms<>22# then print "FAIL frame stage peaks" : return
    if data.memory_events<>2 or data.fish<>2 or data.mode<>"High" or data.fps<>8# then print "FAIL diagnostic context" : return
    print "PASS native-sized HD/FHD canvases, stage averages/peaks, catch-up tick counts and memory-event diagnostics"
end sub
