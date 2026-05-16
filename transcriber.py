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

# If `imageio-ffmpeg` is available (bundles an ffmpeg binary), make sure Whisper
# can find the ffmpeg executable on environments like Streamlit Cloud where
# system `ffmpeg` may not be installed.
try:
    import imageio_ffmpeg as _imageio_ffmpeg

    ffmpeg_exe = _imageio_ffmpeg.get_ffmpeg_exe()

    if ffmpeg_exe:
        os.environ["FFMPEG_BINARY"] = ffmpeg_exe

        ffmpeg_dir = os.path.dirname(ffmpeg_exe)

        # Prepend ffmpeg dir so the `ffmpeg` command is found first
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")

        print("FFmpeg found:", ffmpeg_exe)

except Exception as e:
    ffmpeg_exe = None
    print("FFmpeg setup failed:", e)

# Fallback: if we found an ffmpeg executable via imageio-ffmpeg, create a
# stable `/tmp/ffmpeg` entry (symlink or copy) and prepend `/tmp` to PATH so
# subprocess lookups for `ffmpeg` succeed. This helps on environments where
# PATH changes may not be picked up by lower-level libs.
try:
            model = whisper.load_model("base")
        tmp_ffmpeg = "/tmp/ffmpeg"
        if not os.path.exists(tmp_ffmpeg):
            try:
                os.symlink(ffmpeg_exe, tmp_ffmpeg)
            except Exception:
                shutil.copy(ffmpeg_exe, tmp_ffmpeg)
                os.chmod(tmp_ffmpeg, 0o755)
        # Prepend /tmp so it's found first
        os.environ["PATH"] = "/tmp" + os.pathsep + os.environ.get("PATH", "")
except Exception as e:
    print("ffmpeg fallback failed:", e)

# Quick runtime test to ensure `ffmpeg` is callable as a command in the
# deployed environment. This prints a short version string to the Streamlit
# logs which helps debugging.
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

    The transcribed text will be translated to English (via Whisper's task='translate').
    Supports English, Hindi, and Gujarati audio.

    Notes:
    - Requires `whisper` (OpenAI) package and `ffmpeg` installed and available on PATH.
    - If these are not installed, the function raises an informative error.
    """
    try:
        import whisper
    except Exception as e:
        model = whisper.load_model("base")
            "`whisper` not installed. Install with `pip install -U openai-whisper` and ensure ffmpeg is installed.") from e

    tmp_path = _save_upload_to_temp(uploaded_file)
    try:
        # Try loading the model; if checksum fails, clear cache and retry
        try:
            model = whisper.load_model("small")
        except RuntimeError as e:
            if "SHA256 checksum" in str(e):
                # Clear the corrupted cache and retry
                import shutil
                cache_dir = os.path.expanduser("~/.cache/whisper")
                if os.path.exists(cache_dir):
                    shutil.rmtree(cache_dir)
                model = whisper.load_model("small")
            else:
                raise

        # Auto-detect language
        audio = whisper.load_audio(tmp_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        _, probs = model.detect_language(mel)
        detected_lang_code = max(probs, key=probs.get)

        lang_map = {"en": "English", "hi": "Hindi", "gu": "Gujarati"}
        detected_language = lang_map.get(detected_lang_code, "English")

        # Produce English translation (task='translate' always outputs English)
        try:
            result = model.transcribe(
                tmp_path, language=detected_lang_code, task="translate")
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

    Returns the language name ('English', 'Hindi', 'Gujarati', etc.) or defaults to 'English'.
    """
    try:
        import whisper
    except Exception as e:
        raise RuntimeError("`whisper` not installed.") from e

    try:
        model = whisper.load_model("small")
        # Use detect_language to identify the language
        audio = whisper.load_audio(video_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        _, probs = model.detect_language(mel)
        detected_lang_code = max(probs, key=probs.get)

            model = whisper.load_model("base")
        lang_map = {
            "en": "English",
            "hi": "Hindi",
            "gu": "Gujarati",
        }
        return lang_map.get(detected_lang_code, "English")
    except Exception:
        return "English"


def download_and_transcribe_url(video_url: str) -> tuple[str, str]:
    """Download a video from URL, auto-detect language, and transcribe to English.

    Supports direct MP4 links, YouTube URLs (requires yt-dlp), and other video URLs.

    Returns: (english_transcript, detected_language_name)

    Notes:
    - For YouTube URLs, requires `yt-dlp` package: pip install yt-dlp
    - Requires `ffmpeg` installed and available on PATH.
    """
    try:
        import whisper
    except Exception as e:
        raise RuntimeError(
            "`whisper` not installed. Install with `pip install -U openai-whisper` and ensure ffmpeg is installed.") from e

    tmp_video = None
    try:
        # Determine if URL is YouTube
        is_youtube = "youtube.com" in video_url or "youtu.be" in video_url

        if is_youtube:
            try:
                import yt_dlp
            except ImportError:
                raise RuntimeError(
                    "YouTube URL detected but `yt-dlp` not installed. Install with `pip install yt-dlp`")
            # Download YouTube video
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
            # Direct download of MP4/video link
            tmp_video = os.path.join(
                tempfile.gettempdir(), 'downloaded_video.mp4')
            urllib.request.urlretrieve(video_url, tmp_video)

        # Now transcribe the downloaded video
        try:
            model = whisper.load_model("small")
        except RuntimeError as e:
            if "SHA256 checksum" in str(e):
                cache_dir = os.path.expanduser("~/.cache/whisper")
                if os.path.exists(cache_dir):
                    shutil.rmtree(cache_dir)
                model = whisper.load_model("small")
            else:
                raise

        # Auto-detect language
        audio = whisper.load_audio(tmp_video)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        _, probs = model.detect_language(mel)
        detected_lang_code = max(probs, key=probs.get)

        lang_map = {"en": "English", "hi": "Hindi", "gu": "Gujarati"}
        detected_language = lang_map.get(detected_lang_code, "English")

        # Produce English translation
        try:
            result = model.transcribe(
                tmp_video, language=detected_lang_code, task="translate")
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
