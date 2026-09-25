import os
import logging
import traceback
import shutil
import subprocess
import sys
from flask import Flask, request, render_template, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configuration - Updated to 10GB
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 * 1024  # 10GB
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'mkv', 'wmv'}

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)


def get_ffmpeg_path() -> str:
    """Get FFmpeg path - prefer the one in virtual environment"""
    venv_ffmpeg = os.path.join(os.path.dirname(sys.executable), 'ffmpeg')
    return venv_ffmpeg if os.path.exists(venv_ffmpeg) else 'ffmpeg'


def check_ffmpeg() -> tuple[bool, str]:
    """Check if FFmpeg is available and return status with info"""
    ffmpeg_path = get_ffmpeg_path()
    try:
        result = subprocess.run(
            [ffmpeg_path, '-version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split(
                '\n')[0] if result.stdout else "Version info unavailable"
            return True, f"✅ FFmpeg found at: {ffmpeg_path}\n{version_line}"
        else:
            return False, f"❌ FFmpeg found but returned error: {result.stderr}"
    except Exception as e:
        return False, f"❌ FFmpeg check failed: {str(e)}"


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def cleanup_old_files():
    import time
    current_time = time.time()
    for folder in [app.config['UPLOAD_FOLDER'], app.config['CONVERTED_FOLDER']]:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.getmtime(file_path) < current_time - 3600:
                    os.remove(file_path)
            except Exception:
                pass


def convert_with_ffmpeg(input_path: str, output_path: str) -> bool:
    """Convert using direct FFmpeg command"""
    ffmpeg_path = get_ffmpeg_path()
    try:
        cmd = [
            ffmpeg_path, '-i', input_path, '-vn',
            '-acodec', 'libmp3lame', '-ab', '192k',
            '-ar', '44100', '-y', output_path
        ]

        logger.info(f"Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            return os.path.exists(output_path) and os.path.getsize(output_path) > 0
        else:
            logger.error(f"FFmpeg error: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"FFmpeg conversion failed: {e}")
        return False


def convert_with_moviepy(input_path: str, output_path: str) -> bool:
    """Fallback conversion using moviepy"""
    video = audio = None
    try:
        video = VideoFileClip(input_path)
        audio = video.audio
        if not audio:
            return False
        audio.write_audiofile(output_path, verbose=False,
                              logger=None, bitrate="192k")
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception as e:
        logger.error(f"Moviepy conversion failed: {e}")
        return False
    finally:
        for obj in [audio, video]:
            if obj:
                try:
                    obj.close()
                except:
                    pass


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)

        file = request.files['file']
        if not file or not file.filename:
            flash('No file selected', 'error')
            return redirect(request.url)

        if allowed_file(file.filename):
            # Initialize variables at the start
            input_path = None
            output_path = None
            success = False  # Initialize success here

            try:
                cleanup_old_files()
                filename = secure_filename(file.filename)
                input_path = os.path.join(
                    app.config['UPLOAD_FOLDER'], filename)
                file.save(input_path)

                if not os.path.exists(input_path):
                    flash('Error saving file', 'error')
                    return redirect(request.url)

                base_name = os.path.splitext(filename)[0]
                output_filename = f"{base_name}.mp3"
                output_path = os.path.join(
                    app.config['CONVERTED_FOLDER'], output_filename)

                flash('Conversion starting...', 'info')

                # Try FFmpeg first, then moviepy
                success = convert_with_ffmpeg(input_path, output_path)
                if not success:
                    logger.info("FFmpeg failed, trying moviepy...")
                    success = convert_with_moviepy(input_path, output_path)

                if success:
                    flash('✅ Conversion successful!', 'success')
                    return render_template('index.html', converted_file=output_filename)
                else:
                    flash(
                        '❌ Conversion failed. Check file format and audio track.', 'error')

            except Exception as e:
                logger.error(f"Unexpected error: {traceback.format_exc()}")
                flash(f'Server error: {str(e)}', 'error')
                success = False  # Ensure success is False on exception

            finally:
                # Clean up input file only if conversion failed
                if not success:
                    if input_path and os.path.exists(input_path):
                        try:
                            os.remove(input_path)
                            logger.info(f"Cleaned up input file: {input_path}")
                        except Exception as e:
                            logger.error(f"Error cleaning up input file: {e}")
        else:
            flash('Invalid file type', 'error')

    return render_template('index.html')


@app.route('/debug')
def debug_info():
    """Debug page to check system status"""
    ffmpeg_available, ffmpeg_info = check_ffmpeg()
    info = {
        'ffmpeg_status': ffmpeg_info,
        'upload_files': os.listdir(app.config['UPLOAD_FOLDER']),
        'converted_files': os.listdir(app.config['CONVERTED_FOLDER']),
        'python_version': sys.version,
        'ffmpeg_path': get_ffmpeg_path(),
        'max_file_size': '10GB'
    }
    return f"""
    <h1>System Debug Info</h1>
    <pre>FFmpeg Status: {info['ffmpeg_status']}</pre>
    <pre>FFmpeg Path: {info['ffmpeg_path']}</pre>
    <pre>Python: {info['python_version']}</pre>
    <pre>Max File Size: {info['max_file_size']}</pre>
    <pre>Upload Files: {info['upload_files']}</pre>
    <pre>Converted Files: {info['converted_files']}</pre>
    <a href="/">← Back</a>
    """


@app.route('/download/<filename>')
def download_file(filename: str):
    try:
        file_path = os.path.join(
            app.config['CONVERTED_FOLDER'], secure_filename(filename))
        return send_file(file_path, as_attachment=True) if os.path.exists(file_path) else redirect('/')
    except Exception:
        return redirect('/')


@app.route('/cleanup', methods=['POST'])
def cleanup_files():
    try:
        for folder in [app.config['UPLOAD_FOLDER'], app.config['CONVERTED_FOLDER']]:
            for filename in os.listdir(folder):
                os.remove(os.path.join(folder, filename))
        flash('All files cleaned up', 'success')
    except Exception:
        flash('Cleanup error', 'error')
    return redirect('/')


@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum size is 10GB.', 'error')
    return redirect(url_for('index'))


if __name__ == '__main__':
    cleanup_old_files()
    ffmpeg_available, ffmpeg_info = check_ffmpeg()

    print("=" * 50)
    print("🚀 MP4 to MP3 Converter Starting...")
    print(ffmpeg_info)
    print(f"📁 Uploads: {app.config['UPLOAD_FOLDER']}")
    print(f"📁 Converted: {app.config['CONVERTED_FOLDER']}")
    print(f"📏 Max File Size: 10GB")
    print("🌐 Server: http://localhost:8000")
    print("🔧 Debug: http://localhost:8000/debug")
    print("=" * 50)

    app.run(debug=True, host='0.0.0.0', port=8000)
