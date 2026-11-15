sub Main()
    for each y in [300#,700#,970#,1150#]
        depth=(y+180#)/1332# : cell=240#*depth
        for x=200 to 1800 step 200
            a=ReefSurfaceShade(x,y,.123) : b=ReefSurfaceShade(x,y,8.123)
            if Abs(a-b)>.0001 then print "FAIL shadow cycle seam" : return
            c=ReefSurfaceShade(x+cell,y,.123)
            if Abs(a-c)>.0001 then print "FAIL projector period" : return
            previous=a
            for tick=1 to 120
                value=ReefSurfaceShade(x,y,.123+tick/60#)
                if value<.76 or value>1.0001 then print "FAIL shadow strength" : return
                if Abs(value-previous)>.02 then print "FAIL shadow time jump" : return
                previous=value
            end for
        end for
    end for
    print "PASS soft projected object lighting: bounded intensity, continuous time, periodic sampling and depth-scaled cells"
end sub
