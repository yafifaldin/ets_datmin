import streamlit as st

NAV_ITEMS = [
    ("home",      "Home"),
    ("recommend", "Get Matched"),
    ("dashboard", "Dashboard"),
    ("theory",    "Theory"),
]


def render_topnav():
    current = "home"
    if "page" in st.session_state:
        current = st.session_state["page"]

    st.markdown("""
    <style>
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem !important; }

    /* Navbar card */
    div[data-testid="stHorizontalBlock"]:first-of-type {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 8px 20px;
        margin-bottom: 24px;
        align-items: center !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    /* Nav buttons base */
    div[data-testid="stHorizontalBlock"]:first-of-type button {
        border-radius: 8px !important;
        height: 38px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        white-space: nowrap !important;
        border: none !important;
        box-shadow: none !important;
        transform: none !important;
        padding: 0 20px !important;
        width: auto !important;
        min-width: 100% !important;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type button[kind="secondary"] {
        background: transparent !important;
        color: #555 !important;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type button[kind="secondary"]:hover {
        background: #F3F4F6 !important;
        color: #111 !important;
        box-shadow: none !important;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type button[kind="primary"] {
        background: #0A66C2 !important;
        color: white !important;
        font-weight: 600 !important;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type button[kind="primary"]:hover {
        background: #004182 !important;
        box-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # layout=wide, screen ~1200px
    # brand=200px, 4 buttons ~130px each = 520px, filler = rest
    # In ratio: brand=2, each button=1.3, filler=rest
    c_brand, c1, c2, c3, c4, c_fill = st.columns([2, 1.5, 1.8, 1.6, 1.3, 2])

    with c_brand:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:10px;">'
            '<span style="width:32px;height:32px;background:#0A66C2;color:white;'
            'border-radius:6px;display:inline-flex;align-items:center;'
            'justify-content:center;font-weight:900;font-size:17px;flex-shrink:0;">in</span>'
            '<b style="font-size:16px;color:#111;white-space:nowrap;">CareerMatch</b>'
            '</div>',
            unsafe_allow_html=True)

    for col, (key, label) in zip([c1, c2, c3, c4], NAV_ITEMS):
        with col:
            t = "primary" if current == key else "secondary"
            if st.button(label, key=f"nav__{key}", type=t,
                         use_container_width=True):
                st.session_state["page"] = key
                if key == "recommend":
                    st.session_state["step"] = 1
                st.rerun()

    with c_fill:
        st.markdown(
            '<div style="text-align:right;">'
            '<span style="font-size:11px;color:#9CA3AF;background:#F9F9F8;'
            'border:1px solid #E9E8E4;border-radius:999px;padding:4px 12px;'
            'white-space:nowrap;">ETS Data Mining</span></div>',
            unsafe_allow_html=True)