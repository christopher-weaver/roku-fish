sub Main()
    prefs=ReefValidateSettings(invalid)
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    ' Freeze the original collision dimensions for the v26 trajectory oracle.
    ' Shipping art envelopes are exercised by the traffic/clearance tests.
    species.emperor_angelfish.collisionHalfWidth=99
    species.moorish_idol.collisionHalfWidth=96
    species.green_chromis.collisionHalfWidth=89
    occ=ParseJson(ReadAsciiFile("pkg:/scenes/occupancy.json"))
    s=ReefWorld(prefs,species,occ,47831)
    s.clam.enabled=false
    ReefCPUWindow(s)
end sub

' Fixed two-second window; profiling excludes initialization and texture loading.
sub ReefCPUWindow(s as object)
    for tick=0 to 59
        ReefAdvance(s,1#/30#)
    end for
    expected=[
        [1763.643075944195#,275.9427628473404#,0.1642409821773539#,3.199198083823473#],
        [1632.938427913046#,672.6074795144494#,0.945496557224772#,3.003578053369369#],
        [1745.356609359923#,443.4554313318832#,0.2828282355323715#,3.013493783388471#],
        [1034.286642200057#,180.3689984794417#,0.1173416197386904#,6.192883743481911#],
        [1330.575791510389#,439.8770930371553#,0.944082822319013#,3.118043789477667#],
        [668.0237336820721#,529.2698767789697#,0.9323289016984987#,6.227064632444356#],
        [180.4511908704008#,206.6160062762126#,0.3944468663515426#,6.274418698693391#],
        [837.9251479242363#,391.6031222891091#,0.5549998530177621#,6.256204076634296#]
    ]
    if s.fish.Count()<>8 then print "FAIL CPU fixture fish count" : return
    for i=0 to s.fish.Count()-1
        f=s.fish[i] : e=expected[i]
        if Abs(f.x-e[0])+Abs(f.y-e[1])+Abs(f.z-e[2])+Abs(f.heading-e[3])>.0000001 then print "FAIL changed reference trajectory ";i : return
    end for
    print "PASS CPU workload: 60 fixed ticks, 8 fish retain v26 reference trajectories"
end sub
