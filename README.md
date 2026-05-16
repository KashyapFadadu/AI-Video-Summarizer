# 🎬 AI Video Summarizer

An intelligent video summarization tool powered by cutting-edge AI models. Upload, transcribe, and summarize videos instantly using state-of-the-art NLP models.

## ✨ Features

- **🎥 Multiple Input Methods**
  - Upload video files (MP4, MKV, WebM, AVI, MOV)
  - Paste transcripts directly
  - Provide video URLs (YouTube, direct links)

- **🤖 AI-Powered Summarization**
  - **PEGASUS**: Google's powerful pre-trained summarizer
  - **BART**: Facebook's sequence-to-sequence model
  - **T5**: Unified text-to-text transformer
  - Compare summaries from all three models simultaneously

- **🌍 Multi-Language Support**
  - Automatic language detection
  - Supports 99+ languages
  - Transcription with Whisper AI

- **⚙️ Customizable Parameters**
  - Adjustable summary length (30-400 tokens)
  - Quality metrics (ROUGE scores)
  - Real-time processing feedback

- **📊 Admin Dashboard**
  - Monitor app usage
  - View statistics and analytics
  - System information

## 🚀 Live Demo

👉 **[Try the live app here!](https://your-app-url.streamlit.app)**

## 📋 Requirements

- Python 3.8+
- 4GB+ RAM (for model loading)
- FFmpeg installed (for video processing)

## 💻 Installation

### Local Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/AI-Video-Summarizer.git
   cd AI-Video-Summarizer
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg**
   - **Windows**: `choco install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt-get install ffmpeg`

5. **Run the application**

   ```bash
   streamlit run app.py
   ```

   The app will open at `http://localhost:8501`

## 📁 Project Structure

```
AI-Video-Summarizer/
├── app.py                 # Main Streamlit application
├── summarizer.py          # Summarization models (PEGASUS, BART, T5)
├── transcriber.py         # Video transcription with Whisper
├── pages/
│   └── 1_Admin.py        # Admin dashboard
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml       # Streamlit configuration
└── README.md             # This file
```

## 🔧 Usage Guide

### Method 1: Upload Video

1. Select "Upload video" from the sidebar
2. Choose your video file
3. Adjust summary length as needed
4. Click "Generate Summary"
5. View summaries from all three AI models

### Method 2: Paste Transcript

1. Select "Paste transcript" from the sidebar
2. Paste your transcript text
3. Customize summary parameters
4. Click "Generate Summary"

### Method 3: Video URL

1. Select "Video URL" from the sidebar
2. Enter a YouTube or direct video link
3. Set your preferences
4. Click "Generate Summary"

## 🧠 AI Models Used

| Model       | Provider      | Strengths                               |
| ----------- | ------------- | --------------------------------------- |
| **PEGASUS** | Google        | Abstractive summarization, high quality |
| **BART**    | Facebook/Meta | Balanced speed and quality              |
| **T5**      | Google        | Flexible, good for custom tasks         |

## 📊 How It Works

```
Video Input
    ↓
[FFmpeg] → Extract Audio
    ↓
[Whisper] → Transcription + Language Detection
    ↓
[Preprocessing] → Clean & Prepare Text
    ↓
[AI Models] → Generate Summaries (PEGASUS, BART, T5)
    ↓
[ROUGE Metrics] → Evaluate Quality
    ↓
Display Results
```

## 📝 Configuration

### Adjust Summary Length

Edit in sidebar during app usage (30-400 tokens)

### Change Default Models

Modify `summarizer.py`:

```python
DEFAULT_MODELS = {
    "PEGASUS": "google/pegasus-large",
    "BART": "facebook/bart-large-cnn",
    "T5": "t5-small",
}
```

## 🐛 Troubleshooting

### FFmpeg Not Found

```bash
# Windows
pip install python-ffmpeg

# macOS
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg
```

### Out of Memory

- Use a smaller video
- Reduce summary length
- Close other applications

### Slow Summarization

- First run downloads models (normal, takes time)
- Reduce max summary length
- Use shorter videos for testing

### Whisper Checksum Error

The app handles this automatically by clearing cache and retrying.

## 🎓 Learning Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [ROUGE Metrics](https://github.com/google-research/google-research/tree/master/rouge)

---

**Made with ❤️ by Your Name**

⭐ If you found this helpful, please consider starring the repository!
