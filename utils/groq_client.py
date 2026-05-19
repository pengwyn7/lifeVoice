import os
from openai import OpenAI
from dotenv import load_dotenv
from langfuse import observe, get_client

# Load environment variables
load_dotenv()

# Initialize Langfuse
langfuse = get_client()

# Initialize Groq client using API key from .env
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

@observe()
def query(user_input, persona_prompt="You are a helpful assistant."):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": persona_prompt},
            {"role": "user", "content": user_input}
        ],
        max_tokens=300
    )
    return response.choices[0].message.content


@observe()
def _chat(system: str, user: str, max_tokens: int = 220) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=max_tokens,
    )
    return (response.choices[0].message.content or "").strip()


def generate_random_character_intro(user_name: str) -> str:
    """AI picks a random person, name, and short in-character introduction."""
    ai_line = _chat(
        "You invent brief roleplay intros. Output plain text only: one or two sentences, "
        "first person, in character. No quotes, no meta.",
        f"The human user is named {user_name}. Invent a random believable stranger "
        "(give yourself a name and role). Speak as that character introducing yourself to {user_name}.",
        max_tokens=180,
    )
    return f"Hi {user_name}, {ai_line}"


def fill_you_persona_blanks(
    user_name: str,
    year_hint: str,
    desc_hint: str,
    user_age: int | None = None,
) -> tuple[str, str]:
    """When year and/or description are missing, let the model choose plausible values."""
    y = (year_hint or "").strip()
    d = (desc_hint or "").strip()
    if y and d:
        return y, d
    age_ctx = f"Their current age is {user_age}. " if user_age is not None else ""
    filled = _chat(
        "Reply with exactly two lines. Line 1: a time offset phrase only "
        "(e.g. '5 years ago' or '8 years in the future'). "
        "Line 2: one short phrase describing that version of the person emotionally or in life situation. "
        "No labels, no extra text.",
        f"The person's name is {user_name}. {age_ctx}"
        f"User left some blanks. Known year hint: {y or 'none'}. Known description hint: {d or 'none'}. "
        "Fill missing parts consistently.",
        max_tokens=120,
    )
    lines = [ln.strip() for ln in filled.splitlines() if ln.strip()]
    gen_y = lines[0] if lines else "years away"
    gen_d = lines[1] if len(lines) > 1 else "a version of you shaped by that time"
    return (y or gen_y), (d or gen_d)


def generate_family_personality(family_role: str, user_name: str) -> str:
    """One short phrase describing attitude/demeanor when the user leaves it blank."""
    role = (family_role or "family member").strip() or "family member"
    return _chat(
        "Reply with one short phrase only (max 18 words): how this family member "
        "acts emotionally toward the user — warmth, humor, strictness, etc. "
        "No quotes, no name prefixes.",
        f"The user is named {user_name}. Family role: {role}. "
        "Invent a believable personality/attitude for this relative.",
        max_tokens=80,
    )
