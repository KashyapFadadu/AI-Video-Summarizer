import os
import streamlit as st
from summarizer import ModelComparer
from transcriber import transcribe_file, download_and_transcribe_url

# Suppress HuggingFace symlink warning on Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Allow longer downloads from HF hub (seconds)
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "300")

# If you set a Hugging Face token in Streamlit Secrets as `HF_TOKEN`, log in
# to increase download rate limits and avoid anonymous rate limiting.
try:
    from huggingface_hub import login as hf_login
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        hf_login(token=hf_token)
except Exception:
    # huggingface_hub may not be installed in local dev; it's optional
    pass

st.set_page_config(
    page_title="AI Video Summarizer — User Dashboard", layout="wide")

st.title("AI Video Summarizer — Get Your Video Summary")
st.markdown(
    "Upload a video, paste a transcript, or provide a video URL. Get an AI-generated summary instantly."
)

with st.sidebar:
    st.header("Settings")
    # Default to upload option (index=1 selects the second entry)
    source = st.radio(
        "Input type", ["Paste transcript", "Upload video", "Video URL"], index=1)
    max_length = st.slider("Max summary length", 30, 400, 120)
    run_button = st.button("Generate Summary")

if source == "Paste transcript":
    transcript = st.text_area("Paste transcript here", height=300)
    uploaded_file = None
    video_url = None
elif source == "Upload video":
    uploaded_file = st.file_uploader("Upload video file", type=[
                                     "mp4", "mkv", "webm", "avi", "mov"])
    transcript = ""
    video_url = None
else:  # Video URL
    video_url = st.text_input("Enter video URL (YouTube, MP4 link, etc.)")
    uploaded_file = None
    transcript = ""

comparer = ModelComparer(max_length=max_length)

if run_button:
    detected_language = "English"

    if uploaded_file is not None and uploaded_file.size > 0:
        st.info("Transcribing video with Whisper (may take time)...")
        try:
            transcript, detected_language = transcribe_file(uploaded_file)
            st.success(
                f"Transcription complete (detected language: {detected_language})")
        except Exception as e:
            st.error(f"Transcription failed: {e}")
    elif video_url and video_url.strip():
        st.info("Downloading and transcribing video (may take time)...")
        try:
            transcript, detected_language = download_and_transcribe_url(
                video_url)
            st.success(
                f"Transcription complete (detected language: {detected_language})")
        except Exception as e:
            st.error(f"Failed to download/transcribe video: {e}")

    if not transcript or transcript.strip() == "":
        st.error(
            "No transcript provided. Paste text, upload a video, or provide a video URL.")
    else:
        st.subheader("Transcript (English)")
        st.code(transcript[:10000])

        with st.spinner("Generating summary with AI models..."):
            results = comparer.compare_models(transcript)

        # Compute evaluation scores to find the best model
        with st.spinner("Evaluating model quality..."):
            eval_results = comparer.evaluate_models(transcript, results)

        # Find best model
        best_model, best_scores = comparer.recommend_best_model(eval_results)
        best_summary = results[best_model]["summary"]

        # Display only best summary to user (clean, no model name)
        st.markdown("---")
        st.subheader("Your AI-Generated Summary")
        st.code(best_summary)

        # Download button
        st.download_button(
            "📥 Download Summary",
            best_summary,
            file_name="summary.txt"
        )

        # Store for admin page
        st.session_state.last_transcript = transcript
        st.session_state.last_results = results
        st.session_state.eval_results = eval_results

        st.markdown("---")
        st.info(
            "💡 **Admin?** Visit the **Admin** page (in sidebar) to view all model comparisons and metrics.")
