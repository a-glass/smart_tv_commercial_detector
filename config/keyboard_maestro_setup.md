# Keyboard Maestro Macro Setup

## Macro: Football Auto-Mute System

### Trigger
- **Hot Key Trigger**: ⌘⌥F (Command+Option+F) to start/stop
- **Periodic Trigger**: Every 30 seconds (when enabled)

### Actions

#### 1. Check if System is Enabled
```applescript
-- Check if the auto-mute system should be running
set systemEnabled to do shell script "defaults read com.football-auto-mute enabled 2>/dev/null || echo 'false'"
if systemEnabled is not "true" then
    return
end if
```

#### 2. Get Active Browser Window Info
```applescript
-- Get YouTube TV tab information
tell application "Google Chrome"
    if (count of windows) > 0 then
        tell front window
            if (count of tabs) > 0 then
                tell active tab
                    set currentURL to URL
                    set currentTitle to title
                end tell
            end if
        end tell
    end if
end tell

-- Extract channel and show info using JavaScript
set channelInfo to do shell script "osascript -l JavaScript -e '
    var chrome = Application(\"Google Chrome\");
    if (chrome.windows.length > 0) {
        var tab = chrome.windows[0].activeTab;
        try {
            var result = tab.execute({javascript: \"
                var channelElement = document.querySelector(\".ytlr-guide-entry-text\");
                var titleElement = document.querySelector(\".watch-title\");
                var channel = channelElement ? channelElement.textContent.trim() : \"Unknown\";
                var title = titleElement ? titleElement.textContent.trim() : \"Unknown\";
                JSON.stringify({channel: channel, title: title, url: window.location.href});
            \"});
            result;
        } catch (e) {
            JSON.stringify({channel: \"Unknown\", title: \"Unknown\", url: tab.url});
        }
    } else {
        JSON.stringify({channel: \"Unknown\", title: \"Unknown\", url: \"\"});
    }
'"
```

#### 3. Capture Screenshot
- **Action**: "Capture Screen" 
- **Settings**: 
  - Capture: Front Window
  - Save to: `/tmp/football_screenshot_$(date +%s).png`
  - Format: PNG
  - Store result in variable: `ScreenshotPath`

#### 4. Call Python Detection Script
```bash
#!/bin/bash
cd "/Users/austinglass/football-auto-mute"
source venv/bin/activate

# Get the context from previous step
CONTEXT='%Variable%channelInfo%'
SCREENSHOT='%Variable%ScreenshotPath%'

# Run the detection
python3 src/km_helper.py "$SCREENSHOT" "$CONTEXT"
```

#### 5. Process Result and Log
```applescript
-- Get the result from the Python script
set detectionResult to do shell script result

-- Log to system log for debugging
do shell script "echo '" & (current date) & ": " & detectionResult & "' >> /Users/austinglass/football-auto-mute/logs/km_activity.log"

-- Parse result and handle any errors
try
    -- You can add additional actions here based on the result
    -- For example, display notifications for testing
    if detectionResult contains "COMMERCIAL" then
        display notification "Commercial detected - TV muted" with title "Football Auto-Mute"
    else if detectionResult contains "GAME" then
        display notification "Game content - TV unmuted" with title "Football Auto-Mute"
    end if
on error
    display notification "Detection error" with title "Football Auto-Mute"
end try
```

## Control Macro: Toggle Auto-Mute System

### Trigger
- **Hot Key**: ⌘⌥⇧F (Command+Option+Shift+F)

### Actions

#### 1. Toggle System State
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

## Setup Instructions

1. **Create New Macro Group** in Keyboard Maestro called "Football Auto-Mute"

2. **Import or manually create** the two macros described above

3. **Adjust paths** in the scripts to match your installation directory

4. **Test the macros** individually before enabling automatic operation

5. **Enable the periodic trigger** only after confirming everything works

## Troubleshooting

- Check the log file at `/Users/austinglass/football-auto-mute/logs/km_activity.log`
- Verify Python virtual environment is working: `source venv/bin/activate && python3 --version`
- Test CEC connection: `cec-client -l` to list devices
- Ensure YouTube TV is open in Chrome before testing

## Security Note

The macro requires Screen Recording permission for Chrome and Keyboard Maestro in System Preferences > Security & Privacy > Privacy.