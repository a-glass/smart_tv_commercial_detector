#!/usr/bin/env python3
"""
Football Commercial Auto-Mute System
AI-powered detection of game vs commercial content
"""

import base64
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

import requests
from anthropic import Anthropic
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/football_detector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FootballDetector:
    """Main class for detecting game vs commercial content"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.anthropic_client = Anthropic(api_key=self.config['claude_api_key'])
        self.tv_muted = False
        self.last_detection = None
        self.detection_history = []
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        import yaml
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            raise
            
    def analyze_screenshot(self, screenshot_path: str, context: Dict) -> str:
        """
        Send screenshot to Claude Vision API for analysis
        Returns: "GAME" or "COMMERCIAL"
        """
        try:
            # Encode image to base64
            with open(screenshot_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Create prompt based on context
            prompt = self._create_analysis_prompt(context)
            
            # Send to Claude Vision API
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_data
                                }
                            }
                        ]
                    }
                ]
            )
            
            result = response.content[0].text.strip().upper()
            
            # Ensure we only return valid responses
            if result in ["GAME", "COMMERCIAL"]:
                logger.info(f"Detection result: {result}")
                return result
            else:
                logger.warning(f"Unexpected result: {result}, defaulting to GAME")
                return "GAME"
                
        except Exception as e:
            logger.error(f"Error analyzing screenshot: {e}")
            return "GAME"  # Default to not muting on errors
    
    def _create_analysis_prompt(self, context: Dict) -> str:
        """Create a contextual prompt for Claude Vision API"""
        current_time = datetime.now().strftime("%H:%M")
        
        base_prompt = f"""
You are analyzing a screenshot from YouTube TV to determine if it shows GAME content or COMMERCIAL content during football coverage.

Context:
- Channel: {context.get('channel', 'Unknown')}
- Show: {context.get('title', 'Unknown')}
- Time: {current_time}
- Day: {datetime.now().strftime('%A')}

Look for these GAME indicators:
- Football field with yard lines
- Players in football uniforms
- Scoreboards with team names/scores
- Down and distance indicators
- Play clock or game clock
- Commentator graphics overlays
- Replay graphics
- NFL/college football logos

Look for these COMMERCIAL indicators:
- Product advertisements
- Car commercials
- Food/beverage ads
- Insurance/finance ads
- Generic backgrounds without football field
- Non-sports related content
- Different video quality/aspect ratio

Respond with exactly one word: "GAME" or "COMMERCIAL"
"""
        return base_prompt.strip()
    
    def control_tv_mute(self, should_mute: bool) -> bool:
        """Control TV muting via HDMI-CEC"""
        try:
            if should_mute and not self.tv_muted:
                # Mute the TV
                result = subprocess.run(
                    ["cec-client", "-s", "-d", "1"],
                    input="standby 0\nvoldown 0\nvoldown 0\nvoldown 0\nvoldown 0\nvoldown 0\nq\n",
                    text=True,
                    capture_output=True,
                    timeout=10
                )
                if result.returncode == 0:
                    self.tv_muted = True
                    logger.info("TV muted")
                    return True
                else:
                    logger.error(f"Failed to mute TV: {result.stderr}")
                    
            elif not should_mute and self.tv_muted:
                # Unmute the TV
                result = subprocess.run(
                    ["cec-client", "-s", "-d", "1"],
                    input="on 0\nvolup 0\nvolup 0\nvolup 0\nvolup 0\nvolup 0\nq\n",
                    text=True,
                    capture_output=True,
                    timeout=10
                )
                if result.returncode == 0:
                    self.tv_muted = False
                    logger.info("TV unmuted")
                    return True
                else:
                    logger.error(f"Failed to unmute TV: {result.stderr}")
                    
        except subprocess.TimeoutExpired:
            logger.error("CEC command timeout")
        except Exception as e:
            logger.error(f"Error controlling TV: {e}")
            
        return False
    
    def update_home_assistant(self, detection: str) -> None:
        """Update Home Assistant with current detection status"""
        if not self.config.get('home_assistant', {}).get('enabled', False):
            return
            
        try:
            ha_config = self.config['home_assistant']
            url = f"{ha_config['url']}/api/states/sensor.football_auto_mute"
            headers = {
                'Authorization': f"Bearer {ha_config['token']}",
                'Content-Type': 'application/json'
            }
            data = {
                'state': detection,
                'attributes': {
                    'tv_muted': self.tv_muted,
                    'last_updated': datetime.now().isoformat(),
                    'detection_confidence': 'high'  # Could be enhanced
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=5)
            if response.status_code == 200:
                logger.info("Updated Home Assistant")
            else:
                logger.warning(f"Failed to update Home Assistant: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error updating Home Assistant: {e}")
    
    def process_detection(self, screenshot_path: str, context: Dict) -> Dict:
        """
        Main detection processing function
        Called by Keyboard Maestro macro
        """
        start_time = time.time()
        
        try:
            # Analyze the screenshot
            detection = self.analyze_screenshot(screenshot_path, context)
            
            # Determine if we should mute
            should_mute = detection == "COMMERCIAL"
            
            # Control TV if needed
            tv_success = self.control_tv_mute(should_mute)
            
            # Update Home Assistant
            self.update_home_assistant(detection)
            
            # Store detection history
            result = {
                'timestamp': datetime.now().isoformat(),
                'detection': detection,
                'should_mute': should_mute,
                'tv_muted': self.tv_muted,
                'tv_control_success': tv_success,
                'processing_time': time.time() - start_time,
                'context': context
            }
            
            self.detection_history.append(result)
            
            # Keep only last 100 detections
            if len(self.detection_history) > 100:
                self.detection_history = self.detection_history[-100:]
            
            return result
            
        except Exception as e:
            logger.error(f"Error in process_detection: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'detection': 'ERROR',
                'error': str(e),
                'processing_time': time.time() - start_time
            }


def main():
    """Command line interface for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Football Auto-Mute Detector')
    parser.add_argument('screenshot', help='Path to screenshot file')
    parser.add_argument('--context', help='JSON context data', default='{}')
    parser.add_argument('--config', help='Config file path', default='config/config.yaml')
    
    args = parser.parse_args()
    
    # Create logs directory if it doesn't exist
    Path('logs').mkdir(exist_ok=True)
    
    try:
        detector = FootballDetector(args.config)
        context = json.loads(args.context)
        result = detector.process_detection(args.screenshot, context)
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(json.dumps({'error': str(e)}))


if __name__ == "__main__":
    main()