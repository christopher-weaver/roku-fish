' Conservative yaw-independent body/tail/fin envelopes in world coordinates.
' These cylinders also remain safe during rotation and display interpolation.
function ReefFishBounds(f as object) as object
    bounds=f.bodyBounds
    if bounds<>invalid
        if bounds.sizeKey=f.size and bounds.species=f.sp.image then return bounds
    end if
    size=1#
    if f.size<>invalid then size=f.size
    width=f.sp.length*.52*size : height=f.sp.length*.3*size
    if f.sp.collisionHalfWidth<>invalid and f.sp.renderLength<>invalid
        width=f.sp.collisionHalfWidth*f.sp.length/f.sp.renderLength*size
        height=f.sp.collisionHalfHeight*f.sp.length/f.sp.renderLength*size
    end if
    ' Assign a fresh object: a clam baby initially shallow-copies its parent.
    bounds={sizeKey:f.size,species:f.sp.image,radius:width+height*.22+6#,height:height+width*.22+6#}
    if f.sp.renderLength<>invalid and f.sp.collisionHalfWidth<>invalid
        ratio=f.sp.length*1#/f.sp.renderLength*size
        bounds.coralWidth=(f.sp.collisionHalfWidth+f.sp.collisionHalfHeight*.22)*ratio
        bounds.coralHeight=(f.sp.collisionHalfHeight+f.sp.collisionHalfWidth*.22)*ratio
        bounds.depthRadius=f.sp.bodyThickness*f.sp.length*size/1728#+.012
    end if
    f.bodyBounds=bounds
    return bounds
end function

function ReefFishRadius(f as object) as double
    bounds=ReefFishBounds(f)
    return bounds.radius
end function

function ReefFishHeight(f as object) as double
    bounds=ReefFishBounds(f)
    return bounds.height
end function

' Continuous swept cylinder test: a crossing cannot tunnel between fixed ticks.
function ReefFishPairBlocked(f as object, fromPose as object, toPose as object, other as object, swept = true as boolean, knownBounds=false as boolean) as boolean
    ox=other.x : oy=other.y : oz=other.z
    if swept and other.previousX<>invalid then ox=other.previousX : oy=other.previousY : oz=other.previousZ
    px=fromPose.x-ox : py=fromPose.y-oy : pz=(fromPose.z-oz)*800#
    vx=toPose.x-other.x-px : vy=toPose.y-other.y-py : vz=(toPose.z-other.z)*800#-pz
    own=f.bodyBounds : neighbor=other.bodyBounds
    if not knownBounds
        own=f.bodyBounds
        if own=invalid
            own=ReefFishBounds(f)
        else if own.sizeKey<>f.size or own.species<>f.sp.image
            own=ReefFishBounds(f)
        end if
        neighbor=other.bodyBounds
        if neighbor=invalid
            neighbor=ReefFishBounds(other)
        else if neighbor.sizeKey<>other.size or neighbor.species<>other.sp.image
            neighbor=ReefFishBounds(other)
        end if
    end if
    radius=own.radius+neighbor.radius+4# : height=own.height+neighbor.height+4#
    ' Keep accepted movement clear of the static boundary despite floating-point
    ' contact drift. This is 1/100 of a design pixel, below display precision.
    if swept then radius=radius+.01 : height=height+.01
    ' Exact broad phase: a linear relative sweep wholly outside a slab cannot hit.
    if px>=radius and px+vx>=radius then return false
    if px<=0#-radius and px+vx<=0#-radius then return false
    if pz>=radius and pz+vz>=radius then return false
    if pz<=0#-radius and pz+vz<=0#-radius then return false
    low=0# : high=1#
    if Abs(vy)<0.0000001
        if Abs(py)>=height then return false
    else
        a=(0#-height-py)/vy : b=(height-py)/vy
        if a>b then swap=a : a=b : b=swap
        if a>low then low=a
        if b<high then high=b
        if low>high then return false
    end if
    speed=vx*vx+vz*vz : t=low
    if speed>0.0000001
        t=0#-(px*vx+pz*vz)/speed
        if t<low then t=low
        if t>high then t=high
    end if
    dx=px+vx*t : dz=pz+vz*t
    return dx*dx+dz*dz<radius*radius
end function

function ReefFishBlocked(s as object, f as object, fromPose as object, toPose as object, swept = true as boolean) as boolean
    ready=s.physicsBoundsReady=true : own=f.bodyBounds
    if not ready then own=ReefFishBounds(f)
    for neighborIndex=0 to s.fish.Count()-1
        other=s.fish[neighborIndex]
        if other.id<>f.id
            neighbor=other.bodyBounds
            if not ready then neighbor=ReefFishBounds(other)
            radius=own.radius+neighbor.radius+4.000001#
            if swept then radius=radius+.01
            ox=other.x : oz=other.z
            if swept and other.previousX<>invalid then ox=other.previousX : oz=other.previousZ
            start=fromPose.x-ox : finish=toPose.x-other.x
            far=(start>=radius and finish>=radius) or (start<=0#-radius and finish<=0#-radius)
            if not far
                start=(fromPose.z-oz)*800# : finish=(toPose.z-other.z)*800#
                far=(start>=radius and finish>=radius) or (start<=0#-radius and finish<=0#-radius)
            end if
            ' Exact sweep slabs reject distant pairs before calling the full
            ' cylinder test. Both endpoints include the other fish's movement.
            if not far
                if ReefFishPairBlocked(f,fromPose,toPose,other,swept,true) then return true
            end if
        end if
    end for
    return false
end function

function ReefFishSafeSpawn(s as object, f as object) as boolean
    if not ReefFishBlocked(s,f,f,f,true) then return true
    best=1e20 : chosen=invalid
    if s.navigation<>invalid
        for nodeIndex=0 to s.navigation.nodes.Count()-1
            node=s.navigation.nodes[nodeIndex]
            distance=(node.x-f.x)^2+(node.y-f.y)^2+((node.z-f.z)*800)^2
            if distance<best
                if not ReefFishBlocked(s,f,node,node,true) and not ReefCoralBlocked(s,f,node,node) then best=distance : chosen=node
            end if
        end for
    end if
    if chosen=invalid
        for attempt=0 to 63
            sample={x:ReefRange(s,160,1880),y:ReefRange(s,110,790),z:ReefRange(s,.12,.94)}
            if not ReefFishBlocked(s,f,sample,sample,true) and not ReefCoralBlocked(s,f,sample,sample) then chosen=sample : exit for
        end for
    end if
    if chosen=invalid then return false
    f.x=chosen.x : f.y=chosen.y : f.z=chosen.z
    return true
end function

' Predictive separation for every species; alignment/cohesion only for chromis.
function ReefNeighbors(s as object, f as object) as object
    steer=f.neighborSteer
    if steer=invalid then steer={} : f.neighborSteer=steer
    steer.x=0# : steer.y=0# : steer.z=0# : steer.hx=0# : steer.hz=0#
    steer.cx=0# : steer.cy=0# : steer.cz=0# : steer.count=0 : steer.alarm=false : steer.traffic=0#
    ready=s.physicsBoundsReady=true : own=f.bodyBounds
    if not ready then own=ReefFishBounds(f)
    for neighborIndex=0 to s.fish.Count()-1
        other=s.fish[neighborIndex]
        if other.id<>f.id
            dx=f.x-other.x : dy=f.y-other.y : dz=(f.z-other.z)*800#
            neighbor=other.bodyBounds
            if not ready
                if neighbor=invalid
                    neighbor=ReefFishBounds(other)
                else if neighbor.sizeKey<>other.size or neighbor.species<>other.sp.image
                    neighbor=ReefFishBounds(other)
                end if
            end if
            radius=own.radius+neighbor.radius+4#
            height=own.height+neighbor.height+4#
            vx=0# : vy=0# : vz=0#
            if f.vx<>invalid and other.vx<>invalid then vx=f.vx-other.vx : vy=f.vy-other.vy : vz=(f.vz-other.vz)*800#
            speed=vx*vx+vz*vz : ahead=0#
            if speed>.001
                ahead=0#-(dx*vx+dz*vz)/speed
                if ahead<0# then ahead=0#
                if ahead>6# then ahead=6#
            end if
            cx=dx+vx*ahead : cz=dz+vz*ahead : cy=dy+vy*ahead
            closestSquared=cx*cx+cz*cz : reach=radius*1.65
            if closestSquared<reach*reach and Abs(cy)<height*1.25
                closest=Sqr(closestSquared)
                pressure=ReefClamp((radius*1.65-closest)/(radius*.65),0,1)
                pressure=pressure*(1-ahead/9#)
                steer.traffic=ReefMax(steer.traffic,pressure)
                ' Stable passing lanes prevent symmetric head-on deadlock.
                side=-1#
                if f.id>other.id then side=1#
                if Abs(dy)>height*.3
                    side=1#
                    if dy<0 then side=-1#
                end if
                if f.trafficProbe=invalid then f.trafficProbe={}
                lane=f.trafficProbe
                lane.x=f.x : lane.y=f.y+side*(height+24#) : lane.z=f.z
                blockedPreferred=ReefCoralBlocked(s,f,f,lane)
                if blockedPreferred
                    lane.y=f.y-side*(height+24#)
                    if Abs(dy)<=height*.3 and not ReefCoralBlocked(s,f,f,lane)
                        side=0#-side
                    else
                        ' Never undo useful separation by steering back toward
                        ' the other fish when the floor blocks the outward lane.
                        side=0#
                    end if
                end if
                if f.id<other.id and Abs(dy)<=height*.3
                    lane.x=other.x : lane.y=other.y+height+24# : lane.z=other.z
                    if blockedPreferred or ReefCoralBlocked(s,other,other,lane) then side=0#
                end if
                steer.y=steer.y+side*pressure*520#
                lane.x=f.x : lane.y=f.y : lane.z=ReefClamp(f.z+side*.10,.06,.97)
                if not ReefCoralBlocked(s,f,f,lane) then steer.z=steer.z+side*pressure*90#
                horizontal=Sqr(dx*dx+dz*dz)
                if horizontal>0.001
                    repel=pressure*ReefClamp((radius*1.25-horizontal)/(radius*.35),0,1)*100#
                    steer.x=steer.x+dx/horizontal*repel
                    steer.z=steer.z+dz/horizontal*repel
                end if
                if other.sp.length>160 and f.schooling then steer.alarm=true
            end if
            distance=dx*dx+dy*dy+dz*dz
            if f.schooling and other.schooling and distance<160000
                steer.cx=steer.cx+other.x : steer.cy=steer.cy+other.y : steer.cz=steer.cz+other.z
                steer.hx=steer.hx+Cos(other.heading) : steer.hz=steer.hz+Sin(other.heading)
                steer.count=steer.count+1
            end if
        end if
    end for
    if steer.count>0
        steer.x=steer.x+(steer.cx/steer.count-f.x)*.12+steer.hx/steer.count*16
        steer.y=steer.y+(steer.cy/steer.count-f.y)*.14
        steer.z=steer.z+(steer.cz/steer.count-f.z)*90+steer.hz/steer.count*14
    end if
    return steer
end function
