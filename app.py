import base64
import random
from pathlib import Path

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from utils.groq_client import (
    fill_you_persona_blanks,
    generate_family_personality,
    generate_random_character_intro,
    query,
)
from utils.persona_prompts import (
    FRIEND_STYLE_KEYS,
    PERSONAS,
    RANDOM_ROLES,
    build_system_prompt,
)
from rag_engine import retrieve_context
from utils.avatars import (
    AVATAR_OPTIONS,
    DEFAULT_AVATAR_ID,
    resolve_avatar_path,
)
from utils.pixel_icons import friend_icon_key, persona_icon_key, pixel_icon_html
from dotenv import load_dotenv
import os
from agent_tools import run_agent

load_dotenv()

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
_LOGO_PNG = ASSETS / "lifevoice_logo.png"
LOGO_PATH = _LOGO_PNG if _LOGO_PNG.exists() else ASSETS / "logo.svg"
FONT_PATH = ASSETS / "StardewValley.ttf"

st.set_page_config(page_title="lifeVoice", layout="wide", initial_sidebar_state="expanded")

TAGLINE = "Life speaks in many voices — which one would you like to hear today?"

# ── Logo sizes ──────────────────────────────────────────────────────────────
LOGO_WIDTH_HERO = 560
LOGO_WIDTH_COMPACT = 112


PERSONA_CARDS = [
    ("Professional", "Career voice"),
    ("Family", "Someone who knows you"),
    ("Friend", "Peer energy"),
    ("You", "Past or future you"),
    ("Random", "A surprise stranger"),
]


def inject_warm_theme_css():
    st.markdown(
        f"""
        <style>
            @font-face {{
                font-family: 'StardewValley';
                src: url('app/assets/StardewValley.ttf') format('truetype');
            }}
            :root {{
                --lv-earth: #8B5E3C;
                --lv-wheat: #F4D06F;
                --lv-leaf: #6A994E;
                --lv-sky: #A7C7E7;
                --lv-peach: #F9A875;
                --lv-cream: #FDF8E8;
                --lv-ink: #5C3D28;
                --lv-muted: #8B5E3C;
            }}
            /* ── Apply StardewValley font to everything ── */
            html, body, [class*="css"], * {{
                font-family: 'StardewValley', "Press Start 2P", monospace !important;
            }}
            .stApp {{
                background: linear-gradient(165deg, var(--lv-cream) 0%, #FFF9F0 45%, #F4E8C8 100%);
            }}
            section[data-testid="stSidebar"] {{
                background: linear-gradient(180deg, #FFF9F0 0%, var(--lv-cream) 100%) !important;
                border-right: 2px solid var(--lv-wheat) !important;
            }}
            h1, h2, h3, h4, .lv-pixel-title {{
                font-family: 'StardewValley', "Press Start 2P", monospace !important;
                color: var(--lv-earth) !important;
            }}
            .block-container {{
                padding-top: 1.25rem !important;
                padding-bottom: 3rem !important;
                max-width: 1080px;
            }}
            .lv-pixel-icon {{
                image-rendering: pixelated;
                image-rendering: crisp-edges;
                display: block;
                margin: 0 auto 0.5rem;
            }}
            .lv-persona-blurb {{
                color: var(--lv-muted);
                font-size: 0.85rem;
                margin: 0 0 0.65rem;
                line-height: 1.4;
                text-align: center;
                font-family: 'StardewValley', monospace !important;
            }}
            .lv-selected-label {{
                color: var(--lv-leaf);
                font-weight: 700;
                text-align: center;
                font-size: 0.8rem;
                font-family: 'StardewValley', monospace !important;
            }}
            .lv-tagline {{
                text-align: center;
                color: var(--lv-muted);
                font-size: 1.1rem;
                margin-top: 0.5rem;
                font-family: 'StardewValley', monospace !important;
            }}
            .lv-logo-container {{
                display: flex;
                justify-content: center;
                margin-bottom: 0.5rem;
            }}
            [data-testid="stImage"] img {{
                image-rendering: pixelated;
                image-rendering: crisp-edges;
            }}
            /* ── Ghost buttons ── */
            div[data-testid="column"] .lv-ghost-btn .stButton > button {{
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                color: var(--lv-earth) !important;
                min-height: 0 !important;
                padding: 0.15rem 0.35rem !important;
                font-family: 'StardewValley', monospace !important;
            }}
            div[data-testid="column"] .lv-ghost-btn .stButton > button:hover {{
                color: var(--lv-leaf) !important;
            }}
            div[data-testid="column"] .lv-ghost-btn .stButton > button[kind="primary"] {{
                color: var(--lv-leaf) !important;
                background: transparent !important;
                border: none !important;
            }}
            .stButton > button {{
                border-radius: 8px !important;
                font-weight: 600 !important;
                font-family: 'StardewValley', monospace !important;
            }}
            .stButton > button[kind="primary"] {{
                background: var(--lv-leaf) !important;
                border-color: var(--lv-earth) !important;
                color: #fff !important;
            }}
            .stButton > button[kind="secondary"] {{
                background: var(--lv-wheat) !important;
                color: var(--lv-earth) !important;
                border: 2px solid var(--lv-peach) !important;
            }}
            div[data-testid="stChatMessage"] {{
                background-color: rgba(255, 255, 255, 0.7) !important;
                border: 2px solid var(--lv-wheat) !important;
                border-radius: 10px !important;
            }}
            div[data-testid="stChatMessage"] img {{
                width: 80px !important;
                height: 80px !important;
            }}
            div[data-testid="stBottom"] > div {{
                background: linear-gradient(180deg, transparent, var(--lv-cream));
                padding-top: 0.5rem !important;
                padding-bottom: 0.5rem !important;
                display: flex !important;
                justify-content: center !important;
            }}
            div[data-testid="stBottom"] > div > div {{
                max-width: 80% !important;
                width: 80% !important;
            }}

            /* ── HIDE the enter button entirely! ── */
            div[data-testid="stChatInput"] button {{
                display: none !important;
            }}
            div[data-testid="stChatInput"] textarea {{
                min-height: 44px !important;
                max-height: 120px !important;
                resize: none !important;
                width: 100% !important;
            }}

            /* ── Avatar click styling ── */
            .lv-avatar-clickable {{
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
                border-radius: 12px;
                border: 3px solid transparent;
            }}
            .lv-avatar-clickable:hover {{
                transform: scale(1.08);
                box-shadow: 0 4px 12px rgba(139, 94, 60, 0.3);
            }}
            .lv-avatar-selected {{
                border: 4px solid var(--lv-leaf) !important;
                box-shadow: 0 0 12px var(--lv-leaf);
            }}
            /* ── Avatar name buttons: no hover color shift ── */
            .stButton > button:hover {{
                background: inherit !important;
                color: inherit !important;
                border-color: inherit !important;
                box-shadow: none !important;
                transform: none !important;
            }}
            /* ── Center gender radio label + options ── */
            div[data-testid="stRadio"] {{
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                width: 100% !important;
            }}
            div[data-testid="stRadio"] > label {{
                text-align: center !important;
                width: 100% !important;
                font-family: 'StardewValley', monospace !important;
            }}
            div[data-testid="stRadio"] > div {{
                justify-content: center !important;
                display: flex !important;
                flex-wrap: wrap !important;
                gap: 1rem !important;
                width: 100% !important;
            }}
            /* ── Center the Continue button ── */
            div[data-testid="stFormSubmitButton"] {{
                display: flex !important;
                justify-content: center !important;
            }}
            div[data-testid="stFormSubmitButton"] > button {{
                min-width: 180px !important;
            }}
            /* Ensure all input/form labels use the font */
            label, .stTextInput label, .stNumberInput label, .stRadio label,
            .stSelectbox label, .stTextArea label, .stForm label {{
                font-family: 'StardewValley', monospace !important;
            }}
            /* Streamlit form inputs */
            input, textarea, select {{
                font-family: 'StardewValley', monospace !important;
                background-color: #FFF !important;
                border: 2px solid var(--lv-leaf) !important;
                border-radius: 8px !important;
                box-shadow: 0 2px 8px rgba(106, 153, 78, 0.2) !important;
            }}
            /* Caption text */
            .stCaption, small, .stMarkdown p {{
                font-family: 'StardewValley', monospace !important;
            }}

            /* ── Sidebar toggle: hide Material Icon text, keep only the SVG arrow ── */
            [data-testid="stSidebarCollapsedControl"] {{
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }}
            [data-testid="stSidebarCollapsedControl"] button {{
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                min-width: 36px !important;
                min-height: 36px !important;
                overflow: hidden !important;
            }}
            /* Hide any span/div that does NOT contain an SVG (i.e. the text node wrappers) */
            [data-testid="stSidebarCollapsedControl"] button span:not(:has(svg)),
            [data-testid="stSidebarCollapsedControl"] button div:not(:has(svg)) {{
                display: none !important;
                width: 0 !important;
                height: 0 !important;
                overflow: hidden !important;
                position: absolute !important;
                opacity: 0 !important;
                pointer-events: none !important;
            }}
            [data-testid="stSidebarCollapsedControl"] svg {{
                display: block !important;
                width: 22px !important;
                height: 22px !important;
                color: var(--lv-earth) !important;
                flex-shrink: 0 !important;
            }}

            /* ── Center Start conversation button ── */
            .lv-center-btn {{
                display: flex !important;
                justify-content: center !important;
                margin-top: 1.5rem !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_branding(hero: bool = True):
    inject_warm_theme_css()
    if hero:
        st.markdown('<div class="lv-logo-container">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(str(LOGO_PATH), width=LOGO_WIDTH_HERO)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="lv-tagline">{TAGLINE}</p>', unsafe_allow_html=True)
    else:
        c1, c2 = st.columns([1, 5], vertical_alignment="center")
        with c1:
            st.image(str(LOGO_PATH), width=LOGO_WIDTH_COMPACT)
        with c2:
            st.caption(TAGLINE)


def user_chat_avatar() -> str:
    return resolve_avatar_path(st.session_state.get("user_avatar_id"))


def avatar_as_base64(path: str) -> str:
    """Return a base64 data-URI for an avatar image so it works in HTML <img>."""
    try:
        p = Path(path)
        if not p.exists():
            p = ROOT / "assets" / "avatars" / Path(path).name
        if p.exists():
            ext = p.suffix.lstrip(".").lower()
            mime = "image/png" if ext == "png" else f"image/{ext}"
            data = base64.b64encode(p.read_bytes()).decode()
            return f"data:{mime};base64,{data}"
    except Exception:
        pass
    return ""


def render_avatar_picker(compact: bool = False) -> None:
    """Six-option avatar grid; selection stored in session_state.user_avatar_id."""
    selected = st.session_state.get("user_avatar_id") or DEFAULT_AVATAR_ID
    if not compact:
        st.markdown("##### Pick your avatar")
    cols = st.columns(6, gap="small")
    img_w = 80 if compact else 120
    for col, opt in zip(cols, AVATAR_OPTIONS):
        aid = opt["id"]
        is_selected = selected == aid
        with col:
            border_class = "lv-avatar-selected" if is_selected else ""
            if st.button(
                "",
                key=f"avatar_btn_{aid}" if not compact else f"avatar_btn_sidebar_{aid}",
                help=opt["label"],
                use_container_width=True,
            ):
                st.session_state.user_avatar_id = aid
                st.rerun()
            st.markdown(
                f'''<div style="text-align: center;">
                    <img src="{resolve_avatar_path(aid)}"
                         width="{img_w}"
                         class="lv-avatar-clickable {border_class}"
                         style="image-rendering: pixelated;" />
                </div>''',
                unsafe_allow_html=True,
            )
            if is_selected:
                st.markdown('<p class="lv-selected-label">✓</p>', unsafe_allow_html=True)


def render_avatar_picker_clickable(compact: bool = False) -> None:
    """
    Clickable avatar picker using st.image (no broken HTML img src).
    Avatar name is the button label. Selected avatar gets a green border via CSS trick.
    """
    selected = st.session_state.get("user_avatar_id") or DEFAULT_AVATAR_ID
    if not compact:
        st.markdown("##### Pick your avatar")

    cols = st.columns(6, gap="medium")
    img_w = 88 if compact else 160

    for col, opt in zip(cols, AVATAR_OPTIONS):
        aid = opt["id"]
        label = opt["label"]
        is_selected = selected == aid
        avatar_path = resolve_avatar_path(aid)

        with col:
            if is_selected:
                st.markdown(
                    '<div style="border:4px solid #6A994E;box-shadow:0 0 10px #6A994E;'
                    'border-radius:10px;padding:2px;margin-bottom:4px;">',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div style="border:3px solid transparent;border-radius:10px;'
                    'padding:2px;margin-bottom:4px;">',
                    unsafe_allow_html=True,
                )

            st.image(avatar_path, width=img_w)
            st.markdown("</div>", unsafe_allow_html=True)

            btn_label = f"✓ {label}" if is_selected else label
            if st.button(
                btn_label,
                key=f"avatar_click_{aid}" if not compact else f"avatar_click_sidebar_{aid}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
            ):
                st.session_state.user_avatar_id = aid
                st.rerun()


def render_sidebar():
    if not st.session_state.get("user_name"):
        return
    with st.sidebar:
        av_src = avatar_as_base64(user_chat_avatar())
        img_tag = (
            f'<img src="{av_src}" width="180" '
            'style="image-rendering:pixelated;border-radius:10px;'
            'display:block;margin:0 auto;" />'
            if av_src else
            '<div style="width:180px;height:180px;background:var(--lv-wheat);'
            'border-radius:10px;margin:0 auto;display:flex;align-items:center;'
            'justify-content:center;color:var(--lv-earth);font-size:2rem;">👤</div>'
        )
        st.markdown(
            f'''<div style="display:flex;flex-direction:column;align-items:center;
                           padding:1rem 0 0.5rem;gap:0.5rem;">
                {img_tag}
                <div style="text-align:center;color:var(--lv-earth);font-weight:700;
                            font-size:1rem;font-family:StardewValley,monospace;
                            margin-top:0.25rem;">
                    {st.session_state.user_name}
                </div>
                <div style="text-align:center;color:var(--lv-muted);font-size:0.8rem;
                            font-family:StardewValley,monospace;">
                    Age {st.session_state.user_age} · {st.session_state.get("user_gender") or "—"}
                </div>
            </div>''',
            unsafe_allow_html=True,
        )
        st.divider()
        if st.session_state.get("intro_done"):
            if st.button("Switch persona", use_container_width=True, type="primary"):
                st.session_state.messages = []
                st.session_state.intro_done = False
                st.session_state.system_prompt = None
                st.session_state.selected_persona = None
                st.session_state.friend_style = None
                st.session_state.onboarding_step = "persona"
                st.rerun()
            st.caption("Starts a fresh persona setup. Your name, age, and gender stay the same.")
        else:
            st.caption("Pick a voice to begin.")


def reset_to_persona():
    st.session_state.messages = []
    st.session_state.intro_done = False
    st.session_state.system_prompt = None
    st.session_state.selected_persona = None
    st.session_state.friend_style = None
    st.session_state.onboarding_step = "persona"


# --- Session defaults ---
_defaults = {
    "messages": [],
    "user_name": None,
    "user_age": None,
    "user_gender": None,
    "user_avatar_id": DEFAULT_AVATAR_ID,
    "onboarding_step": "name",
    "selected_persona": None,
    "friend_style": None,
    "system_prompt": None,
    "intro_done": False,
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

inject_warm_theme_css()

# Step 1: name + age + gender
if st.session_state.onboarding_step == "name":
    render_branding(hero=True)
    st.markdown("Hi! This is **lifeVoice** — tell us a little about you.")
    render_avatar_picker_clickable()
    with st.form("name_form"):
        c1, c2 = st.columns(2, gap="large")
        with c1:
            name_in = st.text_input("Your name", placeholder="Type your name")
        with c2:
            age_in = st.number_input(
                "Your age",
                min_value=1,
                max_value=120,
                value=25,
                help="Used especially for the **You** persona.",
            )
        gender_in = st.radio(
            "Gender",
            ["Male", "Female", "Non-binary", "Prefer not to say"],
            horizontal=True,
        )

        if st.form_submit_button("Continue", type="primary"):
            if name_in.strip():
                st.session_state.user_name = name_in.strip()
                st.session_state.user_age = int(age_in)
                st.session_state.user_gender = gender_in
                st.session_state.onboarding_step = "persona"
                st.rerun()
            else:
                st.warning("Please enter your name to continue.")
    st.stop()

user_name = st.session_state.user_name
user_age = st.session_state.user_age
user_gender = st.session_state.user_gender

# Step 2: persona
if st.session_state.onboarding_step == "persona":
    render_sidebar()
    render_branding(hero=True)
    st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)
    st.markdown(f"Hi **{user_name}**, please pick a persona to chat with — you can switch or change details later!")
    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    persona_row = st.columns(5, gap="medium")
    for col, (label, blurb) in zip(persona_row, PERSONA_CARDS):
        with col:
            st.markdown(
                pixel_icon_html(persona_icon_key(label), 72, label)
                + f'<p class="lv-persona-blurb" style="min-height:3rem;">{blurb}</p>',
                unsafe_allow_html=True,
            )
            selected = st.session_state.selected_persona == label
            if st.button(
                label,
                key=f"persona_box_{label}",
                use_container_width=True,
                type="primary" if selected else "secondary",
            ):
                st.session_state.selected_persona = label
                if label != "Friend":
                    st.session_state.friend_style = None
                st.rerun()

    if st.session_state.selected_persona == "Friend":
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        st.markdown("##### Friend personalities — pick one")
        st.caption("Each style changes how your friend talks and reacts.")
        fcols = st.columns(len(FRIEND_STYLE_KEYS), gap="medium")
        for col, style in zip(fcols, FRIEND_STYLE_KEYS):
            with col:
                st.markdown(pixel_icon_html(friend_icon_key(style), 56, style), unsafe_allow_html=True)
                picked = st.session_state.friend_style == style
                st.markdown('<div class="lv-ghost-btn">', unsafe_allow_html=True)
                if st.button(
                    style,
                    key=f"friend_style_{style}",
                    use_container_width=True,
                    type="primary" if picked else "secondary",
                ):
                    st.session_state.friend_style = style
                    st.rerun()

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1, 1, 1])
    with center_col:
        if st.button("Start conversation", type="primary", use_container_width=True):
            p = st.session_state.selected_persona
            if not p:
                st.warning("Choose a persona first.")
            elif p == "Friend" and not st.session_state.friend_style:
                st.warning("Choose a friend personality first.")
            elif p == "Random":
                intro = generate_random_character_intro(user_name)
                st.session_state.system_prompt = build_system_prompt(
                    "Random",
                    user_name=user_name,
                    user_age=user_age,
                    user_gender=user_gender,
                    intro_message=intro,
                )
                st.session_state.messages.append({"role": "assistant", "content": intro})
                st.session_state.intro_done = True
                st.session_state.onboarding_step = "chat"
                st.rerun()
            else:
                st.session_state.onboarding_step = "details"
                st.rerun()
    st.stop()

# Step 3: details
if st.session_state.onboarding_step == "details" and not st.session_state.intro_done:
    render_sidebar()
    render_branding(hero=False)
    persona = st.session_state.selected_persona
    st.markdown(f"##### Almost there")
    st.markdown(f"Tell **lifeVoice** a bit more for **{persona}** — leave blanks where you want the AI to fill in.")

    profession = ""
    family_member = ""
    family_attitude = ""
    character_name = ""
    friend_type = st.session_state.friend_style or "Optimist"
    friend_name = ""
    you_year = ""
    you_description = ""

    if persona == "Professional":
        profession = st.text_input(
            "Profession (e.g. teacher, therapist) — random if left blank",
        )
        character_name = st.text_input("Their name — random if left blank")
    elif persona == "Family":
        family_member = st.text_input(
            "Family role (e.g. mother, older sibling) — random if left blank",
        )
        family_attitude = st.text_area(
            "Personality or attitude of this family member (warm, strict, playful…) — AI picks if left blank",
            placeholder="e.g. protective and teasing, but soft when it matters",
            height=90,
        )
        character_name = st.text_input("Their name — random if left blank")
    elif persona == "You":
        you_year = st.text_input(
            "When? (e.g. 5 years ago, 5 years in the future) — AI picks if left blank",
        )
        you_description = st.text_area(
            "Briefly describe who you were in that time — AI picks if left blank",
        )
    elif persona == "Friend":
        friend_type = st.selectbox(
            "Friend persona",
            FRIEND_STYLE_KEYS,
            index=(
                FRIEND_STYLE_KEYS.index(st.session_state.friend_style)
                if st.session_state.friend_style in FRIEND_STYLE_KEYS
                else 0
            ),
        )
        friend_name = st.text_input("Their name — random if left blank")
    elif persona == "Random":
        st.caption("No fields needed — the AI will invent someone for you.")

    _, center_col, _ = st.columns([1, 1, 1])
    with center_col:
        begin = st.button("Begin chat", type="primary", use_container_width=True)

    if begin:
        intro = None
        prof_resolved = profession
        fam_resolved = family_member
        year_resolved = you_year
        desc_resolved = you_description
        fam_personality = (family_attitude or "").strip()

        if persona == "Professional":
            if not (prof_resolved or "").strip():
                prof_resolved = random.choice(RANDOM_ROLES)
            intro = PERSONAS["Professional"]["intro"](
                prof_resolved, character_name, user_name
            )
            st.session_state.system_prompt = build_system_prompt(
                "Professional",
                user_name=user_name,
                profession=prof_resolved,
                character_name=character_name,
                user_age=user_age,
                user_gender=user_gender,
                intro_message=intro,
            )
        elif persona == "Family":
            if not (fam_resolved or "").strip():
                fam_resolved = random.choice(
                    [
                        "mother",
                        "father",
                        "older sibling",
                        "younger sibling",
                        "grandmother",
                        "grandfather",
                        "aunt",
                        "uncle",
                        "cousin",
                    ]
                )
            if not fam_personality:
                fam_personality = generate_family_personality(fam_resolved, user_name)
            intro = PERSONAS["Family"]["intro"](
                fam_resolved, character_name, user_name, fam_personality
            )
            st.session_state.system_prompt = build_system_prompt(
                "Family",
                user_name=user_name,
                family_member=fam_resolved,
                character_name=character_name,
                family_personality=fam_personality,
                user_age=user_age,
                user_gender=user_gender,
                intro_message=intro,
            )
        elif persona == "You":
            year_resolved, desc_resolved = fill_you_persona_blanks(
                user_name, you_year, you_description, user_age=user_age
            )
            intro = PERSONAS["You"]["intro"](
                year_resolved, desc_resolved, user_name, user_age
            )
            st.session_state.system_prompt = build_system_prompt(
                "You",
                user_name=user_name,
                you_year=year_resolved,
                you_description=desc_resolved,
                user_age=user_age,
                user_gender=user_gender,
                intro_message=intro,
            )
        elif persona == "Friend":
            st.session_state.friend_style = friend_type
            intro = PERSONAS["Friend"]["intro"](friend_type, friend_name, user_name)
            st.session_state.system_prompt = build_system_prompt(
                "Friend",
                user_name=user_name,
                friend_type=friend_type,
                character_name=friend_name,
                user_age=user_age,
                user_gender=user_gender,
                intro_message=intro,
            )
        elif persona == "Random":
            intro = generate_random_character_intro(user_name)
            st.session_state.system_prompt = build_system_prompt(
                "Random",
                user_name=user_name,
                user_age=user_age,
                user_gender=user_gender,
                intro_message=intro,
            )

        st.session_state.messages.append({"role": "assistant", "content": intro})
        st.session_state.intro_done = True
        st.session_state.onboarding_step = "chat"
        st.rerun()
    st.stop()

# Step 4: chat
render_sidebar()
render_branding(hero=False)

user_av = user_chat_avatar()
assistant_av = str(ASSETS / "Krobus.png")

for msg in st.session_state.messages:
    role = msg["role"]
    av = user_av if role == "user" else assistant_av
    with st.chat_message(role, avatar=av):
        st.markdown(msg["content"])

if st.session_state.intro_done:
    if prompt := st.chat_input("What's on your mind?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=user_av):
            st.markdown(prompt)

        # Retrieve RAG context
        context_docs = retrieve_context(
            prompt,
            persona=st.session_state.selected_persona,
            subpersona=st.session_state.friend_style,
        )

        context_text = "\n\n".join(context_docs) if context_docs else "(no retrieved context)"

        # Prepare persona context for agent
        persona_context = f"""{st.session_state.system_prompt}

Useful reference context from our knowledge base:
{context_text}
"""

        # Prepare chat history for agent
        chat_history = []
        for msg in st.session_state.messages[:-1]:
            if msg["role"] == "user":
                chat_history.append(HumanMessage(content=msg["content"]))
            else:
                chat_history.append(AIMessage(content=msg["content"]))

        # Run agent
        response = run_agent(prompt, persona_context, chat_history)

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant", avatar=assistant_av):
            st.markdown(response)