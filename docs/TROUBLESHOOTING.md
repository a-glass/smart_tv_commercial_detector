# 🔧 Football Auto-Mute Troubleshooting Guide

This guide covers common issues and their solutions.

## 🚨 Common Issues

### 1. CEC Control Not Working

**Symptoms:**
- TV doesn't mute/unmute
- Error messages about CEC client
- "Failed to control TV" in logs

**Solutions:**

1. **Check CEC client installation:**
```bash
which cec-client
# Should return: /opt/homebrew/bin/cec-client (Apple Silicon) or /usr/local/bin/cec-client (Intel)
```

2. **Test CEC device detection:**
```bash
cec-client -l
# Should show your TV and other CEC devices
```

3. **Manual CEC test:**
```bash
# Test volume down
echo "voldown 0" | cec-client -s -d 1

# Test volume up  
echo "volup 0" | cec-client -s -d 1
```

4. **Check HDMI-CEC settings on TV:**
   - Go to TV Settings → System → HDMI-CEC
   - Enable "Device Auto Power Off"
   - Enable "TV Auto Power On"
   - Try different HDMI port

5. **MacBook HDMI settings:**
   - Use System Preferences → Displays
   - Ensure TV is detected as audio output
   - Try unplugging/reconnecting HDMI cable

### 2. Claude API Issues

**Symptoms:**
- "API key not found" errors
- "Authentication failed" 
- "Rate limit exceeded"

**Solutions:**

1. **Check API key:**
```bash
grep claude_api_key config/config.yaml
# Should not show "YOUR_CLAUDE_API_KEY_HERE"
```

2. **Test API connection:**
```bash
source venv/bin/activate
python3 -c "
from anthropic import Anthropic
client = Anthropic(api_key='YOUR_KEY_HERE')
print('API connection successful')
"
```

3. **Check API quota:**
   - Visit https://console.anthropic.com/
   - Check usage and billing status
   - Verify account is in good standing

4. **Rate limiting:**
   - Increase `interval_seconds` in config (try 60 instead of 30)
   - Check if you're making other API calls concurrently

### 3. Keyboard Maestro Issues

**Symptoms:**
- Macros not triggering
- Screenshot capture fails
- "Permission denied" errors

**Solutions:**

1. **Check permissions:**
   - System Preferences → Security & Privacy → Privacy
   - Screen Recording: Enable for Keyboard Maestro
   - Accessibility: Enable for Keyboard Maestro

2. **Test screenshot capture manually:**
```bash
# In Keyboard Maestro, test the screenshot action alone
# Should create a file in /tmp/
```

3. **Verify macro triggers:**
   - Check hotkey conflicts with other apps
   - Ensure Chrome is the active application
   - Test periodic trigger separately

4. **Debug macro execution:**
   - Add "Display Text" actions in macro to see where it fails
   - Check Keyboard Maestro Engine.log in Console app

### 4. Screenshot Analysis Issues

**Symptoms:**
- Always detects "GAME" or "COMMERCIAL"
- Poor detection accuracy
- "Unexpected result" warnings in logs

**Solutions:**

1. **Check screenshot quality:**
```bash
# Look at the screenshots being captured
ls -la /tmp/football_screenshot_*
# Open in Preview to verify they show the content clearly
```

2. **Verify browser window capture:**
   - Ensure YouTube TV is in full-screen or large window
   - Check that entire video area is captured
   - Test with different browser zoom levels

3. **Context information:**
```bash
# Check what context is being sent
tail -f logs/football_detector.log | grep "Context:"
```

4. **Manual testing:**
```bash
source venv/bin/activate
python3 src/km_helper.py screenshot.png '{"channel":"ESPN","title":"NFL Game"}'
```

### 5. Home Assistant Integration Issues

**Symptoms:**
- HA entities not created
- Status not updating
- Authentication errors

**Solutions:**

1. **Test HA connection:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     http://your-ha-ip:8123/api/
```

2. **Check token permissions:**
   - Ensure long-lived token has appropriate scopes
   - Test with a simple API call first

3. **Verify configuration:**
```bash
python3 src/ha_integration.py
# Should show connection test results
```

4. **Check HA logs:**
   - Look for API call errors in Home Assistant logs
   - Verify entity IDs are being created correctly

### 6. Python/Virtual Environment Issues

**Symptoms:**
- Import errors
- "Module not found" errors
- Python version conflicts

**Solutions:**

1. **Recreate virtual environment:**
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Check Python version:**
```bash
python3 --version
# Should be 3.8 or higher
```

3. **Verify all dependencies:**
```bash
source venv/bin/activate
pip list
# Check that all required packages are installed
```

## 🧪 Diagnostic Commands

### Full System Test
```bash
./scripts/test_system.sh
```

### Check All Components
```bash
# CEC
cec-client -l

# Python environment
source venv/bin/activate && python3 --version

# API key
grep -v "YOUR_CLAUDE_API_KEY_HERE" config/config.yaml

# Home Assistant (if enabled)
python3 src/ha_integration.py
```

### Monitor Live Activity
```bash
# Watch logs in real-time
tail -f logs/football_detector.log

# Watch Keyboard Maestro activity
tail -f logs/km_activity.log

# Monitor CEC commands
cec-client | grep -v "TRAFFIC"
```

## 📊 Debug Mode

Enable detailed logging by editing `config/config.yaml`:

```yaml
logging:
  level: "DEBUG"
```

Then restart the system and check logs for detailed information.

## 🔄 Reset Everything

If all else fails, complete reset:

```bash
# Stop the system
./scripts/stop_system.sh

# Remove all generated files
rm -rf venv logs/*.log temp/*

# Reinstall
./scripts/install.sh
./scripts/setup.sh

# Reconfigure API key
nano config/config.yaml
```

## 📞 Getting More Help

1. **Check logs first:** Most issues will show up in the log files
2. **Test components individually:** Use the diagnostic commands above
3. **Verify permissions:** Many issues are permission-related on macOS
4. **Start simple:** Test with a single screenshot before automating

## ⚠️ Known Limitations

- **CEC reliability:** Some TV models have inconsistent CEC implementations
- **API rate limits:** Claude API has usage limits that may affect frequent detection
- **Screenshot timing:** Fast channel changes might capture transitional content
- **Browser compatibility:** Tested primarily with Chrome; other browsers may vary

## 🔧 Performance Tuning

### Reduce API Calls
```yaml
detection:
  interval_seconds: 60  # Instead of 30
```

### Improve Accuracy
- Use higher quality screenshots
- Ensure stable browser window size
- Test during actual game broadcasts

### Battery Life (MacBook)
- Increase detection interval
- Disable unnecessary Home Assistant updates
- Use power adapter during games