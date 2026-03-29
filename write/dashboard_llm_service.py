import requests
from datetime import datetime
import os


# -----------------------------------------------------
# DEPTH → TONE STYLE
# -----------------------------------------------------
DEPTH_TONE = {
    "light": "Write gently. Keep it simple and calm.",
    "medium": "Write naturally. Keep it clear and honest.",
    "deep": "Write with emotional weight. Use one real detail. Keep sentences short."
}


# -----------------------------------------------------
# SUPPORTED LANGUAGES
# -----------------------------------------------------
SUPPORTED_LANGUAGES = {
    "en": "English",
    "english": "English",
    "hi": "Hindi",
    "hindi": "Hindi"
}


# -----------------------------------------------------
# DASHBOARD TEMPLATES (FINAL)
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
# LLM SERVICE (MERGED)
# -----------------------------------------------------
class LLM_Service:

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")


    # -------------------------------------------------
    # GEMINI CALL
    # -------------------------------------------------
    def call_gemini(self, prompt, model="flash"):

        # 🔥 Model switching
        if model == "pro":
            model_name = "gemini-2.5-pro"
        else:
            model_name = "gemini-2.5-flash"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.9,
                "topP": 0.9,
                "maxOutputTokens": 300
            }
        }

        try:
            res = requests.post(url, json=payload, timeout=30)
            data = res.json()

            return data.get("candidates", [{}])[0] \
                .get("content", {}) \
                .get("parts", [{}])[0] \
                .get("text", "⚠️ No response").strip()

        except Exception as e:
            return f"⚠️ Gemini error: {str(e)}"


    # -------------------------------------------------
    # MAIN GENERATE
    # -------------------------------------------------
    def generate(self, mode, name, desc, depth="light", language="en"):

        mode = (mode or "").lower().strip()
        depth = (depth or "light").lower().strip()
        language = SUPPORTED_LANGUAGES.get(language.lower(), "English")

        tone = DEPTH_TONE.get(depth, DEPTH_TONE["light"])

        # ✅ Safety first
        safe, msg = self.safety_filter(desc)
        if not safe:
            return msg

        # ✅ Template
        template = self.get_template(mode)
        if not template:
            return "⚠️ Invalid mode"

        date = datetime.now().strftime("%d/%m/%Y")

        prompt = template.format(
            name=name,
            desc=desc,
            tone=tone,
            language=language,
            date=date
        )

        # 🔥 Smart model switch
        model_type = "pro" if depth == "deep" else "flash"

        return self.call_gemini(prompt, model=model_type)


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
    # SAFETY FILTER
    # -------------------------------------------------
    def safety_filter(self, text):

        t = (text or "").lower()

        bad_words = ["fuck", "bitch", "shit", "asshole"]
        for w in bad_words:
            if w in t:
                return False, "⚠️ Please use respectful language."

        selfharm = [
            "kill myself", "i want to die", "end my life",
            "self harm", "no reason to live"
        ]

        for s in selfharm:
            if s in t:
                return False, (
                    "⚠️ I can’t continue this.\n\n"
                    "You matter.\n"
                    "You are not alone.\n"
                    "Support is available."
                )

        return True, text