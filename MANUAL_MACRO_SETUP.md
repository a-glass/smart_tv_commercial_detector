# Manual Keyboard Maestro Macro Setup

Since the automatic import isn't working, here's how to create the macros manually:

## Macro 1: Football Auto-Mute Detection

1. **Open Keyboard Maestro**
2. **Select "Football AutoMute" group** in the left panel
3. **Click the "+" button** to add a new macro
4. **Name it:** `Football Auto-Mute Detection`

### Add Triggers:
1. **Click "Add Trigger"** → **Hot Key Trigger**
   - Set to: **⌘⌥F** (Command+Option+F)
2. **Click "Add Trigger"** → **Periodic Trigger**
   - Set to: **30 seconds**

### Add Actions (in this order):

#### Action 1: Execute AppleScript
```applescript
-- Check if the auto-mute system should be running
set systemEnabled to do shell script "defaults read com.football-auto-mute enabled 2>/dev/null || echo 'false'"
if systemEnabled is not "true" then
    return "System disabled"
end if
```

#### Action 2: Execute AppleScript
```applescript
-- Get YouTube TV tab information
try
    set channelInfo to do shell script "osascript -l JavaScript -e '
        var chrome = Application(\"Google Chrome\");
        if (chrome.windows.length > 0) {
            var tab = chrome.windows[0].activeTab;
            try {
                var result = tab.execute({javascript: \"
                    var channelElement = document.querySelector(\\\".ytlr-guide-entry-text\\\");
                    var titleElement = document.querySelector(\\\".watch-title\\\");
                    var channel = channelElement ? channelElement.textContent.trim() : \\\"Unknown\\\";
                    var title = titleElement ? titleElement.textContent.trim() : \\\"Unknown\\\";
                    JSON.stringify({channel: channel, title: title, url: window.location.href});
                \"});
                result;
            } catch (e) {
                JSON.stringify({channel: \\\"Unknown\\\", title: \\\"Unknown\\\", url: tab.url});
            }
        } else {
            JSON.stringify({channel: \\\"Unknown\\\", title: \\\"Unknown\\\", url: \"\"});
        }
    '"
    set variable "ChannelInfo" to channelInfo
on error
    set variable "ChannelInfo" to "{\"channel\": \"Unknown\", \"title\": \"Unknown\", \"url\": \"\"}"
end try
```

#### Action 3: Screen Capture
- **Action**: Screen Capture
- **Capture**: Front Window  
- **Save to**: `/tmp/football_screenshot_%ExecutionID%.png`
- **Store result in variable**: `ScreenshotPath`

#### Action 4: Execute Shell Script
```bash
#!/bin/bash
cd "/Users/austinglass/football-auto-mute"
source venv/bin/activate

# Get the context and screenshot from Keyboard Maestro variables
CONTEXT="$KMVAR_ChannelInfo"
SCREENSHOT="$KMVAR_ScreenshotPath"

# Run the detection
python3 src/km_helper.py "$SCREENSHOT" "$CONTEXT" 2>&1
```
- **Store result in variable**: `DetectionResult`

#### Action 5: Execute AppleScript
```applescript
-- Get the result from the Python script and log it
set detectionResult to getvariable "DetectionResult"

-- Log to system log for debugging
do shell script "echo '" & (current date) & ": " & detectionResult & "' >> /Users/austinglass/football-auto-mute/logs/km_activity.log"

-- Parse result and show notifications
try
    if detectionResult contains "COMMERCIAL" then
        display notification "Commercial detected - TV muted" with title "Football Auto-Mute"
    else if detectionResult contains "GAME" then
        display notification "Game content - TV unmuted" with title "Football Auto-Mute"
    else if detectionResult contains "error" then
        display notification "Detection error: " & detectionResult with title "Football Auto-Mute"
    end if
on error errMsg
    display notification "Script error: " & errMsg with title "Football Auto-Mute"
end try
```

---

## Macro 2: Toggle Football Auto-Mute System

1. **Click "+" to add another new macro**
2. **Name it:** `Toggle Football Auto-Mute System`

### Add Trigger:
1. **Click "Add Trigger"** → **Hot Key Trigger**
   - Set to: **⌘⌥⇧F** (Command+Option+Shift+F)

### Add Action:

#### Action 1: Execute Shell Script
```bash
#!/bin/bash
# Toggle the enabled state
current=$(defaults read com.football-auto-mute enabled 2>/dev/null || echo "false")
if [ "$current" = "true" ]; then
    defaults write com.football-auto-mute enabled false
    echo "Football Auto-Mute System DISABLED"
    osascript -e 'display notification "System disabled" with title "Football Auto-Mute"'
else
    defaults write com.football-auto-mute enabled true
    echo "Football Auto-Mute System ENABLED"
    osascript -e 'display notification "System enabled" with title "Football Auto-Mute"'
fi
```

---

## Test the Setup

1. **Press ⌘⌥⇧F** - Should show enable/disable notification
2. **Press ⌘⌥F** - Should run detection (needs API credits)

The macros should now appear in your Football AutoMute group!