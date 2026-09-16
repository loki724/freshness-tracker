import streamlit as st
from auth.authentication import login_user, authenticate_user, register_user

def render_landing_page():
    st.markdown("""
    <div class="hero-banner" style="text-align: center; padding: 40px 20px;">
        <div style="font-size: 3.5rem; margin-bottom: 8px;">🌱🥕🍲</div>
        <h1 style="font-size: 2.6rem; font-weight: 800; color: #10b981; margin: 0;">NourishAI</h1>
        <h3 style="color: #cbd5e1; font-weight: 500; margin-top: 6px;">Smart Vegetable Freshness & Food Waste Management System</h3>
        <p style="max-width: 680px; margin: 16px auto 0 auto; color: #94a3b8; font-size: 1.05rem; line-height: 1.6;">
            NourishAI helps <strong>Santhi Welfare Children Home</strong> manage donated vegetables, monitor freshness, prioritize food usage with FIFO cooking guidance, and reduce food waste so healthy meals reach children before food spoils.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display: flex; justify-content: space-around; flex-wrap: wrap; margin-bottom: 32px; text-align: center; gap: 16px;">
        <div style="background: rgba(30, 41, 59, 0.6); padding: 16px 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); flex: 1; min-width: 150px;">
            <div style="font-size: 1.8rem;">📦</div>
            <div style="font-weight: 700; color: #f8fafc; margin-top: 4px;">1. DONATE</div>
            <div style="font-size: 0.8rem; color: #94a3b8;">Log citizen donations</div>
        </div>
        <div style="background: rgba(30, 41, 59, 0.6); padding: 16px 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); flex: 1; min-width: 150px;">
            <div style="font-size: 1.8rem;">📷</div>
            <div style="font-weight: 700; color: #f8fafc; margin-top: 4px;">2. SCAN (AI)</div>
            <div style="font-size: 0.8rem; color: #94a3b8;">YOLOv8 Detection</div>
        </div>
        <div style="background: rgba(30, 41, 59, 0.6); padding: 16px 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); flex: 1; min-width: 150px;">
            <div style="font-size: 1.8rem;">⏳</div>
            <div style="font-weight: 700; color: #f8fafc; margin-top: 4px;">3. TRACK</div>
            <div style="font-size: 0.8rem; color: #94a3b8;">Estimated Use-By Date</div>
        </div>
        <div style="background: rgba(30, 41, 59, 0.6); padding: 16px 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); flex: 1; min-width: 150px;">
            <div style="font-size: 1.8rem;">🍲</div>
            <div style="font-weight: 700; color: #f8fafc; margin-top: 4px;">4. COOK FIRST</div>
            <div style="font-size: 0.8rem; color: #94a3b8;">FIFO Priority Guidance</div>
        </div>
        <div style="background: rgba(30, 41, 59, 0.6); padding: 16px 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); flex: 1; min-width: 150px;">
            <div style="font-size: 1.8rem;">📉</div>
            <div style="font-weight: 700; color: #f8fafc; margin-top: 4px;">5. ZERO WASTE</div>
            <div style="font-size: 0.8rem; color: #94a3b8;">Track & eliminate waste</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### 🔐 Kitchen Staff / Volunteer Login")
        with st.form("login_form"):
            email = st.text_input("Email Address", value="staff@nourishai.org")
            password = st.text_input("Password", type="password", value="staff123")
            submit = st.form_submit_button("Sign In to NourishAI", use_container_width=True)

            if submit:
                user, msg = authenticate_user(email, password)
                if user:
                    login_user(user)
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        
        st.caption("💡 **Demo Accounts:** Staff (`staff@nourishai.org` / `staff123`) | Volunteer (`volunteer@nourishai.org` / `volunteer123`)")

    with col2:
        st.markdown("### 📝 Register New Staff / Volunteer")
        with st.form("register_form"):
            reg_name = st.text_input("Full Name", placeholder="e.g. Ramesh Patel")
            reg_email = st.text_input("Email", placeholder="ramesh@community.org")
            reg_phone = st.text_input("Phone", placeholder="+91 98765 00000")
            reg_role = st.selectbox("Role", ["Kitchen Staff", "Volunteer"])
            reg_pwd = st.text_input("Password", type="password")
            reg_pwd_confirm = st.text_input("Confirm Password", type="password")
            reg_submit = st.form_submit_button("Create Account", use_container_width=True)

            if reg_submit:
                ok, reg_msg = register_user(reg_name, reg_email, reg_phone, reg_pwd, reg_pwd_confirm, reg_role)
                if ok:
                    st.success(reg_msg)
                else:
                    st.error(reg_msg)
