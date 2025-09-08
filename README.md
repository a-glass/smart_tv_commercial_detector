# 📺 Smart TV Commercial Detector for Home Assistant

An AI-powered Home Assistant blueprint that automatically detects TV commercials using the LLM Vision integration. The system analyzes images from any source (camera or file path) along with show context and outputs variables that can trigger any Home Assistant automation - from muting your TV to adjusting lights during commercial breaks.

## ✨ Features

- **🧠 AI-Powered Detection**: Uses the LLM Vision integration with multimodal AI models
- **📱 Home Assistant Native**: Runs entirely within Home Assistant
- **🖼️ Image Source Flexible**: Works with cameras or file paths 
- **🎯 Context-Aware**: Uses show information to improve detection accuracy
- **🔧 Flexible Automation**: Outputs status variables that can trigger any automation you want
- **🔄 Consecutive Detection Logic**: Configurable number of consecutive detections required before status changes
- **📊 Confidence Scoring**: Provides confidence levels for detection accuracy
- **⚡ Real-time Updates**: Continuously monitors and updates status in real-time
- **🎨 Easy Sharing**: Simple blueprint that others can import and use
- **📈 Statistics Tracking**: Built-in logging and statistics for monitoring performance

## 🎯 How It Works

1. **Image Acquisition**: Images from camera or file path
2. **Context Extraction**: Gets current show information from helper entity or filename  
3. **AI Analysis**: LLM Vision analyzes the image with show context to determine content vs commercial
4. **History Tracking**: Maintains history of recent detections for consecutive logic
5. **Status Updates**: Updates helper entities only after consecutive detections meet threshold
6. **Automation Triggers**: Your automations respond to the confirmed status changes

## 📋 Prerequisites

### Home Assistant Requirements
- **Home Assistant 2024.1+** (required for LLM Vision integration)
- **LLM Vision Integration** installed and configured via HACS
- **AI Provider** configured (OpenAI, Anthropic, Google Gemini, etc.)

### Image Source Options
- **Camera Entity**: Camera pointed at your TV (phone, webcam, or dedicated camera)
- **File Path**: Any method that updates a file with TV screenshots  
- **Manual Upload**: Manual image upload via Home Assistant services
- Smart TV or streaming device with Home Assistant integration (for volume control)
- Any devices you want to automate based on commercial detection

## 🚀 Quick Setup

### 1. Install LLM Vision Integration

1. **Install via HACS:**
   - Go to **HACS → Integrations**
   - Click **Explore & Download Repositories**
   - Search for "LLM Vision"
   - Install the integration
   - Restart Home Assistant

2. **Configure LLM Vision:**
   - Go to **Settings → Devices & Services → Add Integration**
   - Search for "LLM Vision" and add it
   - Configure your AI provider (OpenAI, Anthropic, Google Gemini, etc.)
   - Note down your **Provider ID** for the blueprint configuration

3. **Add media directory** to `configuration.yaml`:
   ```yaml
   homeassistant:
     media_dirs:
       llmvision: /media/llmvision
   ```
   
   **Note:** Your current config shows `media_dirs:` at the root level, but it should be under `homeassistant:` section. Update your configuration.yaml to:
   ```yaml
   homeassistant:
     media_dirs:
       llmvision: /media/llmvision
   
   # Move the existing media_dirs under homeassistant section
   # Remove the standalone media_dirs: line
   ```

### 2. Set Up Image Source

Choose your image source method:

**Option A: Camera Entity**
- Phone running Home Assistant Companion app as IP camera
- USB webcam connected to Home Assistant device  
- Dedicated IP camera positioned to view TV
- Existing security camera repositioned

**Option B: File Path**
- Script/automation that captures screenshots to a file
- External tools that update image files
- Screen recording software output


### 3. Create Helper Entities

Add these to your `configuration.yaml` or create via the UI:

```yaml
# Copy the contents of helper_entities.yaml
```

### 4. Import Blueprint

1. Go to **Settings → Automations & Scenes → Blueprints**
2. Click **Import Blueprint**
3. Use this URL: `https://github.com/your-repo/football_commercial_detector.yaml`
4. Or copy the blueprint file contents manually

### 5. Create Detection Automation

1. Go to **Settings → Automations & Scenes → Automations**  
2. Click **Add Automation → Start with Blueprint**
3. Select "Smart TV Commercial Detector"
4. Configure:
   - **Image Source Type**: Choose "camera" or "file"
   - **TV Camera**: Your camera entity (if using camera source)
   - **Image File Path**: Path to image file (if using file source)
   - **LLM Vision Provider**: Your Provider ID from LLM Vision setup
   - **Content Status Helper**: `input_select.tv_content_status`
   - **Confidence Helper**: `input_number.tv_detection_confidence`
   - **Last Detection Helper**: `input_datetime.tv_last_detection`
   - **Enable Switch**: `input_boolean.tv_auto_detection`
   - **Consecutive Detections Required**: How many in a row before status changes (default 2)
   - **Detection History Helper**: `input_text.tv_detection_history`
   - **Show Context Helper**: `input_text.tv_show_context`
   - **Extract Context from Filename**: Whether to get show info from filename
   - **Detection Interval**: How often to check (default 30 seconds)

### 6. Create Your Response Automations

Use the examples in `example_automations.yaml` to create automations that respond to the detection results, such as:
- Muting/unmuting your TV
- Adjusting room lighting
- Sending notifications
- Controlling other smart devices

## 🔧 Configuration

### Detection Settings

- **Interval**: How often to analyze (10-300 seconds)
- **Confidence Threshold**: Minimum confidence level for actions (recommended 75%+)
- **Motion Trigger**: Optional motion sensor to trigger immediate detection

### AI Optimization Tips

- **Camera Positioning**: Ensure clear view of TV with minimal glare
- **Lighting**: Consistent room lighting improves detection accuracy
- **Resolution**: Higher resolution camera provides better AI analysis
- **Timing**: Avoid detection during scene transitions or loading screens

## 📊 Available Variables

The system creates these entities you can use in automations:

### Input Entities
- `input_select.football_game_status` - Current status: "game", "commercial", or "unknown"
- `input_number.football_detection_confidence` - Confidence level (0-100%)
- `input_datetime.football_last_detection` - Timestamp of last detection
- `input_boolean.football_auto_detection` - Enable/disable the system
- `input_text.football_detection_history` - Recent detection history for consecutive logic

### Template Sensors
- `sensor.football_status_display` - Formatted display of current status
- `binary_sensor.football_game_active` - True when game is detected
- `binary_sensor.football_commercial_active` - True when commercial is detected
- `binary_sensor.football_high_confidence_detection` - True when confidence ≥ 80%
- `sensor.football_detection_history_count` - Number of recent detections stored
- `sensor.football_consecutive_same_detections` - Count of consecutive identical detections

## 🎮 Example Automations

### Basic TV Muting
```yaml
automation:
  - alias: "Mute TV During Commercials"
    trigger:
      platform: state
      entity_id: input_select.football_game_status  
      to: "commercial"
    condition:
      - condition: numeric_state
        entity_id: input_number.football_detection_confidence
        above: 75
    action:
      service: media_player.volume_mute
      target:
        entity_id: media_player.your_tv
      data:
        is_volume_muted: true
```

### Smart Lighting Control
```yaml
automation:
  - alias: "Dim Lights During Game"
    trigger:
      platform: state
      entity_id: binary_sensor.football_game_active
      to: "on"
    action:
      service: light.turn_on
      target:
        entity_id: light.living_room
      data:
        brightness_pct: 20
```

See `example_automations.yaml` for more examples.

## 🔍 Troubleshooting

### Detection Issues
- **Low Confidence**: Check camera positioning and lighting
- **False Positives**: Increase confidence threshold in automations
- **Missed Detections**: Decrease detection interval or improve camera angle
- **No Detections**: Verify AI integration is working and camera captures TV clearly

### Home Assistant Issues
- **Blueprint Import Failed**: Check Home Assistant version (2025.8+ required)
- **AI Task Not Available**: Verify AI integration is properly configured
- **Camera Offline**: Check camera connection and Home Assistant integration

### Performance Optimization
- **High CPU Usage**: Increase detection interval or use local AI model
- **Slow Response**: Check network latency to AI service
- **Storage Growth**: Enable log rotation in Home Assistant

## 📈 Monitoring and Statistics

### Built-in Logging
The system automatically logs all detection events to the Home Assistant logbook with:
- Detection results and confidence levels
- Timestamp and duration information
- State change history

### Custom Statistics
Create additional sensors to track:
- Daily commercial/game time ratios
- Detection accuracy over time
- Peak viewing hours
- System uptime and reliability

## 🔒 Privacy and Security

- **Local Processing**: Camera images are only sent to your configured AI service
- **No External Storage**: Screenshots are not permanently stored
- **Secure APIs**: All AI service communication uses HTTPS
- **Home Assistant Only**: No external services required beyond AI integration

## 🤝 Contributing and Sharing

This blueprint is designed to be easily shared with the Home Assistant community:

1. **Fork this repository**
2. **Customize for your setup**
3. **Share improvements via pull requests**
4. **Create blueprint variations for different sports or TV content**

## 📄 Files Included

- `smart_tv_commercial_detector.yaml` - Main Home Assistant blueprint
- `helper_entities.yaml` - Required helper entity configurations
- `example_automations.yaml` - Example response automations
- `README.md` - This documentation

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Home Assistant logs for error messages
3. Test AI integration independently to verify it's working
4. Open an issue in this repository with detailed information

## 📄 License

MIT License - Feel free to use, modify, and share!

## 🙏 Acknowledgments

- Home Assistant team for the AI Task integration
- AI service providers (OpenAI, Anthropic, Google, Ollama)
- Home Assistant community for blueprints and automation ideas

---

**⚠️ Disclaimer**: This system is for personal use only. Detection accuracy may vary based on camera setup, lighting conditions, and AI service performance. Always verify automated actions (like muting) are working as expected during initial setup.