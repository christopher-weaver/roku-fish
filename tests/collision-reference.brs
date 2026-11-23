' Collision oracle from v1.0.26; frozen to detect optimization changes.
function ReferenceReefCoralBlocked(s as object, f as object, fromPose as object, toPose as object) as boolean
    if ReefMin(fromPose.z,toPose.z)<.04 or ReefMax(fromPose.z,toPose.z)>.985 then return true
    if ReefMin(fromPose.x,toPose.x)<85# or ReefMax(fromPose.x,toPose.x)>1963# then return true
    if ReferenceReefSurfaceBlocked(s,f,fromPose,toPose) then return true
    if ReferenceReefFloorBlocked(s,f,fromPose,toPose) then return true
    if s.occupancy = invalid then return false
    if ReferenceReefCaveBlocked(s,f,fromPose,toPose) then return true
    planes = s.occupancy.planes
    if planes = invalid then return false
    radius = f.sp.bodyThickness * f.sp.length * f.size / 1728# + 0.012
    lo=ReefMin(fromPose.z,toPose.z)-radius : hi=ReefMax(fromPose.z,toPose.z)+radius
    for planeIndex = 0 to planes.Count() - 1
        plane = planes[planeIndex]
        if hi >= plane.z - plane.halfDepth and lo <= plane.z + plane.halfDepth
            s.collisionFirst=ReefProjection(fromPose,0#,s.collisionFirst)
            s.collisionLast=ReefProjection(toPose,0#,s.collisionLast)
            first=s.collisionFirst : last=s.collisionLast
            scale = ReefMax(first.scale, last.scale) * f.sp.length / f.sp.renderLength * f.size
            hw = (f.sp.collisionHalfWidth + f.sp.collisionHalfHeight * 0.22) * scale + 8
            hh = (f.sp.collisionHalfHeight + f.sp.collisionHalfWidth * 0.22) * scale + 8
            ' Reef coordinates are screen + camera, while fish have depth parallax.
            ' Reserve the whole camera sweep, so panning cannot push a fish into rock.
            parallax = 1#
            if plane.parallax <> invalid then parallax = plane.parallax
            firstPan = ReefMin(8 * (parallax - first.scale), 120 * (parallax - first.scale))
            lastPan = ReefMin(8 * (parallax - last.scale), 120 * (parallax - last.scale))
            x0 = ReefMin(first.x + firstPan, last.x + lastPan) + 64 * (1 - parallax) - hw
            firstPan = ReefMax(8 * (parallax - first.scale), 120 * (parallax - first.scale))
            lastPan = ReefMax(8 * (parallax - last.scale), 120 * (parallax - last.scale))
            x1 = ReefMax(first.x + firstPan, last.x + lastPan) + 64 * (1 - parallax) + hw
            y0 = ReefMin(first.y, last.y) + 36 - hh
            y1 = ReefMax(first.y, last.y) + 36 + hh
            if ReferenceReefSolidRect(plane.rows, s.occupancy.cell, x0, y0, x1, y1) then return true
        end if
    end for
    return false
end function

function ReferenceReefSolidRect(rows as object, cell as integer, x0 as double, y0 as double, x1 as double, y1 as double) as boolean
    top = Int(ReefClamp(Int(y0 / cell), 0, rows.Count() - 1))
    bottom = Int(ReefClamp(Int(y1 / cell), 0, rows.Count() - 1))
    left = Int(ReefClamp(Int(x0 / cell), 0, Len(rows[0]) - 1))
    right = Int(ReefClamp(Int(x1 / cell), 0, Len(rows[0]) - 1))
    if x1 < 0 or y1 < 0 or x0 >= Len(rows[0]) * cell or y0 >= rows.Count() * cell then return false
    for rowIndex = top to bottom
        found = Instr(left + 1, rows[rowIndex], "#")
        if found > 0 and found <= right + 1 then return true
    end for
    return false
end function

function ReferenceReefCaveBlocked(s as object,f as object,a as object,b as object) as boolean
    if s.occupancy.volumes=invalid then return false
    scale=(.70+.30*ReefMax(a.z,b.z))*f.sp.length/f.sp.renderLength*f.size
    hw=(f.sp.collisionHalfWidth+f.sp.collisionHalfHeight*.22)*scale+26#
    hh=(f.sp.collisionHalfHeight+f.sp.collisionHalfWidth*.22)*scale+12#
    depth=f.sp.bodyThickness*f.sp.length*f.size/1728#+.012
    for volumeIndex=0 to s.occupancy.volumes.Count()-1
        v=s.occupancy.volumes[volumeIndex]
        possible=ReefMax(a.z,b.z)+depth>=v.z-v.halfDepth and ReefMin(a.z,b.z)-depth<=v.z+v.halfDepth
        possible=possible and ReefMax(a.x,b.x)+hw>=v.x-v.halfWidth and ReefMin(a.x,b.x)-hw<=v.x+v.halfWidth
        possible=possible and ReefMax(a.y,b.y)+hh>=v.y-v.halfHeight and ReefMin(a.y,b.y)-hh<=v.y+v.halfHeight
        if possible
            enter=0# : leave=1# : hit=true
            for axis=0 to 2
                start=a.x : delta=b.x-a.x : low=v.x-v.halfWidth-hw : high=v.x+v.halfWidth+hw
                if axis=1 then start=a.y : delta=b.y-a.y : low=v.y-v.halfHeight-hh : high=v.y+v.halfHeight+hh
                if axis=2 then start=a.z : delta=b.z-a.z : low=v.z-v.halfDepth-depth : high=v.z+v.halfDepth+depth
                if Abs(delta)<.0000001
                    if start<low or start>high then hit=false
                else
                    t0=(low-start)/delta : t1=(high-start)/delta
                    enter=ReefMax(enter,ReefMin(t0,t1))
                    leave=ReefMin(leave,ReefMax(t0,t1))
                end if
            end for
            if hit and enter<=leave then return true
        end if
    end for
    return false
end function

function ReferenceReefFloorBlocked(s as object,f as object,a as object,b as object) as boolean
    if s.cfg=invalid then return false
    floor=s.cfg.floor
    if floor=invalid then return false
    scale=(.70+.30*ReefMax(a.z,b.z))*f.sp.length/f.sp.renderLength*f.size
    hh=(f.sp.collisionHalfHeight+f.sp.collisionHalfWidth*.22)*scale+12#
    radius=f.sp.bodyThickness*f.sp.length*f.size/1728#+.012
    firstCeiling=floor.baseY+floor.slope*(a.z-radius)-floor.ridgeClearance-hh
    lastCeiling=floor.baseY+floor.slope*(b.z-radius)-floor.ridgeClearance-hh
    return a.y>firstCeiling or b.y>lastCeiling
end function

function ReferenceReefSurfaceBlocked(s as object,f as object,a as object,b as object) as boolean
    if s.cfg=invalid then return false
    if s.cfg.waterline=invalid then return false
    scale=(.70+.30*ReefMax(a.z,b.z))*f.sp.length/f.sp.renderLength*f.size
    hh=(f.sp.collisionHalfHeight+f.sp.collisionHalfWidth*.22)*scale+12#
    firstTop=a.y+(1#-a.z)*30#-hh
    lastTop=b.y+(1#-b.z)*30#-hh
    return ReefMin(firstTop,lastTop)<s.cfg.waterline.clearanceY
end function

function ReferenceReefFishRadius(f as object) as double
    size=1#
    if f.size<>invalid then size=f.size
    width=f.sp.length*.52*size : height=f.sp.length*.3*size
    if f.sp.collisionHalfWidth<>invalid and f.sp.renderLength<>invalid
        width=f.sp.collisionHalfWidth*f.sp.length/f.sp.renderLength*size
        height=f.sp.collisionHalfHeight*f.sp.length/f.sp.renderLength*size
    end if
    return width+height*.22+6#
end function

function ReferenceReefFishHeight(f as object) as double
    size=1#
    if f.size<>invalid then size=f.size
    width=f.sp.length*.52*size : height=f.sp.length*.3*size
    if f.sp.collisionHalfHeight<>invalid and f.sp.renderLength<>invalid
        height=f.sp.collisionHalfHeight*f.sp.length/f.sp.renderLength*size
        width=f.sp.collisionHalfWidth*f.sp.length/f.sp.renderLength*size
    end if
    return height+width*.22+6#
end function

function ReferenceReefFishPairBlocked(f as object, fromPose as object, toPose as object, other as object, swept = true as boolean) as boolean
    ox=other.x : oy=other.y : oz=other.z
    if swept and other.previousX<>invalid then ox=other.previousX : oy=other.previousY : oz=other.previousZ
    px=fromPose.x-ox : py=fromPose.y-oy : pz=(fromPose.z-oz)*800#
    vx=toPose.x-other.x-px : vy=toPose.y-other.y-py : vz=(toPose.z-other.z)*800#-pz
    radius=ReferenceReefFishRadius(f)+ReferenceReefFishRadius(other)+4#
    height=ReferenceReefFishHeight(f)+ReferenceReefFishHeight(other)+4#
    low=0# : high=1#
    if Abs(vy)<0.0000001
        if Abs(py)>=height then return false
    else
        a=(0#-height-py)/vy : b=(height-py)/vy
        low=ReefMax(0#,ReefMin(a,b)) : high=ReefMin(1#,ReefMax(a,b))
        if low>high then return false
    end if
    speed=vx*vx+vz*vz : t=low
    if speed>0.0000001 then t=ReefClamp(-(px*vx+pz*vz)/speed,low,high)
    dx=px+vx*t : dz=pz+vz*t
    return dx*dx+dz*dz<radius*radius
end function
