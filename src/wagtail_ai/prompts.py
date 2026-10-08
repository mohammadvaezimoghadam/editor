from collections.abc import Sequence
from typing import NotRequired, Required, TypedDict


class PromptDict(TypedDict):
    default_prompt_id: Required[int]
    label: Required[str]
    description: NotRequired[str]
    prompt: Required[str]
    method: Required[str]


DEFAULT_PROMPTS: Sequence[PromptDict] = [
    {
        "default_prompt_id": 1,
        "label": "ویرایش و اصلاح نگارش (Proofread)",
        "description": "اصلاح غلط‌های املایی، دستور زبان، علائم نگارشی و رعایت دقیق نیم‌فاصله‌ها",
        "prompt": (
            "Carefully proofread and edit the provided text. Correct all spelling mistakes, "
            "grammatical errors, punctuation, and Persian half-spaces (نیم‌فاصله). "
            "Do not alter the core vocabulary or style unnecessarily. Return ONLY the edited text."
        ),
        "method": "replace",
    },
    {
        "default_prompt_id": 2,
        "label": "ادامه و تکمیل متن (Continue Writing)",
        "description": "ادامه دادن و توسعه محتوای متن با همان سبک و لحن نویسنده",
        "prompt": (
            "Seamlessly continue writing and developing the provided text. "
            "Match the existing tone, vocabulary, style, perspective, and language. "
            "Do not repeat the input or provide conversational remarks. Return ONLY the continuation."
        ),
        "method": "append",
    },
    {
        "default_prompt_id": 3,
        "label": "روان‌سازی و بازنویسی (Polish & Rewrite)",
        "description": "بازنویسی جملات جهت روان‌تر شدن، شیوایی و رفع حشو و پیچیدگی",
        "prompt": (
            "Rewrite and polish the provided text to maximize fluency, elegance, and clarity. "
            "Remove filler and redundant phrasing (حشو) while staying completely faithful "
            "to the original meaning. Return ONLY the polished text."
        ),
        "method": "replace",
    },
    {
        "default_prompt_id": 4,
        "label": "رسمی و اداری‌سازی (Formal Tone)",
        "description": "تبدیل لحن متن به لحن رسمی، اداری و فاخر مناسب مکاتبات یا نشر",
        "prompt": (
            "Rewrite the provided text in a formal, professional, and respectful tone "
            "suitable for official correspondence, business documents, or publishing. "
            "Return ONLY the formal text."
        ),
        "method": "replace",
    },
    {
        "default_prompt_id": 5,
        "label": "صمیمی و وبلاگی (Casual Tone)",
        "description": "تبدیل لحن به حالتی صمیمی، شیوا و پرکشش مناسب مقالات و وب",
        "prompt": (
            "Rewrite the provided text in an approachable, warm, engaging, and conversational tone "
            "suitable for blogs, digital media, and articles. Return ONLY the rewritten text."
        ),
        "method": "replace",
    },
    {
        "default_prompt_id": 6,
        "label": "خلاصه‌سازی هوشمند (Summarize)",
        "description": "استخراج پیام و نکات کلیدی متن به شکلی فشرده و رسا",
        "prompt": (
            "Summarize the core message and essential points of the provided text "
            "concisely, clearly, and accurately. Return ONLY the summary."
        ),
        "method": "replace",
    },
]
