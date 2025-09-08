#!/usr/bin/env python3
"""
Script to create Keyboard Maestro macros for the Football Auto-Mute system
"""

import plistlib
import uuid
import subprocess
import sys
import os

def generate_uuid():
    """Generate a UUID for Keyboard Maestro"""
    return str(uuid.uuid4()).upper()

def create_detection_macro():
    """Create the main detection macro"""
    return {
        'CreationDate': '2025-09-07T16:30:00Z',
        'CustomIconData': None,
        'IsActive': True,
        'ModificationDate': '2025-09-07T16:30:00Z',
        'Name': 'Football Auto-Mute Detection',
        'Triggers': [
            {
                'FireType': 'Pressed',
                'KeyCode': 3,  # F key
                'MacroTriggerType': 'HotKey',
                'Modifiers': 768,  # Cmd+Opt
                'TriggerType': 'HotKey'
            },
            {
                'MacroTriggerType': 'Periodic',
                'Period': 30.0,
                'TriggerType': 'Periodic'
            }
        ],
        'Actions': [
            {
                'ActionType': 'ExecuteAppleScript',
                'MacroActionType': 'ExecuteAppleScript',
                'Source': '''-- Check if the auto-mute system should be running
set systemEnabled to do shell script "defaults read com.football-auto-mute enabled 2>/dev/null || echo 'false'"
if systemEnabled is not "true" then
    return "System disabled"
end if'''
            },
            {
                'ActionType': 'ExecuteAppleScript',
                'MacroActionType': 'ExecuteAppleScript',
                'Source': '''-- Get YouTube TV tab information
try
    set channelInfo to do shell script "osascript -l JavaScript -e '
        var chrome = Application(\\"Google Chrome\\");
        if (chrome.windows.length > 0) {
            var tab = chrome.windows[0].activeTab;
            try {
                var result = tab.execute({javascript: \\"
                    var channelElement = document.querySelector(\\\\\\".ytlr-guide-entry-text\\\\\\");
                    var titleElement = document.querySelector(\\\\\\".watch-title\\\\\\");
                    var channel = channelElement ? channelElement.textContent.trim() : \\\\\\"Unknown\\\\\\";
                    var title = titleElement ? titleElement.textContent.trim() : \\\\\\"Unknown\\\\\\";
                    JSON.stringify({channel: channel, title: title, url: window.location.href});
                \\"});
                result;
            } catch (e) {
                JSON.stringify({channel: \\\\\\"Unknown\\\\\\", title: \\\\\\"Unknown\\\\\\", url: tab.url});
            }
        } else {
            JSON.stringify({channel: \\\\\\"Unknown\\\\\\", title: \\\\\\"Unknown\\\\\\", url: \\"\\"});
        }
    '"
    set variable "ChannelInfo" to channelInfo
on error
    set variable "ChannelInfo" to "{\\"channel\\": \\"Unknown\\", \\"title\\": \\"Unknown\\", \\"url\\": \\"\\"}"
end try'''
            },
            {
                'ActionType': 'ScreenCapture',
                'CaptureType': 'Window',
                'MacroActionType': 'ScreenCapture',
                'Path': '/tmp/football_screenshot_%ExecutionID%.png',
                'Variable': 'ScreenshotPath',
                'WindowNumber': 1
            },
            {
                'ActionType': 'ExecuteShellScript',
                'MacroActionType': 'ExecuteShellScript',
                'Source': '''#!/bin/bash
cd "/Users/austinglass/football-auto-mute"
source venv/bin/activate

# Get the context and screenshot from Keyboard Maestro variables
CONTEXT="$KMVAR_ChannelInfo"
SCREENSHOT="$KMVAR_ScreenshotPath"

# Run the detection
python3 src/km_helper.py "$SCREENSHOT" "$CONTEXT" 2>&1''',
                'TrimResults': True,
                'TrimResultsNew': True,
                'UseText': True,
                'Variable': 'DetectionResult'
            },
            {
                'ActionType': 'ExecuteAppleScript',
                'MacroActionType': 'ExecuteAppleScript',
                'Source': '''-- Get the result from the Python script and log it
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
end try'''
            }
        ],
        'UID': generate_uuid()
    }

def create_toggle_macro():
    """Create the system toggle macro"""
    return {
        'CreationDate': '2025-09-07T16:30:00Z',
        'CustomIconData': None,
        'IsActive': True,
        'ModificationDate': '2025-09-07T16:30:00Z',
        'Name': 'Toggle Football Auto-Mute System',
        'Triggers': [
            {
                'FireType': 'Pressed',
                'KeyCode': 3,  # F key
                'MacroTriggerType': 'HotKey',
                'Modifiers': 896,  # Cmd+Opt+Shift
                'TriggerType': 'HotKey'
            }
        ],
        'Actions': [
            {
                'ActionType': 'ExecuteShellScript',
                'MacroActionType': 'ExecuteShellScript',
                'Source': '''#!/bin/bash
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
fi''',
                'TrimResults': True,
                'TrimResultsNew': True,
                'UseText': True
            }
        ],
        'UID': generate_uuid()
    }

def main():
    # Path to Keyboard Maestro plist
    km_plist_path = os.path.expanduser("~/Library/Application Support/Keyboard Maestro/Keyboard Maestro Macros.plist")
    
    print("Reading Keyboard Maestro macros...")
    
    # Read the current plist
    with open(km_plist_path, 'rb') as f:
        km_data = plistlib.load(f)
    
    # Find the Football AutoMute group
    football_group = None
    for group in km_data['MacroGroups']:
        if group['Name'] == 'Football AutoMute':
            football_group = group
            break
    
    if not football_group:
        print("ERROR: Football AutoMute group not found!")
        return 1
    
    print(f"Found Football AutoMute group with {len(football_group['Macros'])} existing macros")
    
    # Create the macros
    detection_macro = create_detection_macro()
    toggle_macro = create_toggle_macro()
    
    # Add them to the group
    football_group['Macros'].extend([detection_macro, toggle_macro])
    
    print(f"Added 2 new macros. Group now has {len(football_group['Macros'])} macros")
    
    # Write back to the plist
    with open(km_plist_path, 'wb') as f:
        plistlib.dump(km_data, f)
    
    print("✅ Successfully added macros to Keyboard Maestro!")
    print("\nMacros added:")
    print("1. 'Football Auto-Mute Detection' - Trigger: ⌘⌥F (also runs every 30 seconds)")
    print("2. 'Toggle Football Auto-Mute System' - Trigger: ⌘⌥⇧F")
    print("\nPlease restart Keyboard Maestro Engine to load the new macros.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())