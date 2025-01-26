import tkinter as tk
from tkinter import messagebox
import subprocess
import pyperclip

class YouTubePlayerApp:
    def __init__(self, mpv_path=r'C:\tools\mpv\mpv.exe'):
        self.mpv_path = mpv_path
        self.process = None
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("YouTube URL Player")
        self.root.geometry("400x200")
        
        # URL Input
        self.url_label = tk.Label(self.root, text="YouTube URL:")
        self.url_label.pack(pady=5)
        
        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.pack(pady=5)
        
        # Button Frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # Paste Button
        self.paste_btn = tk.Button(button_frame, text="Paste", command=self.paste_url)
        self.paste_btn.pack(side=tk.LEFT, padx=5)
        
        # Play Button
        self.play_btn = tk.Button(button_frame, text="Play", command=self.play_video)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        
        # Stop Button
        self.stop_btn = tk.Button(button_frame, text="Stop", command=self.stop_video, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
    def paste_url(self):
        """Paste clipboard content into URL entry"""
        clipboard_text = pyperclip.paste()
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, clipboard_text)
        
    def play_video(self):
        """Play video using MPV"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return
        
        try:
            # Stop any existing video
            self.stop_video()
            
            # Start new video
            self.process = subprocess.Popen([
                self.mpv_path, 
                '--fullscreen', 
                url
            ])
            
            # Update button states
            self.play_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Playback Error", str(e))
        
    def stop_video(self):
        """Stop current video playback"""
        if self.process:
            try:
                self.process.terminate()
                self.process = None
            except Exception:
                pass
            
        # Reset button states
        self.play_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    app = YouTubePlayerApp()
    app.run()

if __name__ == "__main__":
    main()