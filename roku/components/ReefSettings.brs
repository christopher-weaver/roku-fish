sub init()
    m.schema = ReefSettingsSchema()
    m.index = 0
    m.rows = m.top.FindNode("rows")
    m.highlight = m.top.FindNode("highlight")
    m.labels = [] : m.values = []
    for i = 0 to 10
        label = m.rows.CreateChild("Label")
        label.translation = [0, i * 64]
        label.width = 900 : label.height = 48
        label.font = CreateObject("roSGNode", "Font")
        label.font.size = 28
        label.color = "0xF5E0DBFF"
        value = m.rows.CreateChild("Label")
        value.translation = [1080, i * 64]
        value.width = 420 : value.height = 48
        value.font = CreateObject("roSGNode", "Font")
        value.font.size = 28
        value.color = "0xFFD3A8FF"
        m.labels.Push(label) : m.values.Push(value)
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
    if key = "back" then m.top.done = true : return true
    if key = "up" then m.index = (m.index + 10) mod 11
    if key = "down" then m.index = (m.index + 1) mod 11
    m.highlight.translation = [125, 240 + m.index * 64]
    if key = "OK" or key = "left" or key = "right"
        if m.index = 10 then m.top.done = true : return true
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
