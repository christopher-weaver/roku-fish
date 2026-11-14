function ReefFractionalFishProbe(screen as object, rotated as boolean) as boolean
    try
        stripe = CreateObject("roBitmap", {width:4,height:4,alphaenable:false})
        if stripe = invalid then return false
        stripe.Clear(&h000000FF) : stripe.DrawRect(1,0,1,4,&hFFFFFFFF)
        region = CreateObject("roRegion",stripe,0,0,4,4)
        if region = invalid then return false
        region.SetScaleMode(1) : region.SetPretranslation(4096,4096)
        screen.SetAlphaEnable(false) : screen.Clear(&h000000FF)
        angle = 0#
        if rotated then angle = 11.25
        first = ReefFishTransform(8#,2#,1#,1#,angle)
        second = ReefFishTransform(8.25,9#,1#,1#,angle)
        if rotated
            screen.DrawTransformedObject(first.x,first.y,first.angle,first.sx,first.sy,region)
            screen.DrawTransformedObject(second.x,second.y,second.angle,second.sx,second.sy,region)
        else
            screen.DrawScaledObject(first.x,first.y,first.sx,first.sy,region)
            screen.DrawScaledObject(second.x,second.y,second.sx,second.sy,region)
        end if
        screen.Finish()
        pixels = screen.GetByteArray(0,0,24,16)
        if pixels = invalid then return false
        return ReefFishPixelsValid(pixels)
    catch error
        print "Deep Reef: fractional fish probe unavailable"
    end try
    return false
end function
