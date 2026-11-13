' Host adapter only. Persistence logic stays in source/settings-model.brs.
function ReefTestRegistry(section as string) as object
    global=GetGlobalAA()
    if global.testRegistry=invalid
        global.testRegistry={values:{},Exists:TestRegExists,Read:TestRegRead,Write:TestRegWrite,Flush:TestRegFlush}
    end if
    return global.testRegistry
end function
function TestRegExists(key as string) as boolean
    return m.values.DoesExist(key)
end function
function TestRegRead(key as string) as string
    return m.values[key]
end function
function TestRegWrite(key as string,value as string) as boolean
    m.values[key]=value
    return true
end function
function TestRegFlush() as boolean
    return true
end function
