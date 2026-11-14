sub Main()
    for each width in [1280,1920]
        scale=width/1920#
        for sample=0 to 180
            camera=ReefCamera(60#+sample/60#, "Slow")
            expected=-camera*scale
            transform=ReefLayerTransform(expected,-36#*scale,scale,scale)
            if Abs(transform.x+65536#*transform.sx-expected)>0.00001 then print "FAIL fractional geometry" : return
            print "PAN ";FormatJson({width:width,target:expected,targetScale:scale,transform:transform})
        end for
    end for
    pixels=[]
    for i=0 to 1535
        pixels.Push(0)
    end for
    for column=0 to 23
        pixels[(4*24+column)*4]=255
        pixels[(11*24+column)*4]=255
    end for
    ' ARGB readback: alpha is constant, so the red channel must identify the stripe.
    pixels[(4*24+9)*4+1]=255
    pixels[(11*24+9)*4+1]=191
    pixels[(11*24+10)*4+1]=64
    if not ReefFractionalPixelsValid(pixels) then print "FAIL fractional GPU probe acceptance" : return
    for column=0 to 23
        top=(4*24+column)*4+1 : bottom=(11*24+column)*4+1
        value=pixels[top] : pixels[top]=pixels[bottom] : pixels[bottom]=value
    end for
    if not ReefFractionalPixelsValid(pixels) then print "FAIL flipped readback acceptance" : return
    pixels[(4*24+9)*4+1]=255 : pixels[(4*24+10)*4+1]=0
    pixels[(11*24+9)*4+1]=255 : pixels[(11*24+10)*4+1]=0
    if ReefFractionalPixelsValid(pixels) then print "FAIL integer-only GPU probe rejection" : return
    print "PASS fractional pan math and GPU probe distinguish smooth placement from integer stepping"
end sub
