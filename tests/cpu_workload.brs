sub Main()
    prefs=ReefValidateSettings(invalid)
    species=ParseJson(ReadAsciiFile("pkg:/scenes/species.json"))
    ' Freeze the original collision dimensions for the v26 trajectory oracle.
    ' Shipping art envelopes are exercised by the traffic/clearance tests.
    species.ocellaris_clownfish.collisionHalfWidth=85
    species.ocellaris_clownfish.collisionHalfHeight=41
    species.ocellaris_clownfish.bodyThickness=0.28
    species.yellow_tang.collisionHalfWidth=92
    species.yellow_tang.collisionHalfHeight=57
    species.yellow_tang.bodyThickness=0.2
    species.royal_gramma.collisionHalfWidth=88
    species.royal_gramma.collisionHalfHeight=40
    species.royal_gramma.bodyThickness=0.216
    species.emperor_angelfish.collisionHalfWidth=100
    species.emperor_angelfish.collisionHalfHeight=47
    species.emperor_angelfish.bodyThickness=0.216
    species.moorish_idol.collisionHalfWidth=97
    species.moorish_idol.collisionHalfHeight=58
    species.moorish_idol.bodyThickness=0.168
    species.green_chromis.collisionHalfWidth=91
    species.green_chromis.collisionHalfHeight=40
    species.green_chromis.bodyThickness=0.24
    species.blue_tang.collisionHalfWidth=113
    species.blue_tang.collisionHalfHeight=49
    species.blue_tang.bodyThickness=0.2
    species.copperband_butterflyfish.collisionHalfWidth=113
    species.copperband_butterflyfish.collisionHalfHeight=69
    species.copperband_butterflyfish.bodyThickness=0.17
    species.banggai_cardinalfish.collisionHalfWidth=113
    species.banggai_cardinalfish.collisionHalfHeight=73
    species.banggai_cardinalfish.bodyThickness=0.18
    species.mandarin_dragonet.collisionHalfWidth=113
    species.mandarin_dragonet.collisionHalfHeight=56
    species.mandarin_dragonet.bodyThickness=0.24
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
