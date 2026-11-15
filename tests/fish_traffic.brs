sub Main()
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    occ=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    for each seed in [1,91,47831,1900000001]
        world=ReefWorld(ReefValidateSettings({density:"High"}),species,occ,seed)
        if world.fish.Count()<>10 then print "FAIL high density roster" : return
        for i=0 to world.fish.Count()-1
            f=world.fish[i]
            if ReefFishBlocked(world,f,f,f,false) then print "FAIL overlapping spawn ";seed;" fish ";i : return
        end for
    end for
    print "PASS ten differently sized fish spawn without fish-to-fish overlap across four seeds"
    for scenario=0 to 3
        world=ReefWorld(ReefValidateSettings({density:"Low"}),species,invalid,91)
        while world.fish.Count()>2
            world.fish.Pop()
        end while
        world.occupancy=invalid : world.navigation=invalid
        a=world.fish[0] : b=world.fish[1]
        a.sp=species.emperor_angelfish : b.sp=species.yellow_tang
        a.size=1# : b.size=1#
        for i=0 to 1
            f=world.fish[i] : f.route=[] : f.duration=1000# : f.state="Cruising"
            f.x=500#+i*900# : f.y=350# : f.z=0.5
            f.heading=i*3.141592654# : f.yawVelocity=0# : f.yawAcceleration=0#
            f.speed=f.sp.speed : f.speedAcceleration=0#
            f.vx=Cos(f.heading)*f.speed : f.vy=0# : f.vz=0#
            f.tx=1800#-i*1500# : f.ty=350# : f.tz=0.5
        end for
        if scenario=1
            a.x=900# : b.x=900# : a.z=0.12 : b.z=0.94
            a.heading=1.570796327# : b.heading=4.71238898#
            a.tx=900# : b.tx=900# : a.tz=0.94 : b.tz=0.12
        end if
        if scenario=2
            a.sp=species.green_chromis : b.sp=species.royal_gramma
            a.x=600# : b.x=950# : a.heading=0# : b.heading=0#
            a.tx=1850# : b.tx=1850#
        end if
        if scenario=3
            a.x=650# : b.x=1100# : a.z=0.5 : b.z=0.12
            a.heading=0# : b.heading=1.570796327#
            a.tx=1850# : b.tx=1100# : b.tz=0.94
        end if
        for i=0 to 1
            f=world.fish[i] : f.vx=Cos(f.heading)*f.speed : f.vz=Sin(f.heading)*f.speed/800#
            ReefSavePose(f)
        end for
        startA={x:a.x,y:a.y,z:a.z} : startB={x:b.x,y:b.y,z:b.z}
        for tick=0 to 359
            ReefAdvance(world,1#/30#)
            if ReefFishPairBlocked(a,{x:a.previousX,y:a.previousY,z:a.previousZ},a,b) then print "FAIL swept fish contact ";scenario;" tick ";tick : return
            for sample=0 to 4
                pose=ReefDisplayPose(a,sample/4#) : otherPose=ReefDisplayPose(b,sample/4#)
                other={id:b.id,sp:b.sp,size:b.size,x:otherPose.x,y:otherPose.y,z:otherPose.z}
                if ReefFishPairBlocked(a,pose,pose,other,false) then print "FAIL displayed fish contact ";scenario;" tick ";tick : return
            end for
        end for
        progressA=Sqr((a.x-startA.x)^2+(a.y-startA.y)^2+((a.z-startA.z)*800)^2)
        progressB=Sqr((b.x-startB.x)^2+(b.y-startB.y)^2+((b.z-startB.z)*800)^2)
        if progressA<30 or progressB<30 then print "FAIL traffic deadlock ";scenario : return
        print "PASS swept and interpolated body/tail/fin clearance, encounter ";scenario;" progress ";progressA;progressB
    end for
    ' A large displacement must still detect an intervening body.
    a=world.fish[0] : b=world.fish[1]
    b.x=1000# : b.y=350# : b.z=0.5
    if not ReefFishPairBlocked(a,{x:100#,y:350#,z:0.5},{x:1800#,y:350#,z:0.5},b,false) then print "FAIL fish tunneling" : return
    print "PASS swept guard prevents tunneling across another fish"
end sub
