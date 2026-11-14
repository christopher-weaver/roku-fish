sub Main()
    for each width in [1280,1920]
        scale=width/1920#
        for sample=0 to 180
            camera=ReefCamera(60#+sample/60#,"Slow")
            target=0#-camera*scale
            phase=ReefPixelPhase(target)
            alpha=Int(phase.blend*255+0.5)
            centroid=phase.first+alpha/255#
            if Abs(centroid-target)>0.002 then print "FAIL adjacent pixel pan" : return
            print "PAN ";FormatJson({width:width,target:target,first:phase.first,alpha:alpha})
        end for
    end for
    print "PASS opaque canvas pan uses adjacent integer positions with continuous alpha, independent of GPU scale precision"
end sub
