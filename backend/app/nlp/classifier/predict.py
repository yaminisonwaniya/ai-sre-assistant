"""NFR requirement classification prediction service with model loading and rule fallback."""
import os
import re
from typing import Tuple
import joblib

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models")
MODEL_PATH = os.path.join(MODELS_DIR, "nfr_classifier.joblib")


class RequirementClassifier:
    """Predicts requirement Type (FUNCTIONAL / NON_FUNCTIONAL) and Subtype (PERFORMANCE, SECURITY, etc.)."""

    def __init__(self):
        self.model_data = None
        if os.path.exists(MODEL_PATH):
            try:
                self.model_data = joblib.load(MODEL_PATH)
            except Exception as e:
                print(f"Warning: Could not load ML model from {MODEL_PATH}: {e}")

    def predict(self, text: str) -> Tuple[str, str, float]:
        """Predict (type, subtype, confidence) for a requirement statement."""
        if self.model_data:
            try:
                bin_clf = self.model_data["binary_pipeline"]
                sub_clf = self.model_data["subtype_pipeline"]

                pred_type = bin_clf.predict([text])[0]
                proba_type = max(bin_clf.predict_proba([text])[0])

                if pred_type == "NON_FUNCTIONAL":
                    pred_subtype = sub_clf.predict([text])[0]
                else:
                    pred_subtype = "AUTHENTICATION" if any(w in text.lower() for w in ["login", "password", "auth"]) else "GENERAL"

                return pred_type, pred_subtype, float(proba_type)
            except Exception:
                pass

        # Heuristic Rule-Based Fallback
        return self._heuristic_predict(text)

    def _heuristic_predict(self, text: str) -> Tuple[str, str, float]:
        """Rule-based heuristic classifier fallback."""
        text_lower = text.lower()

        # Non-functional keywords
        if any(w in text_lower for w in ["seconds", "ms", "latency", "response time", "throughput", "concurrent", "load"]):
            return "NON_FUNCTIONAL", "PERFORMANCE", 0.90
        elif any(w in text_lower for w in ["encrypt", "aes", "tls", "security", "authorization", "permission", "lockout"]):
            return "NON_FUNCTIONAL", "SECURITY", 0.95
        elif any(w in text_lower for w in ["wcag", "accessibility", "user-friendly", "ui", "interface", "screen"]):
            return "NON_FUNCTIONAL", "USABILITY", 0.85
        elif any(w in text_lower for w in ["uptime", "available", "reliability", "crash", "99."]):
            return "NON_FUNCTIONAL", "RELIABILITY", 0.85
        elif any(w in text_lower for w in ["export", "pdf", "email", "send", "log in", "login", "create", "delete", "process"]):
            return "FUNCTIONAL", "AUTHENTICATION" if "login" in text_lower or "email" in text_lower else "GENERAL", 0.80

        return "FUNCTIONAL", "GENERAL", 0.70


classifier_instance = RequirementClassifier()


def predict_requirement_type(text: str) -> Tuple[str, str, float]:
    """Helper function predicting type and subtype for requirement text."""
    return classifier_instance.predict(text)
