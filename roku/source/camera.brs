' Coordinates are 1920x1080 design pixels. z=0 rear wall, z=1 front glass.
function ReefCamera(t as double, mode as string, config = invalid as dynamic) as double
    if mode = "Off" then return 64#
    amplitude = 40# : period = 180#
    if mode = "Slow" then amplitude = 56# : period = 240#
    if config <> invalid and config[mode] <> invalid
        amplitude = config[mode].amplitude : period = config[mode].period
    end if
    return 64# - amplitude * Cos(ReefWrap(t, period) * 6.283185307 / period)
end function

function ReefDisplayPose(f as object, alpha as double, pose = invalid as dynamic) as object
    if pose=invalid then pose={}
    pose.x=f.previousX+(f.x-f.previousX)*alpha
    pose.y=f.previousY+(f.y-f.previousY)*alpha
    pose.z=f.previousZ+(f.z-f.previousZ)*alpha
    if f.previousVx<>invalid and f.emerging<>true
        pose.x=ReefSmoothPosition(f.previousX,f.x,f.previousVx,f.vx,alpha)
        pose.y=ReefSmoothPosition(f.previousY,f.y,f.previousVy,f.vy,alpha)
        pose.z=ReefSmoothPosition(f.previousZ,f.z,f.previousVz,f.vz,alpha)
    end if
    delta = ReefAngleDelta(f.previousHeading, f.heading)
    ' Cubic heading interpolation keeps angular velocity continuous at 30Hz ticks.
    a2 = alpha * alpha : a3 = a2 * alpha
    pose.heading = f.previousHeading + delta * (3*a2-2*a3)
    pose.heading = pose.heading + (a3-2*a2+alpha) * f.previousYawVelocity / 30# + (a3-a2) * f.yawVelocity / 30#
    pose.yawVelocity=f.previousYawVelocity+(f.yawVelocity-f.previousYawVelocity)*alpha
    pose.pitch = f.previousPitch + (f.pitch - f.previousPitch) * alpha
    pose.phase = f.previousPhase + ReefAngleDelta(f.previousPhase, f.phase) * alpha
    pose.finPhase = f.previousFinPhase + ReefAngleDelta(f.previousFinPhase, f.finPhase) * alpha
    return pose
end function

function ReefProjection(f as object, camera as double, result = invalid as dynamic) as object
    scale = 0.70 + 0.30 * f.z
    if result=invalid then result={}
    result.x=f.x-camera*scale : result.y=f.y+(1-f.z)*30 : result.scale=scale
    return result
end function

function ReefSolid(s as object, x as double, y as double) as boolean
    if s.occupancy = invalid then return false
    col = Int(x / s.occupancy.cell)
    row = Int((y + 36) / s.occupancy.cell)
    if row < 0 or row >= s.occupancy.rows.Count() then return false
    line = s.occupancy.rows[row]
    if col < 0 or col >= Len(line) then return false
    return Mid(line, col + 1, 1) = "#"
end function

 ' Load the immutable row unions once; custom/test grids retain the exact fallback.
sub ReefCollisionInit(s as object)
    if s.occupancy=invalid then return
    if s.occupancy.planes=invalid then return
    table=ParseJson(ReadAsciiFile("pkg:/scenes/collision-index.json"))
    if table=invalid then return
    if table.cell<>s.occupancy.cell or table.planes.Count()<>s.occupancy.planes.Count() then return
    for i=0 to table.planes.Count()-1
        plane=s.occupancy.planes[i] : entry=table.planes[i]
        plane.rowIndex=invalid
        matches=entry.id=plane.id and entry.levels[0].Count()=plane.rows.Count()
        if matches
            for row=0 to plane.rows.Count()-1
                if table.masks[entry.levels[0][row]]<>plane.rows[row] then matches=false : exit for
            end for
        end if
        if matches then plane.rowIndex={masks:table.masks,levels:entry.levels,levelByHeight:table.levelByHeight,spanByHeight:table.spanByHeight}
    end for
end sub

' Fish footprints include every yaw, tail and fin pose plus the maximum pitch.
' Test the swept rectangle, not just the center at a depth-plane crossing.
function ReefCoralBlocked(s as object, f as object, fromPose as object, toPose as object) as boolean
    ' Compute the swept extents once. This is the hottest simulation path.
    z0=fromPose.z : z1=toPose.z
    if z0>z1 then swap=z0 : z0=z1 : z1=swap
    x0=fromPose.x : x1=toPose.x
    if x0>x1 then swap=x0 : x0=x1 : x1=swap
    if z0<.04 or z1>.985 or x0<85# or x1>1963# then return true
    bounds=f.bodyBounds
    if s.physicsBoundsReady<>true
        ' Geometry-free schooling queries need no texture/anatomy metadata.
        if s.cfg=invalid and s.occupancy=invalid then return false
        bounds=ReefFishBounds(f)
    end if
    depthScale=.70+.30*z1
    ' Constant anatomy is validated once per physics tick, including baby sizes.
    hw=bounds.coralWidth*depthScale+.000000001#
    hh=bounds.coralHeight*depthScale+.000000001#
    radius=bounds.depthRadius
    clearanceHeight=hh+12#
    if s.cfg<>invalid
        if s.cfg.waterline<>invalid
            top=fromPose.y+(1#-fromPose.z)*30#-clearanceHeight
            if top<s.cfg.waterline.clearanceY then return true
            top=toPose.y+(1#-toPose.z)*30#-clearanceHeight
            if top<s.cfg.waterline.clearanceY then return true
        end if
        if s.cfg.floor<>invalid
            floor=s.cfg.floor
            ceiling=floor.baseY+floor.slope*(fromPose.z-radius)-floor.ridgeClearance-clearanceHeight
            if fromPose.y>ceiling then return true
            ceiling=floor.baseY+floor.slope*(toPose.z-radius)-floor.ridgeClearance-clearanceHeight
            if toPose.y>ceiling then return true
        end if
    end if
    if s.occupancy=invalid then return false
    y0=fromPose.y : y1=toPose.y
    if y0>y1 then swap=y0 : y0=y1 : y1=swap
    lo=z0-radius : hi=z1+radius
    volumes=s.occupancy.volumes
    if volumes<>invalid
        for volumeIndex=0 to volumes.Count()-1
            v=volumes[volumeIndex]
            ' Reject distant caves before running the exact segment/slab test.
            if hi>=v.z-v.halfDepth and lo<=v.z+v.halfDepth
                if x1+hw+26#>=v.x-v.halfWidth and x0-hw-26#<=v.x+v.halfWidth
                    if y1+hh+12#>=v.y-v.halfHeight and y0-hh-12#<=v.y+v.halfHeight
                        if ReefCaveBlocked(s,f,fromPose,toPose) then return true
                    end if
                end if
            end if
        end for
    end if
    planes=s.occupancy.planes
    if planes=invalid then return false
    ' Projection and the common parallax rectangle are shared by all planes.
    firstScale=.70+.30*fromPose.z : lastScale=.70+.30*toPose.z
    firstY=fromPose.y+(1#-fromPose.z)*30#
    lastY=toPose.y+(1#-toPose.z)*30#
    y0=firstY : y1=lastY
    if y0>y1 then swap=y0 : y0=y1 : y1=swap
    y0=y0+36#-(hh+8#) : y1=y1+36#+(hh+8#)
    planeWidth=hw+8#
    previousParallax=-999#
    for planeIndex=0 to planes.Count()-1
        plane=planes[planeIndex]
        if hi>=plane.z-plane.halfDepth and lo<=plane.z+plane.halfDepth
            parallax=1#
            if plane.parallax<>invalid then parallax=plane.parallax
            if parallax<>previousParallax
                firstPan=8#*(parallax-firstScale) : lastPan=8#*(parallax-lastScale)
                if parallax<firstScale then firstPan=120#*(parallax-firstScale)
                if parallax<lastScale then lastPan=120#*(parallax-lastScale)
                x0=fromPose.x+firstPan : value=toPose.x+lastPan
                if value<x0 then x0=value
                firstPan=120#*(parallax-firstScale) : lastPan=120#*(parallax-lastScale)
                if parallax<firstScale then firstPan=8#*(parallax-firstScale)
                if parallax<lastScale then lastPan=8#*(parallax-lastScale)
                x1=fromPose.x+firstPan : value=toPose.x+lastPan
                if value>x1 then x1=value
                x0=x0+64#*(1#-parallax)-planeWidth
                x1=x1+64#*(1#-parallax)+planeWidth
                previousParallax=parallax
            end if
            if ReefSolidRect(plane.rows,s.occupancy.cell,x0,y0,x1,y1,plane.rowIndex) then return true
        end if
    end for
    return false
end function

function ReefSolidRect(rows as object, cell as integer, x0 as double, y0 as double, x1 as double, y1 as double, index=invalid as dynamic) as boolean
    width=Len(rows[0]) : height=rows.Count()
    if x1<0 or y1<0 or x0>=width*cell or y0>=height*cell then return false
    top=Int(y0/cell) : bottom=Int(y1/cell)
    left=Int(x0/cell) : right=Int(x1/cell)
    if top<0 then top=0
    if bottom>=height then bottom=height-1
    if left<0 then left=0
    if right>=width then right=width-1
    if index<>invalid
        ' Immutable occupancy grids: small exact cell rectangles repeat as fish
        ' move less than one grid cell. Bounded direct-mapped memoization keeps
        ' every swept query, while avoiding repeated native string searches.
        cacheable=width<=256 and height<=144
        if cacheable
            if index.cacheKeys=invalid
                index.cacheKeys=[] : index.cacheValues=[]
                for slot=0 to 63
                    index.cacheKeys.Push(-1) : index.cacheValues.Push(false)
                end for
            end if
            key=((top*height+bottom)*width+left)*width+right
            slot=(top*3+bottom*5+left*7+right*11) mod 64
            if index.cacheKeys[slot]=key then return index.cacheValues[slot]
        end if
        height=bottom-top+1 : level=index.levelByHeight[height]
        bands=index.levels[level] : masks=index.masks
        found=Instr(left+1,masks[bands[top]],"#")
        if found>0 and found<=right+1
            if cacheable then index.cacheKeys[slot]=key : index.cacheValues[slot]=true
            return true
        end if
        last=bottom-index.spanByHeight[height]+1
        if last<>top
            found=Instr(left+1,masks[bands[last]],"#")
            if found>0 and found<=right+1
                if cacheable then index.cacheKeys[slot]=key : index.cacheValues[slot]=true
                return true
            end if
        end if
        if cacheable then index.cacheKeys[slot]=key : index.cacheValues[slot]=false
        return false
    end if
    for rowIndex = top to bottom
        found = Instr(left + 1, rows[rowIndex], "#")
        if found > 0 and found <= right + 1 then return true
    end for
    return false
end function

sub ReefSafeSpawn(s as object, f as object)
    if not ReefCoralBlocked(s, f, f, f) then return
    original = f.z : best = 10# : chosen = 0.3
    for each lane in [0.12, 0.94]
        candidate = {x:f.x, y:f.y, z:lane}
        distance = Abs(lane - original)
        if distance < best and not ReefCoralBlocked(s, f, candidate, candidate)
            chosen = lane : best = distance
        end if
    end for
    ' A deeply emerged eel can occupy both usual depth lanes. Relocate a
    ' blocked initial spawn to the nearest pre-cleared navigation node.
    if best=10# and s.navigation<>invalid
        selected=invalid : nearest=1e20
        for nodeIndex=0 to s.navigation.nodes.Count()-1
            node=s.navigation.nodes[nodeIndex]
            distance=(node.x-f.x)^2+(node.y-f.y)^2+((node.z-f.z)*800#)^2
            if distance<nearest and not ReefCoralBlocked(s,f,node,node)
                selected=node : nearest=distance
            end if
        end for
        if selected<>invalid
            f.x=selected.x : f.y=selected.y : f.z=selected.z
            return
        end if
    end if
    f.z = chosen
end sub

' A swept body against the cave's solid reserved volume. The resident moray is
' not in s.fish; spawning, planning and final free-swimmer guards all use this.
function ReefCaveBlocked(s as object,f as object,a as object,b as object) as boolean
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

' The fish's whole pitched body must remain above the ridged 3D floor.
' A linear floor plane and a swept maximum body envelope need both endpoints.
function ReefFloorBlocked(s as object,f as object,a as object,b as object) as boolean
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

' Bound every posed fish below the thin surface layer, including pitched fins.
function ReefSurfaceBlocked(s as object,f as object,a as object,b as object) as boolean
    if s.cfg=invalid then return false
    if s.cfg.waterline=invalid then return false
    scale=(.70+.30*ReefMax(a.z,b.z))*f.sp.length/f.sp.renderLength*f.size
    hh=(f.sp.collisionHalfHeight+f.sp.collisionHalfWidth*.22)*scale+12#
    firstTop=a.y+(1#-a.z)*30#-hh
    lastTop=b.y+(1#-b.z)*30#-hh
    return ReefMin(firstTop,lastTop)<s.cfg.waterline.clearanceY
end function
