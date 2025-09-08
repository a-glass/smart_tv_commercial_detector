-- Create Football Auto-Mute macros directly in Keyboard Maestro

tell application "Keyboard Maestro"
	
	-- Create the main detection macro
	set newMacro to make new macro in macro group "Football AutoMute" with properties {name:"Football Auto-Mute Detection"}
	
	-- Add hot key trigger (Cmd+Opt+F)
	make new hot key trigger in newMacro with properties {key code:3, modifiers:{command down, option down}}
	
	-- Add periodic trigger (every 30 seconds)
	make new periodic trigger in newMacro with properties {period:30}
	
	-- Add actions
	make new execute AppleScript action in newMacro with properties {script:"-- Check if the auto-mute system should be running
set systemEnabled to do shell script \"defaults read com.football-auto-mute enabled 2>/dev/null || echo 'false'\"
if systemEnabled is not \"true\" then
	return \"System disabled\"
end if"}
	
	make new execute AppleScript action in newMacro with properties {script:"-- Get YouTube TV tab information
try
	set channelInfo to do shell script \"osascript -l JavaScript -e '
		var chrome = Application(\\\"Google Chrome\\\");
		if (chrome.windows.length > 0) {
			var tab = chrome.windows[0].activeTab;
			try {
				var result = tab.execute({javascript: \\\"
					var channelElement = document.querySelector(\\\\\\\".ytlr-guide-entry-text\\\\\\\");
					var titleElement = document.querySelector(\\\\\\\".watch-title\\\\\\\");
					var channel = channelElement ? channelElement.textContent.trim() : \\\\\\\"Unknown\\\\\\\";
					var title = titleElement ? titleElement.textContent.trim() : \\\\\\\"Unknown\\\\\\\";
					JSON.stringify({channel: channel, title: title, url: window.location.href});
				\\\"});
				result;
			} catch (e) {
				JSON.stringify({channel: \\\\\\\"Unknown\\\\\\\", title: \\\\\\\"Unknown\\\\\\\", url: tab.url});
			}
		} else {
			JSON.stringify({channel: \\\\\\\"Unknown\\\\\\\", title: \\\\\\\"Unknown\\\\\\\", url: \\\"\\\"});
		}
	'\"
	set variable \"ChannelInfo\" to channelInfo
on error
	set variable \"ChannelInfo\" to \"{\\\"channel\\\": \\\"Unknown\\\", \\\"title\\\": \\\"Unknown\\\", \\\"url\\\": \\\"\\\"}\"
end try"}
	
	make new screen capture action in newMacro with properties {capture type:window, path:"/tmp/football_screenshot_%ExecutionID%.png", variable:"ScreenshotPath", window number:1}
	
	make new execute shell script action in newMacro with properties {script:"#!/bin/bash
cd \"/Users/austinglass/football-auto-mute\"
source venv/bin/activate

# Get the context and screenshot from Keyboard Maestro variables
CONTEXT=\"$KMVAR_ChannelInfo\"
SCREENSHOT=\"$KMVAR_ScreenshotPath\"

# Run the detection
python3 src/km_helper.py \"$SCREENSHOT\" \"$CONTEXT\" 2>&1", variable:"DetectionResult"}
	
	make new execute AppleScript action in newMacro with properties {script:"-- Get the result from the Python script and log it
set detectionResult to getvariable \"DetectionResult\"

-- Log to system log for debugging
do shell script \"echo '\" & (current date) & \": \" & detectionResult & \"' >> /Users/austinglass/football-auto-mute/logs/km_activity.log\"

-- Parse result and show notifications
try
	if detectionResult contains \"COMMERCIAL\" then
		display notification \"Commercial detected - TV muted\" with title \"Football Auto-Mute\"
	else if detectionResult contains \"GAME\" then
		display notification \"Game content - TV unmuted\" with title \"Football Auto-Mute\"
	else if detectionResult contains \"error\" then
		display notification \"Detection error: \" & detectionResult with title \"Football Auto-Mute\"
	end if
on error errMsg
	display notification \"Script error: \" & errMsg with title \"Football Auto-Mute\"
end try"}
	
	-- Create the toggle macro
	set toggleMacro to make new macro in macro group "Football AutoMute" with properties {name:"Toggle Football Auto-Mute System"}
	
	-- Add hot key trigger (Cmd+Opt+Shift+F)
	make new hot key trigger in toggleMacro with properties {key code:3, modifiers:{command down, option down, shift down}}
	
	-- Add shell script action
	make new execute shell script action in toggleMacro with properties {script:"#!/bin/bash
# Toggle the enabled state
current=$(defaults read com.football-auto-mute enabled 2>/dev/null || echo \"false\")
if [ \"$current\" = \"true\" ]; then
	defaults write com.football-auto-mute enabled false
	echo \"Football Auto-Mute System DISABLED\"
	osascript -e 'display notification \"System disabled\" with title \"Football Auto-Mute\"'
else
	defaults write com.football-auto-mute enabled true
	echo \"Football Auto-Mute System ENABLED\"
	osascript -e 'display notification \"System enabled\" with title \"Football Auto-Mute\"'
fi"}
	
end tell