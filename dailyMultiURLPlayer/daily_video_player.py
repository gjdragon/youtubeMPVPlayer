import os
import sys
import time
import random
import logging
import schedule
import subprocess
from datetime import datetime
from ctypes import windll, c_int, byref

class DailyVideoPlayer:
    # Windows Monitor Power Constants
    HWND_BROADCAST = 0xFFFF
    WM_SYSCOMMAND = 0x0112
    SC_MONITORPOWER = 0xF170
    MONITOR_ON = -1
    MONITOR_OFF = 2

    def __init__(self, 
                 url_file=r'C:\play_url\url.txt', 
                 mpv_path=r'C:\tools\mpv\mpv.exe', 
                 daily_duration=10, 
                 start_time='09:21'):
        self.url_file = url_file
        self.mpv_path = mpv_path
        self.daily_duration = daily_duration
        self.start_time = start_time
        
        # Create logs directory if it doesn't exist
        logs_dir = r'C:\play_url\logs'
        os.makedirs(logs_dir, exist_ok=True)
        
        # Setup logging
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(logs_dir, f'daily_video_player_{timestamp}.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

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
                # Move mouse slightly
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

    def play_daily_videos(self):
        """Play random videos for daily duration"""
        target_duration_sec = self.daily_duration * 60
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

        self.logger.info(f"Daily target duration reached. Total playback time: {total_played_sec} seconds")

    def run_daily(self):
        """Schedule daily video playback"""
        schedule.every().day.at(self.start_time).do(self.play_daily_videos)
        
        self.logger.info(f"Scheduler started. Will play videos daily at {self.start_time}")
        
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(55)

def main():
    # Allow customization via command-line arguments
    url_file = sys.argv[1] if len(sys.argv) > 1 else r'C:\play_url\url.txt'
    mpv_path = sys.argv[2] if len(sys.argv) > 2 else r'C:\tools\mpv\mpv.exe'
    daily_duration = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    start_time = sys.argv[4] if len(sys.argv) > 4 else '20:26'

    player = DailyVideoPlayer(
        url_file=url_file, 
        mpv_path=mpv_path, 
        daily_duration=daily_duration, 
        start_time=start_time
    )
    player.run_daily()

if __name__ == "__main__":
    main()