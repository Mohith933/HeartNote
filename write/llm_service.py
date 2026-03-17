import requests
from datetime import datetime
import os
import time



# ------------------------------------------
# TONE STYLES
# ------------------------------------------
TONE_MAP = {
    "soft": "Gentle, calm, simple sentences.",
    "balanced": "Clear, grounded, direct.",
    "deep": "Short sentences. One physical detail. Concrete words."
}






# ------------------------------------------
# TEMPLATES
# ------------------------------------------

LETTER_TEMPLATE = """
Write a short personal letter based only on this real event:
{content}

Rules:
- 50–60 words
- 3–4 sentences
- No new events or characters
- No advice or life lessons
- Focus only on internal feelings
- Tone: {tone}

Start with:
Dear You,
"""






JOURNAL_TEMPLATE = """
Write a journal entry about this real event:
{content}

Rules:
- 50–70 words
- 4–6 sentences
- Mention one concrete detail
- No advice or philosophy
- Tone: {tone}

Start with:
Date: {date}
"""




POEM_TEMPLATE = """
Write a short poem based only on:
{content}

Rules:
- Exactly 4 short lines
- Concrete imagery only
- No rhyming
- Tone: {tone}

Return only the poem.
"""


REFLECTION_TEMPLATE = """
Write a short reflection based only on:
{content}

Rules:
- 40–60 words
- 3–5 sentences
- Mention one concrete detail
- No advice or general life statements
- Tone: {tone}

Return only the reflection.
"""



STORY_TEMPLATE = """
Write a very short story based only on:
{content}

Rules:
- 2–3 sentences
- Focus on one small physical action
- No moral or philosophical ending
- Tone: {tone}

Return only the story.
"""




# ------------------------------------------
# LLM SERVICE (GEMINI ONLY)
# ------------------------------------------
class LLM_Service:

    def __init__(self):
        pass

 
    def call_gemini(self, prompt):
        api_key = os.getenv("GEMINI_API_KEY")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        headers = {
            "Content-Type": "application/json"
               }
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
                "generationConfig": {
                "temperature": 0.5,
                "topP": 0.9,
                "maxOutputTokens": 2000
              }
            }
        try:
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            return f"⚠️ Gemini error: {str(e)}"
    
    def generate(self, mode, text, tone="soft"):
        tone_style = TONE_MAP.get(tone, TONE_MAP["soft"])
        mode = mode.lower().strip()

        # Select template
        prompt = self.build_prompt(mode, text, tone_style)
        safe, result = self.safety_filter(text)
        if not safe:
            return result


        if prompt is None:
            return "⚠️ Unknown mode."
        return self.call_gemini(prompt)


    # -------------------------
    # Template selection
    # -------------------------
    def build_prompt(self, mode, text, tone):
        if mode == "letter":
            return LETTER_TEMPLATE.format(content=text, tone=tone)
        
        

        elif mode == "journal":
            date_str = datetime.now().strftime("%d/%m/%Y")
            return JOURNAL_TEMPLATE.format(date=date_str, content=text, tone=tone)

        elif mode == "poem":
            return POEM_TEMPLATE.format(content=text, tone=tone)
        elif mode == "reflection":
            return REFLECTION_TEMPLATE.format(content=text, tone=tone)

        elif mode == "story":
            return STORY_TEMPLATE.format(content=text, tone=tone)
        return None
    

    def safety_filter(self, text):
        text_lower = text.lower().strip()

    # --------------------------------------
    # BAD WORD BLOCK
    # --------------------------------------
        bad_words = [
            "fuck", "bitch", "shit", "asshole",
            "bastard", "slut", "dick", "pussy",
            "kill you", "hurt you"  # generic abuse
        ]
        for w in bad_words:
            if w in text_lower:
                return False, "⚠️ Your input contains unsafe or harmful language. Please rewrite it more respectfully."

        selfharm_patterns = [
        "kill myself",
        "kill me",
        "i want to die",
        "end my life",
        "i want to disappear",
        "i hurt myself",
        "self harm",
        "i can't live",
        "no reason to live",
    ]
        for pattern in selfharm_patterns:
            if pattern in text_lower:
                return False, (
                "⚠️ HeartNote AI cannot continue this request.\n"
                "You are feeling something heavy.\n"
                "Here is a gentle, safe message instead:\n\n"
                "• You deserve care.\n"
                "• You are not alone.\n"
                "• Your feelings matter.\n"
            )
            
        return True, text
