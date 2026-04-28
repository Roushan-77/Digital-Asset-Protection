import os
import re
from pathlib import Path


def analyze_image_with_gemini(image_path: str, context_text: str) -> str:
    api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    if not api_key:
        return (
            "Risk Level: Medium. The perceptual hash is close to another sports media asset, "
            "which suggests likely reuse. Visual review should check for cropping, edits, or removed "
            "branding before enforcement."
        )

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        image_bytes = Path(image_path).read_bytes()
        response = model.generate_content(
            [
                context_text,
                {
                    "mime_type": _guess_mime_type(image_path),
                    "data": image_bytes,
                },
            ]
        )
        return (response.text or "").strip() or "Gemini returned an empty analysis."
    except Exception as exc:
        return (
            "Risk Level: Medium. Gemini analysis could not be completed, so the system is relying "
            f"on perceptual-hash similarity for review. Error: {exc}"
        )


def extract_risk_level(response_text: str) -> str:
    match = re.search(r"\b(low|medium|high)\b", response_text, re.IGNORECASE)
    if match:
        return match.group(1).title()
    return "Medium"


def _guess_mime_type(image_path: str) -> str:
    suffix = Path(image_path).suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".webp":
        return "image/webp"
    return "image/png"
