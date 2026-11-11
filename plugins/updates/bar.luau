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
    noctalia.runAsync('"$HOME/.local/bin/system-update" --status', function(result)
        busy = false
        local data = result.exitCode == 0 and noctalia.json.decode(result.stdout) or nil
        if data and type(data) == "table" then
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
    local target = hovering and 1 or 0
    if math.abs(progress - target) < 0.01 then
        progress = target
        noctalia.setUpdateInterval(1000)
    else
        progress = progress + (target - progress) * 0.45
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
    noctalia.runAsync('"$HOME/.local/bin/system-update" --open')
end
function onRightClick()
    noctalia.runAsync('"$HOME/.local/bin/system-update" --reload')
end
barWidget.setVisible(true)
barWidget.setGlyph("packages")
barWidget.setText("")
noctalia.setUpdateInterval(1000)
poll()
