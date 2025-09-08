-- Test Chrome access and basic context
try
    set tabURL to do shell script "osascript -l JavaScript -e '
        var chrome = Application(\"Google Chrome\");
        if (chrome.windows.length > 0) {
            chrome.windows[0].activeTab.url();
        } else {
            \"No Chrome windows\";
        }
    '"
    
    set variable "ChannelInfo" to "{\"channel\": \"Test\", \"title\": \"" & tabURL & "\", \"url\": \"" & tabURL & "\"}"
    display notification "URL: " & tabURL with title "Football Auto-Mute"
    
on error errMsg
    set variable "ChannelInfo" to "{\"channel\": \"Error\", \"title\": \"Error\", \"url\": \"\"}"
    display notification "Chrome access error: " & errMsg with title "Football Auto-Mute"
end try