import requests
from datetime import datetime
import os

GEMINI_MODEL = "gemini-2.5-flash"




# -----------------------------------------------------
# TONE DEPTH MAP
# -----------------------------------------------------
DEPTH_TONE = {
    "light": "Write gently. Keep it simple and calm.",
    "medium": "Write naturally. Keep it clear and honest.",
    "deep": "Write with emotional weight. Use one real detail. Keep sentences short."
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
Write a simple emotional reflection in {language}.

Topic: {name}
Feeling: {desc}
Style: {tone}

Rules:
- 40–60 words
- 3–5 sentences
- Mention one concrete detail
- No advice or life lessons
- End naturally
- Keep it complete
- Do not cut sentences

Return only the reflection.
"""


DASHBOARD_LETTER = """
Write a short emotional letter in {language}.

Recipient: {name}
Feeling: {desc}
Style: {tone}

Rules:
- 50–60 words
- 3–4 sentences
- No advice or moral tone
- Focus on feelings only
- End naturally
- Keep it complete
- Do not cut sentences

Start with:
Dear You,

Return only the letter.
"""


DASHBOARD_JOURNAL = """
Write a calm journal entry in {language}.

Topic: {name}
Feeling: {desc}
Style: {tone}

Rules:
- 50–70 words
- 4–6 sentences
- Mention one real detail
- No advice or philosophy
- End naturally
- Keep it complete
- Do not cut sentences

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

Rules:
- 25–45 words
- Simple and honest
- No advice
- End naturally
- Keep it complete
- Do not cut sentences

Return only the message.
"""


DASHBOARD_MEMORIES = """
Write a short memory reflection in {language}.

Memory about:
{name}

Feeling:
{desc}

Style: {tone}

Rules:
- 40–60 words
- Include one small past detail
- No life lesson
- End naturally
- Keep it complete
- Do not cut sentences

Return only the reflection.
"""


DASHBOARD_CHECKIN = """
Write a gentle emotional check-in in {language}.

Focus:
{name}

Feeling:
{desc}

Style: {tone}

Rules:
- 35–55 words
- Calm tone
- Awareness only, no advice
- End naturally
- Keep it complete
- Do not cut sentences

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
