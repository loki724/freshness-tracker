import streamlit as st
from auth.authentication import get_current_user

def render_profile():
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; color: #f8fafc;">
            👤 User Profile
        </h1>
    </div>
    """, unsafe_allow_html=True)

    user = get_current_user()
    if user:
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 24px; max-width: 500px;">
            <div style="font-size: 3rem; margin-bottom: 8px;">👨‍🍳</div>
            <h3 style="margin: 0; color: #f8fafc;">{user.get('full_name')}</h3>
            <div style="color: #10b981; font-weight: 700; margin-top: 4px;">🏷️ {user.get('role')}</div>
            <div style="color: #94a3b8; font-size: 0.9rem; margin-top: 12px;">
                Email: <strong style="color: #f8fafc;">{user.get('email')}</strong>
            </div>
            <div style="color: #94a3b8; font-size: 0.9rem; margin-top: 4px;">
                Phone: <strong style="color: #f8fafc;">{user.get('phone') or 'Not provided'}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Not currently logged in.")
