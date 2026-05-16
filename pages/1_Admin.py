import streamlit as st
from summarizer import ModelComparer
import pandas as pd

st.set_page_config(
    page_title="AI Video Summarizer — Admin Dashboard", layout="wide")

st.title("Admin Dashboard — Model Metrics & Analysis")
st.markdown(
    "View detailed model performance metrics, ROUGE scores, and recommendations."
)

# Check if results are available from the main app
if "last_results" not in st.session_state or "last_transcript" not in st.session_state:
    st.warning(
        "⚠️ No summarization data available. Please run a summarization on the main **User** page first."
    )
else:
    results = st.session_state.last_results
    transcript = st.session_state.last_transcript

    comparer = ModelComparer()

    st.markdown("---")
    st.subheader("📊 Generating Evaluation Metrics...")
    with st.spinner("Computing ROUGE scores..."):
        eval_results = comparer.evaluate_models(transcript, results)

    # Display detailed analysis table first
    st.markdown("---")
    st.subheader("📈 Detailed Analysis")

    analysis_data = []
    for model_name in results.keys():
        model_display = model_name.split(" (")[0]  # Get display name
        metrics = results[model_name]
        evals = eval_results[model_name]
        avg_rouge = (evals['rouge1'] + evals['rouge2'] + evals['rougeL']) / 3
        analysis_data.append({
            "Model": model_display,
            "Time (s)": round(metrics['time'], 2),
            "Length (chars)": metrics['length'],
            "Compression": round(metrics['compression'], 2),
            "ROUGE-1": round(evals['rouge1'], 3),
            "ROUGE-2": round(evals['rouge2'], 3),
            "ROUGE-L": round(evals['rougeL'], 3),
            "Avg ROUGE": round(avg_rouge, 3),
        })

    df = pd.DataFrame(analysis_data)
    st.dataframe(df, use_container_width=True)

    # Recommendation panel
    st.markdown("---")
    st.subheader("🎯 Model Recommendation")
    best_model, best_scores = comparer.recommend_best_model(eval_results)
    col1, col2, col3 = st.columns(3)
    col1.metric("🏆 Best Model", best_model.split(" (")[0])
    col2.metric("Best ROUGE-1", f"{best_scores['rouge1']:.3f}")
    col3.metric("Best ROUGE-L", f"{best_scores['rougeL']:.3f}")
    st.success(
        f"✅ **{best_model}** achieves the highest quality score and is recommended for deployment."
    )

    # Detailed summaries section
    st.markdown("---")
    st.subheader("📄 Detailed Summaries")

    cols = st.columns(len(results))
    for (model_name, metrics), col in zip(results.items(), cols):
        col.markdown(f"### **{model_name}**")
        col.markdown("**Summary:**")
        col.code(metrics['summary'])
