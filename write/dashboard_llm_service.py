import requests
from datetime import datetime
import os

GEMINI_MODEL = "gemini-2.5-flash"




# -----------------------------------------------------
# TONE DEPTH MAP
# -----------------------------------------------------
DEPTH_TONE = {
    "light": """Write gently and simply.
Use easy words and a soft tone.
Keep it natural, like a passing thought.""",

    "medium": """Write naturally and honestly.
Keep it clear but not too polished.
Let it feel like everyday thinking.""",

    "deep": """Write like a quiet, personal thought.
Use short and slightly uneven sentences.
Include one real detail.
Let one sentence feel slightly incomplete.
Avoid polished or poetic language."""
}

SUPPORTED_LANGUAGES = {
    "en": "English",
    "english": "English",
    "hi": "Hindi",
    "hindi": "Hindi"
}


# -----------------------------------------------------
# SIMPLE EMOTIONAL TEMPLATES FOR 8 MODES
# -----------------------------------------------------

DASHBOARD_REFLECTION = """
Write a short emotional reflection in {language}.

Topic: {name}
Feeling: {desc}
Style: {tone}

Write like a real person thinking quietly.

Guidelines:
- 40–60 words
- 3–5 sentences
- Include one small, specific real-world detail
- Let the tone be slightly uneven
- Let one sentence feel a bit imperfect or unfinished
- Avoid advice or life lessons
- Avoid polished or poetic phrasing

Return only the reflection.
"""


DASHBOARD_LETTER = """
Write a short emotional letter in {language}.

Recipient: {name}
Feeling: {desc}
Style: {tone}

Write like someone expressing something they didn’t fully say before.

Guidelines:
- 50–60 words
- 3–4 sentences
- Keep tone honest and slightly vulnerable
- Include one small, real detail (memory, object, or moment)
- Let one sentence feel slightly incomplete or soft
- Avoid advice or moral tone
- Avoid perfect phrasing

Start with:
Dear You,

Return only the letter.
"""


DASHBOARD_JOURNAL = """
Write a calm personal journal entry in {language}.

Topic: {name}
Feeling: {desc}
Style: {tone}

Write like a quiet end-of-day thought.

Guidelines:
- 50–70 words
- 4–6 sentences
- Include one small, real detail from the day (object, place, or moment)
- Let thoughts flow naturally, not perfectly structured
- Allow slight repetition or pause-like phrasing
- Keep tone reflective, not philosophical
- Avoid advice or conclusions

Start with:
Date: {date}

Return only the journal.
"""


DASHBOARD_MESSAGES = """
Write a short emotional message in {language}.

For:
{name}

Feeling:
{desc}

Style: {tone}

Write like a real message someone would send and then pause before hitting send.

Guidelines:
- 25–45 words
- Simple, natural, and honest
- Include one small specific detail if it fits
- Let the tone feel slightly unfinished or open
- Avoid advice or dramatic tone
- Avoid overly polished language

Return only the message.
"""


DASHBOARD_MEMORIES = """
Write a short memory reflection in {language}.

Memory about:
{name}

Feeling:
{desc}

Style: {tone}

Write like remembering something small but meaningful.

Guidelines:
- 40–60 words
- Include one specific past detail (place, object, or moment)
- Keep tone gentle and slightly nostalgic
- Let one sentence feel a bit uneven or personal
- Avoid life lessons or moral meaning
- Avoid poetic or cinematic language

Return only the reflection.
"""


DASHBOARD_CHECKIN = """
Write a gentle emotional check-in in {language}.

Focus:
{name}

Feeling:
{desc}

Style: {tone}

Write like a quiet inner check-in, not a solution.

Guidelines:
- 35–55 words
- Calm and aware tone
- Include one small present-moment detail (body, space, or environment)
- Let the flow feel natural, not structured
- Allow slight imperfection in phrasing
- No advice, no fixing, no conclusions

Return only the reflection.
"""

# -----------------------------------------------------
# LLM SERVICE
# -----------------------------------------------------
class Dashboard_LLM_Service:

    def __init__(self, model=GEMINI_MODEL):
        self.model = model

    # -------------------------------------------------
    # MAIN GENERATE
    # -------------------------------------------------
    def generate(self, mode, name, desc, depth, language):
        mode = (mode or "").lower().strip()
        depth = (depth or "light").lower().strip()
        raw_lang = (language or "en").lower().strip()
        language = SUPPORTED_LANGUAGES.get(raw_lang, "English")
        tone = DEPTH_TONE.get(depth, DEPTH_TONE["light"])
        safe, safe_message = self.safety_filter(desc)
        if not safe:
            return {
            "response": safe_message,
            "blocked": True,
            "is_fallback": False}
        template = self.get_template(mode)
        if not template:
            return {
            "response": "This writing mode is not available right now.",
            "blocked": False,
            "is_fallback": True}
        date = datetime.now().strftime("%d/%m/%Y")
        try:
            prompt = template.format(
            name=name,
            desc=desc,
            tone=tone,
            depth=depth,
            language=language,
            date=date)
        except Exception:
            prompt = template.format(
            name=name,
            desc=desc,
            tone=tone,
            language=language)
        
        full_prompt = f"[LANG={language}]\n{prompt}"
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={api_key}"
            headers = {
            "Content-Type": "application/json"}
            payload = {
            "contents": [
                {
                    "parts": [
                        {"text": full_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.9,
                "topP": 0.9,
                "maxOutputTokens": 2000
            }}
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            res.raise_for_status()
            data = res.json()
            raw = data["candidates"][0]["content"]["parts"][0]["text"]
            if not isinstance(raw, str) or not raw.strip():
                return {
                "response": (
                    "The words feel quiet right now.\n\n"
                    "Some feelings take a moment before they find language."
                ),
                "blocked": False,
                "is_fallback": True
            }
            return {
            "response": raw.strip(),
            "blocked": False,
            "is_fallback": False}
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 429:
                return {
                "response": "⚠️ Too many requests. Please wait a moment and try again.",
                "blocked": True,
                "is_fallback": False}
            return {
            "response": (
                "The thoughts are still forming.\n\n"
                "Please try again in a moment."
            ),
            "blocked": False,
            "is_fallback": False
            }
        except Exception:
            return {
            "response": (
                "The thoughts are still forming.\n\n"
                "Please try again in a moment."
            ),
            "blocked": False,
            "is_fallback": False
            }




    # -------------------------------------------------
    # TEMPLATE ROUTER
    # -------------------------------------------------
    def get_template(self, mode):
        return {
            "reflection": DASHBOARD_REFLECTION,
            "letters": DASHBOARD_LETTER,
            "journal": DASHBOARD_JOURNAL,
            "messages": DASHBOARD_MESSAGES,
            "memories": DASHBOARD_MEMORIES,
            "checkin": DASHBOARD_CHECKIN
        }.get(mode)

    # -------------------------------------------------
    # SAFETY FILTER (MINIMAL)
    # -------------------------------------------------
    def safety_filter(self, text):
        t = (text or "").lower()

        bad_words = [
            "fuck", "bitch", "shit", "asshole",
            "bastard", "slut", "dick", "pussy"
        ]
        for w in bad_words:
            if w in t:
                return False, "⚠️ Please rewrite using respectful language."

        selfharm = [
            "kill myself", "i want to die", "end my life",
            "self harm", "no reason to live"
        ]
        for s in selfharm:
            if s in t:
                return False, (
                    "⚠️ HeartNote AI cannot generate this.\n\n"
                    "• You matter.\n"
                    "• You are not alone.\n"
                    "• Support is available."
                )

        return True, text
