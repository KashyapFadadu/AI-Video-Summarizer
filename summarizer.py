import os
import time
from typing import Dict

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from rouge_score import rouge_scorer

# If a HF token is provided in the environment, log in to increase download
# rate limits and reduce anonymous throttling.
try:
    from huggingface_hub import login as hf_login
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        hf_login(token=hf_token)
except Exception:
    pass


class ModelComparer:
    """Load three summarization models and compare their outputs.

    Models used (pretrained defaults):
    - PEGASUS: `google/pegasus-large`
    - BART: `facebook/bart-large-cnn`
    - T5: `t5-small`
    """

    DEFAULT_MODELS = {
        "DistilBART": "sshleifer/distilbart-cnn-12-6",
        "T5 Small": "t5-small",
        "FLAN-T5 Small": "google/flan-t5-small",
    }

    def __init__(self, max_length: int = 120):
        self.max_length = max_length
        self.cache: Dict[str, Dict] = {}
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")

    def _load(self, model_name: str):
        """Load a model and tokenizer, with caching."""
        if model_name in self.cache:
            return self.cache[model_name]
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        model.to(self.device)
        self.cache[model_name] = {"tokenizer": tokenizer, "model": model}
        return self.cache[model_name]

    def summarize(self, text: str, model_name: str) -> str:

        objs = self._load(model_name)

        tokenizer = objs["tokenizer"]
        model = objs["model"]

        # T5 models need summarize prompt
        if "t5" in model_name.lower():
            text = "summarize: " + text

        model_max = getattr(tokenizer, "model_max_length", 1024)

        if model_max <= 0:
            model_max = 1024

        model_max = min(model_max, 1024)

        batch = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=model_max,
        )

        input_ids = batch["input_ids"].to(self.device)

        attention_mask = batch.get("attention_mask")

        if attention_mask is not None:
            attention_mask = attention_mask.to(self.device)

        generated = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_length=self.max_length,
            min_length=30,
            num_beams=2,
            early_stopping=True,
        )

        summary = tokenizer.decode(
            generated[0],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True,
        )

        if not summary.strip():
            summary = "No summary generated."

        return summary

    def compare_models(self, text: str) -> Dict[str, Dict]:

        results = {}

        for display_name, hf_name in self.DEFAULT_MODELS.items():

            start = time.time()

            try:
                summary = self.summarize(text, hf_name)

            except Exception as e:

                print(f"MODEL FAILED: {display_name}")
                print(str(e))

                summary = f"ERROR: {str(e)}"

            elapsed = time.time() - start

            length = len(summary)

            compression = len(text) / (length + 1)

            results[display_name] = {
                "summary": summary,
                "time": elapsed,
                "length": length,
                "compression": compression,
            }

        return results

    def evaluate_models(self, text: str, results: Dict[str, Dict]) -> Dict[str, Dict]:

        scorer = rouge_scorer.RougeScorer(
            ["rouge1", "rouge2", "rougeL"],
            use_stemmer=True
        )

        eval_results = {}

        for model_name, metrics in results.items():

            summary = metrics["summary"]

            if summary.startswith("ERROR"):
                eval_results[model_name] = {
                    "rouge1": 0,
                    "rouge2": 0,
                    "rougeL": 0,
                }

                continue

            try:

                scores = scorer.score(text, summary)

                eval_results[model_name] = {
                    "rouge1": scores["rouge1"].fmeasure,
                    "rouge2": scores["rouge2"].fmeasure,
                    "rougeL": scores["rougeL"].fmeasure,
                }

            except Exception as e:

                print(f"Evaluation failed: {e}")

                eval_results[model_name] = {
                    "rouge1": 0,
                    "rouge2": 0,
                    "rougeL": 0,
                }

        return eval_results

    def recommend_best_model(self, eval_results: Dict[str, Dict]):
        """Recommend the best model based on average ROUGE score."""
        best_model = None
        best_avg_score = -1
        best_scores = {}

        for model_name, scores in eval_results.items():
            avg_score = (scores["rouge1"] +
                         scores["rouge2"] + scores["rougeL"]) / 3
            if avg_score > best_avg_score:
                best_avg_score = avg_score
                best_model = model_name
                best_scores = scores

        return best_model, best_scores


if __name__ == "__main__":
    mc = ModelComparer(60)
    s = "This is a short test transcript. " * 20
    res = mc.compare_models(s)
    for k, v in res.items():
        print(k, v["time"], v["length"])
