#!/usr/bin/env python3
"""
Keyboard Maestro Helper Script
Handles screenshot capture, context extraction, and orchestration
"""

import json
import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent))

from football_detector import FootballDetector


def get_browser_context():
    """
    Extract context from YouTube TV browser tab
    This would typically be called by Keyboard Maestro with AppleScript
    """
    # This is a placeholder - in practice, Keyboard Maestro will extract this
    # using JavaScript in the browser and pass it as an argument
    return {
        'channel': 'ESPN',
        'title': 'NFL Game',
        'url': 'https://tv.youtube.com/watch',
        'timestamp': datetime.now().isoformat()
    }


def main():
    """
    Main function called by Keyboard Maestro
    Expected arguments:
    1. Screenshot file path
    2. JSON context data (optional)
    """
    
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Screenshot path required'}))
        sys.exit(1)
        
    screenshot_path = sys.argv[1]
    
    # Get context from argument or default
    if len(sys.argv) >= 3:
        try:
            context = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            context = get_browser_context()
    else:
        context = get_browser_context()
    
    # Ensure logs directory exists
    logs_dir = Path(__file__).parent.parent / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    try:
        # Initialize detector
        config_path = str(Path(__file__).parent.parent / 'config' / 'config.yaml')
        detector = FootballDetector(config_path)
        
        # Process the detection
        result = detector.process_detection(screenshot_path, context)
        
        # Output result for Keyboard Maestro
        print(json.dumps(result))
        
        # Clean up temporary screenshot if it's in temp directory
        if '/tmp/' in screenshot_path or '/var/folders/' in screenshot_path:
            try:
                os.remove(screenshot_path)
            except OSError:
                pass  # File might already be cleaned up
                
    except Exception as e:
        error_result = {
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'screenshot_path': screenshot_path,
            'context': context
        }
        print(json.dumps(error_result))
        sys.exit(1)


if __name__ == "__main__":
    main()