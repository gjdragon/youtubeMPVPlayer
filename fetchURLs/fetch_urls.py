import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, 
                             QPushButton, QVBoxLayout, QMessageBox)
from pytube import Playlist

class YouTubePlaylistURLFetcher(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set up the main window
        self.setWindowTitle('YouTube Playlist URL Fetcher')
        self.setGeometry(100, 100, 500, 200)

        # Create layout
        layout = QVBoxLayout()

        # Playlist URL Label and Input
        self.url_label = QLabel('Enter YouTube Playlist URL:')
        layout.addWidget(self.url_label)

        self.url_input = QLineEdit()
        layout.addWidget(self.url_input)

        # Save Button
        self.save_button = QPushButton('Save URLs')
        self.save_button.clicked.connect(self.save_urls)
        layout.addWidget(self.save_button)

        # Set the layout
        self.setLayout(layout)

    def save_urls(self):
        # Get the playlist URL from input
        playlist_url = self.url_input.text().strip()

        try:
            # Fetch the playlist
            playlist = Playlist(playlist_url)
            
            # Get video URLs
            video_urls = playlist.video_urls

            # Ensure save directory exists
            save_dir = r'C:\play_url\urls'
            os.makedirs(save_dir, exist_ok=True)

            # Clean playlist title for filename
            clean_title = ''.join(c if c.isalnum() or c in [' ', '-', '_'] else '' for c in playlist.title)
            clean_title = clean_title.replace(' ', '-').lower()

            # Create filename
            filename = f'urls_{clean_title}.txt'
            filepath = os.path.join(save_dir, filename)

            # Save URLs to file
            with open(filepath, 'w', encoding='utf-8') as f:
                for url in video_urls:
                    f.write(url + '\n')

            # Show success message
            QMessageBox.information(
                self, 
                'Success', 
                f'Successfully saved {len(video_urls)} URLs to {filename}'
            )

        except Exception as e:
            # Show error message if something goes wrong
            QMessageBox.critical(
                self, 
                'Error', 
                f'An error occurred: {str(e)}'
            )

def main():
    app = QApplication(sys.argv)
    fetcher = YouTubePlaylistURLFetcher()
    fetcher.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()