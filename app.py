import streamlit as st
from openai import OpenAI
from PIL import Image
import json
import io
import os
import base64
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="Desi Calorie & Nutrition Detector",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Mandala Pattern Base64 (Subtle Geometric Pattern) ---
MANDALA_SVG = """
<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <path d="M50 0 L60 40 L100 50 L60 60 L50 100 L40 60 L0 50 L40 40 Z" fill="rgba(168, 85, 247, 0.03)" />
    <circle cx="50" cy="50" r="10" fill="rgba(34, 211, 238, 0.02)" />
</svg>
"""
MANDALA_B64 = base64.b64encode(MANDALA_SVG.encode()).decode()

# --- Custom Styling (Premium Desi Aesthetic) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');

    html, body, [class*="css"] {{
        font-family: 'Outfit', sans-serif;
    }}

    /* Layered Background with Mandala Pattern */
    .stApp {{
        background-color: #050505;
        background-image: 
            url("data:image/svg+xml;base64,{MANDALA_B64}"),
            radial-gradient(circle at top right, #1e1b4b, #050505);
        background-repeat: repeat, no-repeat;
        background-size: 100px 100px, cover;
        color: #f8fafc;
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }}

    /* Glowing Header */
    .header-title {{
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a855f7, #22d3ee);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
        filter: drop-shadow(0 0 15px rgba(168, 85, 247, 0.3));
        letter-spacing: -1px;
    }}

    .header-tagline {{
        text-align: center;
        font-weight: 300;
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 1rem;
        letter-spacing: 1px;
    }}

    /* Gradient Divider */
    .gradient-divider {{
        height: 1px;
        background: linear-gradient(90deg, transparent, #a855f7, #22d3ee, transparent);
        margin: 1.5rem 0;
        opacity: 0.4;
    }}

    /* Re-styling st.file_uploader to BE the attractive zone */
    [data-testid="stFileUploader"] {{
        border: 1px dashed rgba(34, 211, 238, 0.3);
        border-radius: 24px;
        padding: 60px 20px !important;
        text-align: center;
        background: rgba(168, 85, 247, 0.02);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        min-height: 250px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }}
    
    [data-testid="stFileUploader"]:hover {{
        background: rgba(168, 85, 247, 0.05);
        border-color: #22d3ee;
        transform: translateY(-4px);
        box-shadow: 0 10px 40px rgba(168, 85, 247, 0.1);
    }}

    /* Make the functional uploader fill the space and be transparent */
    [data-testid="stFileUploader"] section {{
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        z-index: 10;
        opacity: 0;
        cursor: pointer;
    }}
    [data-testid="stFileUploader"] label {{ display: none !important; }}
    
    /* Inject attractive UI via pseudo-elements - ensure they don't block clicks */
    [data-testid="stFileUploader"]::before {{
        content: 'add_a_photo';
        font-family: 'Material Icons';
        font-size: 48px;
        color: #22d3ee;
        display: block;
        margin-bottom: 15px;
        animation: neon-pulse 2s infinite;
        pointer-events: none;
    }}

    [data-testid="stFileUploader"]::after {{
        content: 'Drop your food photo here\\A Studio-grade AI Analysis';
        white-space: pre;
        display: block;
        font-weight: 400;
        font-size: 1rem;
        color: #94a3b8;
        line-height: 1.5;
        pointer-events: none;
    }}

    /* Metric Cards Upgrade */
    .macro-card {{
        background: rgba(15, 15, 18, 0.6);
        backdrop-filter: blur(20px);
        border-radius: 22px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(168, 85, 247, 0.15);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}
    .macro-card:hover {{
        transform: translateY(-10px);
        border-color: #a855f7;
        box-shadow: 0 15px 40px rgba(168, 85, 247, 0.2);
    }}
    .val {{ font-size: 1.8rem; font-weight: 800; margin: 0.5rem 0; color: #f8fafc; }}
    .unit {{ font-size: 0.75rem; color: #64748b; font-weight: 400; text-transform: uppercase; letter-spacing: 1px; }}
    .label {{ font-size: 0.8rem; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 5px; color: #94a3b8; }}

    /* Burn Plan visual pills */
    .burn-pill {{
        display: flex;
        align-items: center;
        gap: 10px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 100px;
        padding: 8px 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }}
    .burn-pill:hover {{
        background: rgba(168, 85, 247, 0.05);
        border-color: rgba(168, 85, 247, 0.2);
        transform: translateY(-2px);
    }}
    .burn-label {{ font-size: 0.85rem; color: #cbd5e1; }}
    .burn-time {{ font-weight: 800; font-size: 0.9rem; }}

    /* Insight Cards */
    .insight-card {{
        background: rgba(168, 85, 247, 0.03);
        border-left: 3px solid #a855f7;
        padding: 15px 20px;
        border-radius: 8px 20px 20px 8px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 12px;
        border: 1px solid rgba(168, 85, 247, 0.1);
    }}

    .swap-card {{
        background: rgba(34, 211, 238, 0.03);
        border-left: 3px solid #22d3ee;
        padding: 18px;
        border-radius: 8px 24px 24px 8px;
        margin-top: 15px;
        border: 1px solid rgba(34, 211, 238, 0.1);
    }}

    /* Confidence Badges */
    .badge {{
        padding: 4px 12px;
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .badge-high {{ background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }}
    .badge-medium {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }}
    .badge-low {{ background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }}

    /* Full-width Button */
    .stButton>button {{
        width: 100% !important;
        background: linear-gradient(90deg, #a855f7, #6366f1) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        padding: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.2) !important;
    }}
    .stButton>button:hover {{
        box-shadow: 0 0 30px rgba(168, 85, 247, 0.4) !important;
        transform: scale(1.02) translateY(-2px) !important;
        background: linear-gradient(90deg, #6366f1, #a855f7) !important;
    }}

    /* Animations */
    @keyframes neon-pulse {{
        0% {{ transform: scale(1); filter: drop-shadow(0 0 2px #22d3ee); }}
        50% {{ transform: scale(1.05); filter: drop-shadow(0 0 10px #22d3ee); }}
        100% {{ transform: scale(1); filter: drop-shadow(0 0 2px #22d3ee); }}
    }}
    
    @keyframes fadeSlideUp {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .fade-in {{ animation: fadeSlideUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; }}
    
    .loading-pulse {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px;
    }}
    .pulse-emoji {{ font-size: 4rem; animation: neon-pulse 1.5s infinite ease-in-out; }}

    /* History Chips */
    .history-chip {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 8px 12px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.85rem;
    }}

    /* Intelligence Panel */
    .intel-panel {{
        background: rgba(168, 85, 247, 0.05);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(168, 85, 247, 0.1);
        border-radius: 24px;
        padding: 24px;
        margin-top: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }}

    .donut-container {{
        width: 140px;
        height: 140px;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    .donut-ring {{
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: conic-gradient(
            #a855f7 0deg var(--p-angle), 
            #22d3ee var(--p-angle) var(--c-angle), 
            #6366f1 var(--c-angle) 360deg
        );
        box-shadow: inset 0 0 15px rgba(0,0,0,0.5);
    }}

    .donut-center {{
        position: absolute;
        width: 75%;
        height: 75%;
        background: #050505;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 2;
    }}

    .score-badge {{
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        width: 80px;
        height: 80px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 8px;
    }}

    .dot-line {{
        display: flex;
        gap: 4px;
        margin-top: 4px;
    }}

    .dot {{ width: 8px; height: 8px; border-radius: 50%; background: rgba(255,255,255,0.1); }}
    .dot-active {{ background: #22d3ee; box-shadow: 0 0 5px #22d3ee; }}

    .goal-tag {{
        background: rgba(34, 197, 94, 0.1);
        color: #4ade80;
        padding: 4px 12px;
        border-radius: 100px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        border: 1px solid rgba(34, 197, 94, 0.2);
        display: inline-block;
    }}

    .xp-badge {{
        color: #fbbf24;
        font-size: 0.75rem;
        font-weight: 700;
        background: rgba(245, 158, 11, 0.1);
        padding: 2px 6px;
        border-radius: 6px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- App Logic ---

def get_api_key():
    """Retrieve API key from secrets or environment safely."""
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        pass
    return os.getenv("GOOGLE_API_KEY")

def encode_image(image_bytes):
    """Encodes image bytes to base64 string."""
    return base64.b64encode(image_bytes).decode('utf-8')

import textwrap

# --- React-Style UI Components ---

def Debugger(data):
    """Injects console logs into the browser for forensic debugging."""
    js_log = f"""
    <script>
        console.log("Forensic Debugger Active:");
        console.log("Data Type: {type(data)}");
        console.log("Payload:", {json.dumps(data)});
    </script>
    """
    st.markdown(js_log, unsafe_allow_html=True)

def IntelligencePanel(res):
    """Renders the Smart Nutrition Intelligence Dashboard in col1."""
    import textwrap
    p_pct = res.get("protein_pct", 20)
    c_pct = res.get("carbs_pct", 40)
    f_pct = res.get("fat_pct", 40)
    p_angle = (p_pct / 100) * 360
    c_angle = p_angle + ((c_pct / 100) * 360)

    html = textwrap.dedent(f"""
    <div class="intel-panel fade-in">
        <div style="display: flex; gap: 25px; align-items: center; margin-bottom: 20px;">
            <div class="donut-container">
                <div class="donut-ring" style="--p-angle: {p_angle}deg; --c-angle: {c_angle}deg;"></div>
                <div class="donut-center">
                    <span style="font-size: 1.2rem; font-weight: 800; color: #f8fafc;">{res['calories']}</span>
                    <span style="font-size: 0.6rem; color: #64748b; letter-spacing: 1.5px;">KCAL</span>
                </div>
            </div>
            <div style="flex: 1;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
                    <span class="material-icons" style="color: #a855f7; font-size: 18px;">bolt</span>
                    <span style="font-weight: 700; font-size: 0.9rem; color: #f8fafc;">Intelligence Panel</span>
                </div>
                <p style="color: #64748b; font-size: 0.8rem; margin: 0;">AI Nutritionist reasoning active.</p>
                <div style="margin-top: 10px; font-size: 0.75rem; color: #94a3b8; display: flex; flex-direction: column; gap: 4px;">
                    <div style="display: flex; justify-content: space-between;"><span>Carbs {res.get('carbs_g')}g</span> <span style="color: #6366f1;">({c_pct}%)</span></div>
                    <div style="display: flex; justify-content: space-between;"><span>Protein {res.get('protein_g')}g</span> <span style="color: #22d3ee;">({p_pct}%)</span></div>
                    <div style="display: flex; justify-content: space-between;"><span>Fat {res.get('fat_g')}g</span> <span style="color: #a855f7;">({f_pct}%)</span></div>
                </div>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 15px;">
            <div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="material-icons" style="color: #22d3ee; font-size: 14px;">favorite</span>
                    <span style="font-size: 0.75rem; font-weight: 600; color: #94a3b8;">Meal Score</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px; margin-top: 5px;">
                    <div class="score-badge">
                        <span style="font-size: 1.2rem; font-weight: 800; color: #f8fafc;">{res.get('meal_score', 7.5)}</span>
                        <span style="font-size: 0.5rem; color: #64748b;">/ 10</span>
                    </div>
                    <div>
                        <div style="font-size: 0.85rem; font-weight: 700; color: #4ade80;">{res.get('meal_type_label', 'Good Choice!')}</div>
                        <div class="goal-tag" style="margin-top: 4px;">{res.get('goal_compatibility', 'Maintenance')}</div>
                    </div>
                </div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.7rem; color: #94a3b8;"><span>Energy</span> <span>{res.get('energy_score')}</span></div>
                    <div class="dot-line"><div class="dot dot-active"></div><div class="dot dot-active"></div><div class="dot {'dot-active' if res.get('energy_score') == 'High' else ''}"></div></div>
                </div>
                <div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.7rem; color: #94a3b8;"><span>Satiety</span> <span>{res.get('satiety_score')}</span></div>
                    <div class="dot-line"><div class="dot dot-active"></div><div class="dot {'dot-active' if res.get('satiety_score') != 'Low' else ''}"></div><div class="dot {'dot-active' if res.get('satiety_score') == 'High' else ''}"></div></div>
                </div>
            </div>
        </div>
        <div style="margin-top: 20px; padding: 12px; background: rgba(34, 211, 238, 0.05); border-radius: 12px; border-left: 3px solid #22d3ee;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;"><span class="material-icons" style="font-size: 14px; color: #22d3ee;">auto_awesome</span><span style="font-size: 0.75rem; font-weight: 700; color: #f8fafc;">SMART TIP</span></div>
            <p style="font-size: 0.75rem; color: #94a3b8; margin: 0; line-height: 1.4;">{res.get('smart_tip', 'Enjoy your meal in moderation.')}</p>
        </div>
    </div>
    """).strip()
    return html

def MacroGrid(res):
    """Renders the top macro-nutrient cards in col2."""
    import textwrap
    conf = res.get('confidence', 'Medium')
    badge_class = f"badge-{conf.lower()}"
    
    html = textwrap.dedent(f"""
    <div class="fade-in">
        <div style="display: flex; align-items: baseline; gap: 15px; margin-bottom: 25px;">
            <h2 style="margin: 0; background: linear-gradient(90deg, #a855f7, #22d3ee); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.5px;">{res['dish_identified']}</h2>
            <span class="badge {badge_class}">{conf} Confidence</span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px;">
            <div class="macro-card" style="border-top: 2px solid #a855f7;"><div class="label"><span class="material-icons" style="font-size:14px; color:#a855f7">local_fire_department</span> CALORIES</div><div class="val">{res["calories"]}</div><div class="unit">kcal</div></div>
            <div class="macro-card" style="border-top: 2px solid #22d3ee;"><div class="label"><span class="material-icons" style="font-size:14px; color:#22d3ee">restaurant</span> PROTEIN</div><div class="val">{res.get("protein_g", 0)}</div><div class="unit">grams</div></div>
            <div class="macro-card" style="border-top: 2px solid #6366f1;"><div class="label"><span class="material-icons" style="font-size:14px; color:#6366f1">breakfast_dining</span> CARBS</div><div class="val">{res.get("carbs_g", 0)}</div><div class="unit">grams</div></div>
            <div class="macro-card" style="border-top: 2px solid #0ea5e9;"><div class="label"><span class="material-icons" style="font-size:14px; color:#0ea5e9">eco</span> FAT</div><div class="val">{res.get("fat_g", 0)}</div><div class="unit">grams</div></div>
        </div>
        <div class="gradient-divider" style="opacity: 0.1; margin-bottom: 25px;"></div>
    </div>
    """).strip()
    return html

def HealthInsights(res):
    """Maps the insights list into a clean structured list."""
    import textwrap
    insights_html = ""
    for insight in res.get("health_insight", []):
        insights_html += textwrap.dedent(f"""
            <div class="insight-card">
                <span class="material-icons" style="color:#a855f7; font-size: 20px;">tips_and_updates</span>
                <span style="color: #cbd5e1; font-size: 0.95rem;">{insight}</span>
            </div>
        """).strip()
    
    optimizer_html = textwrap.dedent(f"""
        <div class="swap-card">
            <div style="font-weight: 700; color: #22d3ee; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">
                <span class="material-icons" style="font-size: 18px;">auto_awesome</span> AI OPTIMIZER
            </div>
            <div style="color: #94a3b8; font-size: 0.95rem; line-height: 1.6;">{res.get('better_option', 'N/A')}</div>
        </div>
    """).strip()

    forensic_html = ""
    if res.get('accuracy_check'):
        forensic_html = textwrap.dedent(f"""
            <div style="margin-top: 15px; padding: 10px 15px; background: rgba(34, 197, 94, 0.05); border: 1px solid rgba(34, 197, 94, 0.2); border-radius: 12px; font-size: 0.8rem; color: #4ade80;">
                <b>🔍 Forensic Note:</b> {res['accuracy_check']}
            </div>
        """).strip()

    # Wrap in a single parent div with NO leading whitespace
    return f'<div class="fade-in"><h3 style="color:#f8fafc; font-size:1.2rem; margin-bottom:15px;">💡 AI Insights</h3>{insights_html}{optimizer_html}{forensic_html}</div>'

def BurnChallenge(res):
    """Renders the gamified burn plan center."""
    total_cal = res.get("calories", 0)
    burn_activities = [
        ("Brisk Walking", "🚶", 4, "#a855f7", "Easy", 60),
        ("Running", "🏃", 12, "#f43f5e", "Medium", 100),
        ("Cycling", "🚴", 9, "#10b981", "Medium", 80),
        ("Skipping", "➰", 13, "#6366f1", "Hard", 120),
        ("Cricket Match", "🏏", 8, "#22d3ee", "Hard", 150)
    ]
    
    activities_html = ""
    for label, icon, factor, color, level, xp in burn_activities:
        mins = round(total_cal / factor)
        prog = min(100, (factor * 8)) 
        activities_html += textwrap.dedent(f"""
            <div style="margin-bottom: 18px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 1.2rem;">{icon}</span>
                        <span style="font-weight: 600; font-size: 0.9rem; color: #cbd5e1;">{label}</span>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 0.85rem; font-weight: 700; color: #f8fafc;">{mins} min</div>
                        <div style="font-size: 0.7rem; color: #64748b;">{level}</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="flex: 1; height: 6px; background: rgba(255,255,255,0.05); border-radius: 10px; overflow: hidden;">
                        <div style="width: {prog}%; height: 100%; background: {color}; box-shadow: 0 0 10px {color}44;"></div>
                    </div>
                    <span class="xp-badge">+{xp} XP</span>
                </div>
            </div>
        """).strip()

    html = textwrap.dedent(f"""
    <div style="background: rgba(15, 15, 18, 0.4); border: 1px solid rgba(168, 85, 247, 0.1); border-radius: 20px; padding: 25px; margin-top: 30px;" class="fade-in">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span class="material-icons" style="color: #f43f5e; font-size: 24px;">rocket_launch</span>
                <h3 style="margin: 0; font-size: 1.2rem;">Gamified Burn Plan</h3>
            </div>
            <span style="font-size: 0.8rem; color: #64748b;">Burn {total_cal} kcal</span>
        </div>
        {activities_html}
    </div>
    """).strip()
    return html

@st.cache_data
def analyze_food_image(image_bytes):
    """Sends a request to Grok Cloud (X.AI) and returns parsed JSON."""
    api_key = get_api_key()
    if not api_key:
        st.error("Missing API Key. Please set GOOGLE_API_KEY in your .env file.")
        return None

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    system_prompt = """
    ROLE: You are the "Elite Desi Nutrition Architect." You possess expert-level knowledge of South Asian culinary techniques, regional ingredients, and the nutritional variances between home-cooked (Ghar ka) and commercial (Bahar ka) food.

    CORE OBJECTIVE: Provide forensic-level calorie and macronutrient estimations for Desi dishes. Account for high oil/fat saturation typical in South Asian cooking.

    1. ANALYSIS DIMENSIONS:
    - Fat Profile: Distinguish between Desi Ghee, Vanaspati, and Seed Oils.
    - "Tarka/Raunq" Factor: Identify if Lean (Tandoori), Standard (Home Style), or Restaurant Style (floating fat).
    - Carb Density: Differentiate between Chakki Atta, Maida, and Basmati.
    - Protein Quality: Distinguish lean cuts vs. high-fat cuts.

    2. INTELLIGENCE METRICS:
    - meal_score: 1.0 to 10.0 based on nutritional balance.
    - meal_type_label: "Balanced Choice", "Heavy Meal", "High Protein", etc.
    - Sub-metrics: Energy, Satiety, and Nutrient Density (Must be "High", "Medium", or "Low").
    - Goal compatibility: "Weight Loss", "Muscle Gain", or "Maintenance".
    - Smart Tip: One short (10-12 words) actionable tip.

    3. TONE: Professional, brutally honest about health impacts, culturally attuned.

    OUTPUT FORMAT (STRICT JSON):
    {
      "is_food": true,
      "dish_identified": "Name (Style: Home/Restaurant)",
      "calories": 720,
      "protein_g": 37,
      "carbs_g": 42,
      "fat_g": 43,
      "protein_pct": 21,
      "carbs_pct": 23,
      "fat_pct": 56,
      "meal_score": 7.5,
      "meal_type_label": "Good Choice",
      "energy_score": "High",
      "satiety_score": "High",
      "nutrient_density": "Medium",
      "goal_compatibility": "Maintenance",
      "smart_tip": "Pair with a side salad or raita for better fiber balance.",
      "confidence": "High/Medium/Low",
      "health_insight": ["Forensic insight 1", "Forensic insight 2"],
      "better_option": "Suggestion based on forensic detail",
      "accuracy_check": "Specific detail noticed (e.g. bone-in meat)"
    }
    If not food: {"is_food": false, "message": "Reason..."}
    """

    try:
        base64_image = encode_image(image_bytes)
        
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this food image and provide nutrition details in JSON format."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                },
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        # Fallback error handling if structure changes
        return {"is_food": False, "message": f"Error calling API: {str(e)}"}

# --- UI Setup ---

def main():
    # Initialize Session State
    if 'uploaded_file' not in st.session_state: st.session_state.uploaded_file = None

    # Header Section
    st.markdown('<h1 class="header-title">🍲 Desi Calorie & Nutrition Detector</h1>', unsafe_allow_html=True)
    st.markdown('<p class="header-tagline">Studio-grade AI Nutrition Analysis for South Asian Cuisine</p>', unsafe_allow_html=True)
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # --- Main Analysis Logic ---
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        # Antigravity UX: Uploader vanishes after selection
        if st.session_state.uploaded_file is None:
            file = st.file_uploader(
                "Drop your food photo here", 
                type=["jpg", "jpeg", "png"],
                help="Supports JPG, PNG"
            )
            if file:
                st.session_state.uploaded_file = file
                st.rerun()
        else:
            # Hero Image with Overlays
            st.markdown(f'''
                <div style="position: relative; border-radius: 28px; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.5);">
                    <img src="data:image/png;base64,{encode_image(st.session_state.uploaded_file.getvalue())}" style="width: 100%; display: block;">
                    <div style="position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(0deg, rgba(0,0,0,0.8), transparent); padding: 40px 20px 20px;">
                        <p style="color: white; margin: 0; font-weight: 600; font-size: 1.2rem;">Image ready for analysis</p>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
            
            # Action Buttons
            st.markdown("<br>", unsafe_allow_html=True)
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("🔍 Analyze Meal"):
                    loading_placeholder = st.empty()
                    messages = [
                        ("🥗", "Deconstructing spices..."),
                        ("🔥", "Scanning for oils..."),
                        ("🕌", "AI Nutritionist active..."),
                        ("🍲", "Finalizing your macro-profile...")
                    ]
                    for emoji, msg in messages[:-1]:
                        loading_placeholder.markdown(f'<div class="loading-pulse"><div class="pulse-emoji">{emoji}</div><p style="font-weight: 600; font-size: 1.2rem; background: linear-gradient(90deg, #a855f7, #22d3ee); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{msg}</p></div>', unsafe_allow_html=True)
                        time.sleep(1)
                    
                    result = analyze_food_image(st.session_state.uploaded_file.getvalue())
                    loading_placeholder.empty()
                    st.session_state['analysis_result'] = result
            
            with btn_col2:
                if st.button("🗑️ Clear Image"):
                    st.session_state.pop('analysis_result', None)
                    st.session_state.uploaded_file = None
                    st.rerun()

            # --- Smart Nutrition Intelligence Panel ---
            if 'analysis_result' in st.session_state:
                res = st.session_state['analysis_result']
                if res.get("is_food"):
                    # Forensic Debugging
                    Debugger(res)
                    # Component Rendering
                    st.markdown(IntelligencePanel(res), unsafe_allow_html=True)

    with col2:
        if 'analysis_result' in st.session_state:
            res = st.session_state['analysis_result']
            
            if res and res.get("is_food"):
                # Component Rendering
                st.markdown(MacroGrid(res), unsafe_allow_html=True)
                st.markdown(HealthInsights(res), unsafe_allow_html=True)
                st.markdown(BurnChallenge(res), unsafe_allow_html=True)

            elif res:
                st.markdown(f"""
                    <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid #f59e0b; padding: 25px; border-radius: 15px; text-align: center;">
                        <span class="material-icons" style="font-size: 48px; color: #f59e0b; margin-bottom: 10px;">info</span>
                        <p style="font-weight: 600; font-size: 1.1rem;">{res.get("message", "We couldn't detect a food item. Please upload a clear photo of your meal.")}</p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="background: rgba(255, 255, 255, 0.02); border: 1px dashed rgba(255, 255, 255, 0.1); padding: 60px; border-radius: 20px; text-align: center; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                    <span class="material-icons" style="font-size: 64px; color: rgba(255,255,255,0.1); margin-bottom: 20px;">restaurant_menu</span>
                    <p style="font-weight: 600; font-size: 1.2rem; color: #94a3b8;">Your nutrition breakdown will appear here</p>
                    <p style="font-size: 0.9rem; color: #64748b;">Upload a food photo and hit Analyze</p>
                </div>
            """, unsafe_allow_html=True)

    # Footer
    st.markdown('<div class="gradient-divider" style="margin-top: 50px;"></div>', unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; padding-bottom: 40px;">
            <p style="color: #64748b; font-size: 0.8rem; margin-bottom: 5px;">Disclaimer: AI estimates are for informational purposes only. Credits: Grok Vision.</p>
            <p style="color: #94a3b8; font-weight: 600;">Made with ❤️ for Desi food lovers</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
