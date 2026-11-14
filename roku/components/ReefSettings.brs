sub init()
    m.schema = ReefSettingsSchema()
    ' All menu coordinates use FHD design units; keep every row/value on HD screens.
    resolution = m.top.currentDesignResolution
    if resolution <> invalid
        layout = m.top.FindNode("layout")
        layout.scale = [resolution.width / 1920.0, resolution.height / 1080.0]
    end if
    m.index = 0
    m.rows = m.top.FindNode("rows")
    m.highlight = m.top.FindNode("highlight")
    m.labels = [] : m.values = []
    for i = 0 to 10
        m.labels.Push(m.top.FindNode("label" + i.ToStr()))
        m.values.Push(m.top.FindNode("value" + i.ToStr()))
    end for
    refreshRows()
    m.top.SetFocus(true)
end sub

sub refreshRows()
    if m.schema = invalid then return
    prefs = ReefValidateSettings(m.top.preferences)
    for i = 0 to 8
        row = m.schema[i]
        m.labels[i].text = row.label
        m.values[i].text = "‹  " + prefs[row.id] + "  ›"
    end for
    m.labels[9].text = "Restore Defaults"
    m.labels[10].text = "Done"
end sub

function onKeyEvent(key as string, press as boolean) as boolean
    if not press then return false
    if key = "back"
        m.top.closeRequested = true
        return true
    end if
    if key = "up" then m.index = (m.index + 10) mod 11
    if key = "down" then m.index = (m.index + 1) mod 11
    m.highlight.translation = [125, 240 + m.index * 64]
    if key = "OK" or key = "left" or key = "right"
        if m.index = 10
            m.top.closeRequested = true
            return true
        end if
        prefs = ReefValidateSettings(m.top.preferences)
        if m.index = 9
            m.top.preferences = ReefValidateSettings(invalid)
            return true
        end if
        row = m.schema[m.index]
        current = 0
        for i = 0 to row.choices.Count() - 1
            if row.choices[i] = prefs[row.id] then current = i
        end for
        direction = 1
        if key = "left" then direction = -1
        current = (current + direction + row.choices.Count()) mod row.choices.Count()
        prefs[row.id] = row.choices[current]
        m.top.preferences = prefs
        return true
    end if
    return key = "up" or key = "down"
end function
