import tempfile
import os
import shutil
import urllib.request
import subprocess
import warnings

# Hide Whisper FP16 CPU warning (Whisper will automatically use FP32 on CPU).
warnings.filterwarnings(
    "ignore",
    message="FP16 is not supported on CPU",
)

# Try to locate ffmpeg via imageio-ffmpeg and make sure it's on PATH.
ffmpeg_exe = None
try:
    import imageio_ffmpeg as _imageio_ffmpeg

    ffmpeg_exe = _imageio_ffmpeg.get_ffmpeg_exe()

    if ffmpeg_exe:
        os.environ["FFMPEG_BINARY"] = ffmpeg_exe
        ffmpeg_dir = os.path.dirname(ffmpeg_exe)
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
        print("FFmpeg found:", ffmpeg_exe)
except Exception as e:
    ffmpeg_exe = None
    print("FFmpeg setup failed:", e)

# Fallback: create /tmp/ffmpeg symlink or copy if possible and prepend /tmp to PATH
try:
    if ffmpeg_exe:
        tmp_ffmpeg = "/tmp/ffmpeg"
        if not os.path.exists(tmp_ffmpeg):
            try:
                os.symlink(ffmpeg_exe, tmp_ffmpeg)
            except Exception:
                shutil.copy(ffmpeg_exe, tmp_ffmpeg)
                os.chmod(tmp_ffmpeg, 0o755)
        os.environ["PATH"] = "/tmp" + os.pathsep + os.environ.get("PATH", "")
except Exception as e:
    print("ffmpeg fallback failed:", e)

# Runtime test for ffmpeg command
try:
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        first_line = result.stdout.splitlines()[0] if result.stdout else "(no output)"
        print("FFmpeg test output:", first_line)
    else:
        print("FFmpeg returned non-zero code:", result.returncode)
except Exception as e:
    print("FFmpeg test failed:", e)


def _save_upload_to_temp(uploaded_file):
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        return tmp.name


def transcribe_file(uploaded_file) -> tuple[str, str]:
    """Transcribe an uploaded video file using OpenAI Whisper with auto language detection.

    Returns: (english_transcript, detected_language_name)
    """
    try:
        import whisper
    except Exception as e:
        raise RuntimeError(
            "`whisper` not installed. Install with `pip install -U openai-whisper` and ensure ffmpeg is installed.") from e

    tmp_path = _save_upload_to_temp(uploaded_file)
    try:
        try:
            model = whisper.load_model("base")
        except RuntimeError as e:
            if "SHA256 checksum" in str(e):
                cache_dir = os.path.expanduser("~/.cache/whisper")
                if os.path.exists(cache_dir):
                    shutil.rmtree(cache_dir)
                model = whisper.load_model("base")
            else:
                raise

        audio = whisper.load_audio(tmp_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        _, probs = model.detect_language(mel)
        detected_lang_code = max(probs, key=probs.get)

        lang_map = {"en": "English", "hi": "Hindi", "gu": "Gujarati"}
        detected_language = lang_map.get(detected_lang_code, "English")

        try:
            result = model.transcribe(tmp_path, language=detected_lang_code, task="translate")
            english_text = result.get("text", "")
        except Exception:
            english_text = ""

        return english_text, detected_language
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def detect_language(video_path: str) -> str:
    """Detect the language of audio in a video file using Whisper.

    Returns the language name or defaults to 'English'.
    """
    try:
        import whisper
    except Exception as e:
        raise RuntimeError("`whisper` not installed.") from e

    try:
        model = whisper.load_model("base")
        audio = whisper.load_audio(video_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        _, probs = model.detect_language(mel)
        detected_lang_code = max(probs, key=probs.get)

        lang_map = {"en": "English", "hi": "Hindi", "gu": "Gujarati"}
        return lang_map.get(detected_lang_code, "English")
    except Exception:
        return "English"


def download_and_transcribe_url(video_url: str) -> tuple[str, str]:
    """Download a video from URL, auto-detect language, and transcribe to English.

    Returns: (english_transcript, detected_language_name)
    """
    try:
        import whisper
    except Exception as e:
        raise RuntimeError(
            "`whisper` not installed. Install with `pip install -U openai-whisper` and ensure ffmpeg is installed.") from e

    tmp_video = None
    try:
        is_youtube = "youtube.com" in video_url or "youtu.be" in video_url

        if is_youtube:
            try:
                import yt_dlp
            except ImportError:
                raise RuntimeError(
                    "YouTube URL detected but `yt-dlp` not installed. Install with `pip install yt-dlp`")
            ydl_opts = {
                'format': 'best[ext=mp4]',
                'quiet': True,
                'no_warnings': True,
                'outtmpl': os.path.join(tempfile.gettempdir(), '%(id)s.%(ext)s'),
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                tmp_video = ydl.prepare_filename(info)
        else:
            tmp_video = os.path.join(tempfile.gettempdir(), 'downloaded_video.mp4')
            urllib.request.urlretrieve(video_url, tmp_video)

        try:
            model = whisper.load_model("base")
        except RuntimeError as e:
            if "SHA256 checksum" in str(e):
                cache_dir = os.path.expanduser("~/.cache/whisper")
                if os.path.exists(cache_dir):
                    shutil.rmtree(cache_dir)
                model = whisper.load_model("base")
            else:
                raise

        audio = whisper.load_audio(tmp_video)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        _, probs = model.detect_language(mel)
        detected_lang_code = max(probs, key=probs.get)

        lang_map = {"en": "English", "hi": "Hindi", "gu": "Gujarati"}
        detected_language = lang_map.get(detected_lang_code, "English")

        try:
            result = model.transcribe(tmp_video, language=detected_lang_code, task="translate")
            english_text = result.get("text", "")
        except Exception:
            english_text = ""

        return english_text, detected_language

    finally:
        if tmp_video and os.path.exists(tmp_video):
            try:
                os.unlink(tmp_video)
            except Exception:
                pass
