# 🏈 Football Auto-Mute System

An AI-powered system that automatically mutes your TCL TV during commercial breaks while watching football on YouTube TV, using Claude Vision AI to intelligently detect game vs. commercial content.

## ✨ Features

- **🧠 AI-Powered Detection**: Uses Claude Vision API to analyze screenshots and distinguish between game content and commercials
- **📺 Seamless TV Control**: Controls TCL TV muting via HDMI-CEC commands from your MacBook
- **⌨️ Keyboard Maestro Integration**: Fully automated with configurable hotkeys and periodic detection
- **🏠 Home Assistant Support**: Optional integration with Home Assistant for remote control and automation
- **📊 Smart Context Awareness**: Considers channel, show title, and time context for better accuracy
- **📝 Comprehensive Logging**: Detailed logging and statistics for debugging and optimization

## 🎯 How It Works

1. **Screenshot Capture**: Keyboard Maestro captures screenshots of the YouTube TV browser window every 30 seconds
2. **Context Extraction**: Extracts show information (channel, title) from the browser using JavaScript
3. **AI Analysis**: Sends screenshot and context to Claude Vision API for "GAME" vs "COMMERCIAL" determination
4. **TV Control**: Automatically mutes/unmutes TV via HDMI-CEC based on AI detection
5. **Home Assistant**: Updates HA sensors and triggers automations (optional)

## 📋 Requirements

### Hardware
- MacBook Pro (Intel or Apple Silicon)
- TCL TV with HDMI-CEC support
- HDMI connection between MacBook and TV

### Software
- macOS 10.15+ 
- Chrome browser
- Keyboard Maestro 11.4+
- YouTube TV subscription
- Claude API key (Anthropic)
- Homebrew (will be installed automatically)

### Optional
- Home Assistant instance
- Home Assistant long-lived access token

## 🚀 Quick Start

### 1. Clone and Install

```bash
git clone <repository-url>
cd football-auto-mute
chmod +x scripts/install.sh
./scripts/install.sh
```

### 2. Configure API Key

Edit `config/config.yaml` and add your Claude API key:

```yaml
claude_api_key: "sk-ant-api03-your-key-here"
```

Get your API key from: https://console.anthropic.com/

### 3. Run Setup

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 4. Configure Keyboard Maestro

1. Open Keyboard Maestro
2. Follow the setup guide in `config/keyboard_maestro_setup.md`
3. Import or create the macros as described

### 5. Test the System

```bash
./scripts/test_system.sh
```

### 6. Start Watching Football!

```bash
./scripts/start_system.sh
```

Use **⌘⌥F** to start detection, **⌘⌥⇧F** to toggle system on/off.

## ⚙️ Configuration

### Main Configuration (`config/config.yaml`)

```yaml
# Claude AI API
claude_api_key: "your-api-key-here"

# Detection Settings
detection:
  interval_seconds: 30  # How often to check
  enable_logging: true

# TV Control
tv_control:
  enabled: true
  cec_device_id: 0
  mute_method: "volume_down"
  volume_steps: 5

# Home Assistant (Optional)
home_assistant:
  enabled: false
  url: "http://homeassistant.local:8123"
  token: "your-ha-token"
```

### Keyboard Maestro Setup

See `config/keyboard_maestro_setup.md` for detailed macro configuration.

Key macros:
- **Football Auto-Mute System**: Main detection loop (⌘⌥F)
- **Toggle Auto-Mute System**: Enable/disable system (⌘⌥⇧F)

## 🏠 Home Assistant Integration

### Setup

1. Enable in `config/config.yaml`:
```yaml
home_assistant:
  enabled: true
  url: "http://your-ha-ip:8123"
  token: "your-long-lived-token"
```

2. Add configuration to Home Assistant:
```bash
python3 src/ha_integration.py
```

3. Restart Home Assistant

### Available Entities

- `input_boolean.football_auto_mute_enabled` - System enable/disable switch
- `sensor.football_auto_mute_status` - Current detection status
- `sensor.football_auto_mute_stats` - Detection statistics

### Automations

The system creates automations for:
- Start/stop notifications
- Commercial detection alerts
- Game resumed notifications

## 🛠 Usage

### Manual Control

```bash
# Start the system
./scripts/start_system.sh

# Stop the system  
./scripts/stop_system.sh

# Test detection
./scripts/test_system.sh

# Check logs
tail -f logs/football_detector.log
```

### Keyboard Maestro Shortcuts

- **⌘⌥F** - Start/resume detection loop
- **⌘⌥⇧F** - Toggle system on/off

### Command Line Testing

```bash
# Test with a screenshot
source venv/bin/activate
python3 src/km_helper.py /path/to/screenshot.png '{"channel": "ESPN", "title": "NFL Game"}'

# Test CEC connection
cec-client -l

# Test Home Assistant integration
python3 src/ha_integration.py
```

## 📊 Monitoring and Logs

### Log Files

- `logs/football_detector.log` - Main system activity
- `logs/km_activity.log` - Keyboard Maestro macro activity

### Home Assistant Dashboard

If enabled, monitor via:
- Detection status sensor
- Statistics dashboard
- Automation history

### Debug Mode

Enable debug logging in `config/config.yaml`:

```yaml
logging:
  level: "DEBUG"
```

## 🔧 Troubleshooting

### Common Issues

**CEC Not Working**
```bash
# Check if TV is detected
cec-client -l

# Test CEC commands manually
echo "voldown 0" | cec-client -s -d 1
```

**Claude API Errors**
- Verify API key is correct
- Check API quota/billing
- Review logs for specific error messages

**Keyboard Maestro Not Triggering**
- Check macro is enabled
- Verify Chrome window is active
- Check Screen Recording permissions

**Detection Accuracy Issues**
- Review context information being sent
- Check screenshot quality/timing
- Examine detection history in logs

### Getting Help

1. Check the logs: `tail -f logs/football_detector.log`
2. Run test script: `./scripts/test_system.sh`
3. Verify configuration: `cat config/config.yaml`

## 🔒 Security & Privacy

- Screenshots are processed locally and sent only to Claude API
- No data is stored permanently (screenshots are deleted after analysis)
- Claude API calls are over HTTPS
- Home Assistant integration uses local network only
- All logs stored locally

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Test thoroughly
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Anthropic for Claude Vision API
- TCL for HDMI-CEC support
- Keyboard Maestro for automation capabilities
- Home Assistant community

---

**⚠️ Disclaimer**: This system is for personal use only. Ensure compliance with YouTube TV terms of service. The AI detection is not 100% accurate and may occasionally misclassify content.