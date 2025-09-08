#!/usr/bin/env python3
"""
Home Assistant Integration for Football Auto-Mute System
Provides switches, sensors, and automation capabilities
"""

import json
import logging
import requests
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class HomeAssistantIntegration:
    """Home Assistant API integration"""
    
    def __init__(self, config: Dict):
        self.config = config.get('home_assistant', {})
        self.enabled = self.config.get('enabled', False)
        
        if self.enabled:
            self.url = self.config['url'].rstrip('/')
            self.token = self.config['token']
            self.headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
    
    def create_entities(self) -> bool:
        """Create necessary entities in Home Assistant"""
        if not self.enabled:
            return True
            
        entities = [
            {
                'entity_id': 'input_boolean.football_auto_mute_enabled',
                'state': 'off',
                'attributes': {
                    'friendly_name': 'Football Auto-Mute Enabled',
                    'icon': 'mdi:television'
                }
            },
            {
                'entity_id': 'sensor.football_auto_mute_status',
                'state': 'idle',
                'attributes': {
                    'friendly_name': 'Football Auto-Mute Status',
                    'icon': 'mdi:eye',
                    'last_detection': None,
                    'tv_muted': False,
                    'detection_count': 0
                }
            },
            {
                'entity_id': 'sensor.football_auto_mute_stats',
                'state': '0',
                'attributes': {
                    'friendly_name': 'Football Auto-Mute Statistics',
                    'icon': 'mdi:chart-line',
                    'total_detections': 0,
                    'commercial_count': 0,
                    'game_count': 0,
                    'mute_count': 0,
                    'session_start': None
                }
            }
        ]
        
        success = True
        for entity in entities:
            if not self._create_entity(entity):
                success = False
                
        return success
    
    def _create_entity(self, entity_data: Dict) -> bool:
        """Create or update a single entity"""
        try:
            url = f"{self.url}/api/states/{entity_data['entity_id']}"
            response = requests.post(
                url, 
                headers=self.headers,
                json={
                    'state': entity_data['state'],
                    'attributes': entity_data['attributes']
                },
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Created/updated entity: {entity_data['entity_id']}")
                return True
            else:
                logger.error(f"Failed to create entity {entity_data['entity_id']}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating entity {entity_data['entity_id']}: {e}")
            return False
    
    def update_status(self, detection_result: Dict) -> bool:
        """Update status sensor with latest detection"""
        if not self.enabled:
            return True
            
        try:
            # Update main status sensor
            status_data = {
                'state': detection_result.get('detection', 'unknown'),
                'attributes': {
                    'friendly_name': 'Football Auto-Mute Status',
                    'icon': 'mdi:eye',
                    'last_detection': detection_result.get('timestamp'),
                    'tv_muted': detection_result.get('tv_muted', False),
                    'processing_time': detection_result.get('processing_time', 0),
                    'context': detection_result.get('context', {}),
                    'tv_control_success': detection_result.get('tv_control_success', False)
                }
            }
            
            url = f"{self.url}/api/states/sensor.football_auto_mute_status"
            response = requests.post(url, headers=self.headers, json=status_data, timeout=5)
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            logger.error(f"Error updating HA status: {e}")
            return False
    
    def update_statistics(self, detection_history: list) -> bool:
        """Update statistics sensor"""
        if not self.enabled or not detection_history:
            return True
            
        try:
            # Calculate statistics from detection history
            total = len(detection_history)
            commercial_count = sum(1 for d in detection_history if d.get('detection') == 'COMMERCIAL')
            game_count = sum(1 for d in detection_history if d.get('detection') == 'GAME')
            mute_count = sum(1 for d in detection_history if d.get('should_mute', False))
            
            # Find session start (first detection of the day)
            session_start = None
            if detection_history:
                first_detection = min(detection_history, key=lambda x: x.get('timestamp', ''))
                session_start = first_detection.get('timestamp')
            
            stats_data = {
                'state': str(total),
                'attributes': {
                    'friendly_name': 'Football Auto-Mute Statistics',
                    'icon': 'mdi:chart-line',
                    'total_detections': total,
                    'commercial_count': commercial_count,
                    'game_count': game_count,
                    'mute_count': mute_count,
                    'commercial_percentage': round((commercial_count / total * 100) if total > 0 else 0, 1),
                    'session_start': session_start,
                    'last_updated': datetime.now().isoformat()
                }
            }
            
            url = f"{self.url}/api/states/sensor.football_auto_mute_stats"
            response = requests.post(url, headers=self.headers, json=stats_data, timeout=5)
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            logger.error(f"Error updating HA statistics: {e}")
            return False
    
    def is_enabled(self) -> bool:
        """Check if the system is enabled via Home Assistant switch"""
        if not self.enabled:
            return True  # Default to enabled if HA not configured
            
        try:
            url = f"{self.url}/api/states/input_boolean.football_auto_mute_enabled"
            response = requests.get(url, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('state') == 'on'
            else:
                logger.warning(f"Could not check HA switch status: {response.status_code}")
                return True  # Default to enabled on error
                
        except Exception as e:
            logger.error(f"Error checking HA enabled status: {e}")
            return True  # Default to enabled on error
    
    def send_notification(self, title: str, message: str, notification_id: str = None) -> bool:
        """Send notification via Home Assistant"""
        if not self.enabled:
            return True
            
        try:
            data = {
                'title': title,
                'message': message
            }
            
            if notification_id:
                data['data'] = {'tag': notification_id}
            
            url = f"{self.url}/api/services/notify/notify"
            response = requests.post(url, headers=self.headers, json=data, timeout=5)
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            logger.error(f"Error sending HA notification: {e}")
            return False


def create_ha_configuration() -> str:
    """Generate Home Assistant configuration YAML"""
    config = """
# Football Auto-Mute System Configuration
# Add this to your configuration.yaml

input_boolean:
  football_auto_mute_enabled:
    name: Football Auto-Mute Enabled
    icon: mdi:television

sensor:
  - platform: rest
    name: Football Auto-Mute Status
    resource: http://your-mac-ip:8000/status
    scan_interval: 30
    json_attributes:
      - last_detection
      - tv_muted
      - processing_time
      - context

automation:
  - alias: "Football Auto-Mute: Start Detection"
    trigger:
      - platform: state
        entity_id: input_boolean.football_auto_mute_enabled
        to: 'on'
    action:
      - service: notify.notify
        data:
          title: "Football Auto-Mute"
          message: "Commercial detection started"

  - alias: "Football Auto-Mute: Stop Detection"
    trigger:
      - platform: state
        entity_id: input_boolean.football_auto_mute_enabled
        to: 'off'
    action:
      - service: notify.notify
        data:
          title: "Football Auto-Mute"
          message: "Commercial detection stopped"

  - alias: "Football Auto-Mute: Commercial Detected"
    trigger:
      - platform: state
        entity_id: sensor.football_auto_mute_status
        to: 'COMMERCIAL'
    action:
      - service: notify.notify
        data:
          title: "🏈 Commercial Break"
          message: "TV has been muted during commercial"
          
  - alias: "Football Auto-Mute: Game Resumed"
    trigger:
      - platform: state
        entity_id: sensor.football_auto_mute_status
        to: 'GAME'
    action:
      - service: notify.notify
        data:
          title: "🏈 Game Resumed"
          message: "TV has been unmuted - game is back!"

script:
  football_auto_mute_toggle:
    alias: Toggle Football Auto-Mute
    sequence:
      - service: input_boolean.toggle
        entity_id: input_boolean.football_auto_mute_enabled
      - service: notify.notify
        data:
          title: "Football Auto-Mute"
          message: >
            System {{ 'enabled' if states('input_boolean.football_auto_mute_enabled') == 'on' else 'disabled' }}
"""
    return config


def main():
    """Test the Home Assistant integration"""
    # Load config
    config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Test integration
    ha = HomeAssistantIntegration(config)
    
    if ha.enabled:
        print("Testing Home Assistant connection...")
        success = ha.create_entities()
        if success:
            print("✅ Successfully created HA entities")
            
            # Test status update
            test_result = {
                'timestamp': datetime.now().isoformat(),
                'detection': 'GAME',
                'tv_muted': False,
                'processing_time': 1.5,
                'context': {'channel': 'ESPN', 'title': 'Test Game'}
            }
            
            if ha.update_status(test_result):
                print("✅ Successfully updated HA status")
            else:
                print("❌ Failed to update HA status")
                
        else:
            print("❌ Failed to create HA entities")
    else:
        print("Home Assistant integration disabled in config")
        print("\nGenerated HA configuration:")
        print(create_ha_configuration())


if __name__ == "__main__":
    main()