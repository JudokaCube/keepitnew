local displayMode = "hover"
local animation = .45
local busy = false
local renderedText = nil
local hasStatus = false
local label = "…"
local hovering = false
local progress = 0
local lastPoll = 0

local function render()
    local count = math.floor((utf8.len(label) or #label) * progress + 0.5)
    local stop = utf8.offset(label, count + 1)
    local text = count == 0 and "" or (stop and label:sub(1, stop - 1) or label)
    if text ~= renderedText then barWidget.setText(text); renderedText = text end
end

local function poll()
    if busy then return end
    busy = true
    lastPoll = os.time()
    noctalia.runAsync('if command -v keepitnew >/dev/null 2>&1; then keepitnew --status; else "$HOME/.local/bin/system-update" --status; fi', function(result)
        busy = false
        local data = result.exitCode == 0 and noctalia.json.decode(result.stdout) or nil
        if data and type(data) == "table" then
            displayMode = data.displayMode or "hover"
            animation = data.animation or .45
            barWidget.setVisible(data.visible ~= false)
            hasStatus = true
            label = data.text or "…"
            barWidget.setGlyph(data.glyph or "packages")
            barWidget.setColor(data.color or "#88c0d0")
            barWidget.setGlyphColor(data.color or "#88c0d0")
            barWidget.setTooltip(data.tips)
        elseif not hasStatus then
            -- Keep the last valid display during transient polling failures.
            label = "!"
            barWidget.setTooltip("Status unavailable")
        end
        render()
    end, 5000)
end

function update()
    if os.time() - lastPoll >= 5 then poll() end
    local target = (displayMode == "always" or (displayMode ~= "icon" and hovering)) and 1 or 0
    if math.abs(progress - target) < 0.01 then
        progress = target
        noctalia.setUpdateInterval(1000)
    else
        progress = progress + (target - progress) * animation
        noctalia.setUpdateInterval(16)
    end
    render()
end
function onHover(value)
    hovering = value
    noctalia.setUpdateInterval(16)
    update()
end
function onClick()
    noctalia.runAsync('if command -v keepitnew >/dev/null 2>&1; then keepitnew --open; else "$HOME/.local/bin/system-update" --open; fi')
end
function onRightClick()
    noctalia.runAsync('if command -v keepitnew >/dev/null 2>&1; then keepitnew --reload; else "$HOME/.local/bin/system-update" --reload; fi')
end
barWidget.setVisible(true)
barWidget.setGlyph("packages")
barWidget.setText("")
noctalia.setUpdateInterval(1000)
poll()
