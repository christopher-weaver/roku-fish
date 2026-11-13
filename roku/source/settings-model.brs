function ReefSettingsSchema() as object
    return [
        { id: "lighting", label: "Lighting", choices: ["Sunset", "Daylight", "Dusk", "Moonlight", "Automatic"], defaultValue: "Sunset" }
        { id: "density", label: "Fish density", choices: ["Low", "Medium", "High"], defaultValue: "Medium" }
        { id: "camera", label: "Camera movement", choices: ["Off", "Subtle", "Slow"], defaultValue: "Subtle" }
        { id: "bubbles", label: "Bubble density", choices: ["Off", "Low", "Medium"], defaultValue: "Low" }
        { id: "particles", label: "Water particles", choices: ["Off", "Low", "Medium"], defaultValue: "Low" }
        { id: "movement", label: "Fish movement", choices: ["Calm", "Natural", "Active"], defaultValue: "Natural" }
        { id: "quality", label: "Visual quality", choices: ["Auto", "Performance", "High"], defaultValue: "Auto" }
        { id: "clock", label: "Show clock", choices: ["Off", "On"], defaultValue: "Off" }
        { id: "fps", label: "Show FPS", choices: ["Off", "On"], defaultValue: "Off" }
    ]
end function

function ReefValidateSettings(raw as dynamic) as object
    result = {}
    valid = Type(raw) = "roAssociativeArray"
    for each row in ReefSettingsSchema()
        value = row.defaultValue
        if valid
            candidate = raw[row.id]
            if Type(candidate) = "String" or Type(candidate) = "roString"
                for each choice in row.choices
                    if candidate = choice then value = choice
                end for
            end if
        end if
        result[row.id] = value
    end for
    return result
end function

function ReefLoadSettings() as object
    reg = CreateObject("roRegistrySection", "deep-reef-v1")
    raw = invalid
    if reg.Exists("preferences") then raw = ParseJson(reg.Read("preferences"))
    return ReefValidateSettings(raw)
end function

sub ReefSaveSettings(raw as object)
    reg = CreateObject("roRegistrySection", "deep-reef-v1")
    reg.Write("preferences", FormatJson(ReefValidateSettings(raw)))
    reg.Flush()
end sub
