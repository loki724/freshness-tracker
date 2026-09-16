import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #0f172a 100%);
        color: #f3f4f6;
    }

    .hero-banner {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.05) 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        backdrop-filter: blur(12px);
    }

    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        transition: transform 0.2s ease, border-color 0.2s ease;
        backdrop-filter: blur(8px);
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(16, 185, 129, 0.4);
    }
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
    }
    .metric-value {
        font-size: 1.9rem;
        font-weight: 800;
        margin-top: 6px;
        color: #f8fafc;
    }
    .metric-subtitle {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 4px;
    }

    .urgent-banner {
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.2) 0%, rgba(185, 28, 28, 0.05) 100%);
        border-left: 5px solid #ef4444;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.25rem;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);
        transform: translateY(-1px);
    }

    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    </style>
    """, unsafe_allow_html=True)
