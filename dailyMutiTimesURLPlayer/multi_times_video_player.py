import os
import sys
import time
import random
import logging
import json
import schedule
import subprocess
from datetime import datetime
from ctypes import windll, c_int, byref

class MultiTimesVideoPlayer:
    # Windows Monitor Power Constants
    HWND_BROADCAST = 0xFFFF
    WM_SYSCOMMAND = 0x0112
    SC_MONITORPOWER = 0xF170
    MONITOR_ON = -1
    MONITOR_OFF = 2

    def __init__(self, 
                 config_file=r'C:\play_url\config.json', 
                 url_file=r'C:\play_url\url.txt', 
                 mpv_path=r'C:\tools\mpv\mpv.exe'):
        self.config_file = config_file
        self.url_file = url_file
        self.mpv_path = mpv_path
        
        # Create logs directory if it doesn't exist
        logs_dir = r'C:\play_url\logs'
        os.makedirs(logs_dir, exist_ok=True)
        
        # Setup logging
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(logs_dir, f'multi_video_player_{timestamp}.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Load configuration
        self.load_config()

    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            
            # Validate config
            for schedule_item in self.config.get('schedules', []):
                if not all(key in schedule_item for key in ['time', 'duration']):
                    raise ValueError("Invalid schedule configuration")
            
            self.logger.info(f"Loaded configuration from {self.config_file}")
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            sys.exit(1)

    def wake_monitor(self):
        """Wake up the monitor using Windows API"""
        try:
            # Simulate mouse movement
            windll.user32.mouse_event(0x0001, 0, 0, 0, 0)
            
            # Send monitor power on command
            windll.user32.PostMessageW(
                self.HWND_BROADCAST, 
                self.WM_SYSCOMMAND,
                self.SC_MONITORPOWER, 
                self.MONITOR_ON
            )
            
            # Additional method to ensure monitor wakes up
            for _ in range(3):
                windll.user32.mouse_event(0x0001, 1, 0, 0, 0)
                time.sleep(0.1)
                windll.user32.mouse_event(0x0001, -1, 0, 0, 0)
                time.sleep(0.1)
            
            self.logger.info("Monitor wake attempt completed")
        except Exception as e:
            self.logger.error(f"Error waking monitor: {e}")

    def read_urls(self):
        """Read URLs from file"""
        try:
            with open(self.url_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            if not urls:
                raise ValueError(f"No URLs found in {self.url_file}")
            
            return urls
        except Exception as e:
            self.logger.error(f"Error reading URL file: {e}")
            sys.exit(1)

    def play_videos(self, duration):
        """Play random videos for specified duration"""
        target_duration_sec = duration * 60
        total_played_sec = 0
        urls = self.read_urls()

        # Wake monitor before starting
        self.wake_monitor()

        while total_played_sec < target_duration_sec:
            # Calculate remaining time
            remaining_sec = target_duration_sec - total_played_sec
            self.logger.info(f"Remaining playback time: {remaining_sec} seconds")

            # Select random URL
            url = random.choice(urls)
            self.logger.info(f"Selected URL: {url}")

            # Wake monitor before each video
            self.wake_monitor()

            # Play video
            start_time = time.time()
            try:
                subprocess.run([
                    self.mpv_path, 
                    '--really-quiet', 
                    f'--end={remaining_sec}', 
                    '--fullscreen', 
                    url
                ], check=True)
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Video playback error: {e}")
                break

            # Calculate actual played duration
            actual_duration = time.time() - start_time
            total_played_sec += int(actual_duration)
            self.logger.info(f"Completed playback. Actual duration: {int(actual_duration)} seconds. Total played: {total_played_sec} seconds")

        self.logger.info(f"Target duration reached. Total playback time: {total_played_sec} seconds")

    def schedule_playback(self):
        """Schedule video playback based on configuration"""
        for schedule_item in self.config.get('schedules', []):
            play_time = schedule_item['time']
            duration = schedule_item['duration']
            
            # Create a lambda function to pass duration
            play_func = lambda d=duration: self.play_videos(d)
            
            # Schedule the playback
            schedule.every().day.at(play_time).do(play_func)
            self.logger.info(f"Scheduled video play at {play_time} for {duration} minutes")

        # Keep the script running
        self.logger.info("Scheduler started. Waiting for scheduled times.")
        while True:
            schedule.run_pending()
            time.sleep(55)

def main():
    # Allow customization via command-line arguments
    config_file = sys.argv[1] if len(sys.argv) > 1 else r'C:\play_url\config.json'
    url_file = sys.argv[2] if len(sys.argv) > 2 else r'C:\play_url\url.txt'
    mpv_path = sys.argv[3] if len(sys.argv) > 3 else r'C:\tools\mpv\mpv.exe'

    player = MultiTimesVideoPlayer(
        config_file=config_file, 
        url_file=url_file, 
        mpv_path=mpv_path
    )
    player.schedule_playback()

if __name__ == "__main__":
    main()