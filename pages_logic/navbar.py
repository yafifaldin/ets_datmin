import streamlit as st

NAV_ITEMS = [
    ("home",      "🏠", "Home"),
    ("recommend", "🎯", "Get Matched"),
    ("dashboard", "📊", "Dashboard"),
    ("theory",    "📐", "Theory"),
]

def render_topnav():
    current = "home"
    if "page" in st.session_state:
        current = st.session_state["page"]

    st.markdown("""<style>
    /* Global button pill shape */
    .stButton > button {
        border-radius: 999px !important;
        height: 38px !important;
        font-size: 13px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        padding: 0 14px !important;
        box-shadow: none !important;
        transform: none !important;
        min-width: 0 !important;
        width: 100% !important;
    }
    .stButton > button[kind="primary"] {
        background: #0A66C2 !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #004182 !important;
        transform: none !important;
        box-shadow: none !important;
    }
    .stButton > button[kind="secondary"] {
        background: white !important;
        border: 1.5px solid #e0dfdc !important;
        color: #3D3D3D !important;
        font-weight: 500 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: #EBF3FB !important;
        border-color: #0A66C2 !important;
        color: #004182 !important;
        transform: none !important;
        box-shadow: none !important;
    }
    /* Navbar container */
    div[data-testid="stHorizontalBlock"]:first-of-type {
        background: white;
        border: 1px solid rgba(0,0,0,0.09);
        border-radius: 12px;
        padding: 8px 16px;
        margin-bottom: 20px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.07);
        align-items: center !important;
    }
    </style>""", unsafe_allow_html=True)

    c0, c1, c2, c3, c4, c5 = st.columns([2, 1, 1.3, 1.1, 1, 1.6])

    with c0:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:8px;padding:3px 0;">'
            '<span style="width:28px;height:28px;background:#0A66C2;color:white;'
            'border-radius:4px;display:inline-flex;align-items:center;'
            'justify-content:center;font-weight:900;font-size:14px;">in</span>'
            '<b style="font-size:15px;color:#0D0D0D;">CareerMatch</b></div>',
            unsafe_allow_html=True)

    for col, (key, icon, label) in zip([c1,c2,c3,c4], NAV_ITEMS):
        with col:
            t = "primary" if current == key else "secondary"
            if st.button(f"{icon} {label}", key=f"nav__{key}", type=t,
                         use_container_width=True):
                st.session_state["page"] = key
                if key == "recommend":
                    st.session_state["step"] = 1
                st.rerun()

    with c5:
        st.markdown(
            '<div style="text-align:right;padding:3px 0;">'
            '<span style="font-size:11px;color:#9CA3AF;background:#F9F9F8;'
            'border:1px solid #E9E8E4;border-radius:999px;padding:4px 10px;'
            'white-space:nowrap;">ETS Data Mining</span></div>',
            unsafe_allow_html=True)
