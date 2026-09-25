# MP4 to MP3 Converter

A simple and efficient web application built with Python Flask that converts MP4 video files to MP3 audio files.

## Features

- 🎵 Convert MP4, AVI, MOV, MKV, and WMV files to MP3
- 🌐 Web-based interface with drag-and-drop file selection
- 📁 Supports files up to 10GB
- 🔄 Automatic cleanup of temporary files
- 📱 Responsive design for desktop and mobile
- 🔧 Built-in debug and system status page

## Technology Stack

- **Backend**: Python 3.13, Flask
- **Video Processing**: FFmpeg, MoviePy
- **Frontend**: HTML5, CSS3, JavaScript
- **Development**: VS Code

## Installation

### Prerequisites

- Python 3.13
- FFmpeg
- macOS (Darwin arm64) or compatible system

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ejuPhd/mp4-to-mp3_converter.git
   cd mp4-to-mp3_converter

2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

3. Install FFmpeg (macOS)
brew install ffmpeg

4. Install Python dependencies
pip install -r requirements.txt

5. Run the application
python app.py

6. Access the application
Open your browser and navigate to http://localhost:5000

7. Project Structure
mp4-to-mp3_converter/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── LICENSE               # MIT License
├── README.md             # Project documentation
├── uploads/              # Uploaded video files (auto-created)
├── converted/            # Converted MP3 files (auto-created)
├── static/
│   └── style.css         # CSS styles
└── templates/
    ├── index.html        # Main application interface
    └── debug.html        # System status page

8. Usage:
Upload: Click "Choose a video file" or drag and drop your video file
Convert: Click "Convert to MP3" - the conversion will start automatically
Download: Once conversion is complete, click "Download MP3"
Cleanup: Use "Clean Up All Files" to remove temporary files

9. Supported Input Formats
MP4, AVI, MOV, MKV, WMV

10. Output Format
MP3 (192kbps, 44100Hz)

11. API Endpoints
GET / - Main application interface
POST / - File upload and conversion
GET /download/<filename> - Download converted MP3 file
GET /debug - System status and debug information
POST /cleanup - Clean up all uploaded and converted files

12. Configuration
The application can be configured by modifying app.py:
MAX_CONTENT_LENGTH: Maximum file size (default: 10GB)
UPLOAD_FOLDER: Directory for uploaded files
CONVERTED_FOLDER: Directory for converted files
ALLOWED_EXTENSIONS: Supported file formats

13. Common Issues
Conversion fails

Check if FFmpeg is installed: ffmpeg -version
Verify the input file has an audio track
Check the debug page at http://localhost:5000/debug

File upload fails
Ensure file size is under 10GB
Check file format is supported
Verify sufficient disk space

FFmpeg not found
Install FFmpeg: brew install ffmpeg
Ensure FFmpeg is in system PATH

14. Debug Information
Visit http://localhost:8000/debug for system status including:

FFmpeg availability and version
Python version
File system status
Upload and converted file listings

15. The application will run with debug mode enabled on http://localhost:5000

16. Dependencies
See requirements.txt for complete Python package requirements.

17. License
This project is licensed under the MIT License - see the LICENSE file for details.

Copyright (c) 2025 by Dr. Earnest Ujaama for euVisio and Visioideas. Free to use for personal use only.

18. Contributing
Fork the repository
Create a feature branch
Commit your changes
Push to the branch
Create a Pull Request

19. Acknowledgments
Built with Flask web framework
Video processing with FFmpeg and MoviePy
Developed for macOS (Darwin arm64) compatibility

20. Complete requirements.txt
Flask==3.0.0
moviepy==1.0.3
ffmpeg-python==0.2.0
werkzeug==3.0.1
typing-extensions>=4.15.0,<5

21. [gitHub/ejuPhd](https://github.com/ejuPhd/mp4-to-mp3_converter)

Thank you. 
Dr. Earnest J. Ujaama, Saturday, November 8, 2025
eju247@uw.edu