from __future__ import annotations


LANGUAGE_LABELS = {
    "ko": "Korean",
    "ko-jeju": "Jejueo",
}


def build_translation_prompt(source_lang: str, target_lang: str, source_text: str) -> str:
    source_label = LANGUAGE_LABELS[source_lang]
    target_label = LANGUAGE_LABELS[target_lang]
    return (
        "You are a translation system for Korean and Jejueo.\n"
        f"Translate the user text from {source_label} to {target_label}.\n"
        "Return the translation only.\n"
        "Do not add explanations, labels, or notes.\n"
        "Preserve line breaks.\n\n"
        f"Source ({source_label}):\n"
        f"{source_text}\n\n"
        f"Translation ({target_label}):\n"
    )
