import streamlit as st

NAV_ITEMS = [
    ("home",      "🏠 Home"),
    ("recommend", "🎯 Get Matched"),
    ("dashboard", "📊 Dashboard"),
    ("theory",    "📐 Theory"),
]


def render_topnav():
    current = "home"
    if "page" in st.session_state:
        current = st.session_state["page"]

    # Style radio buttons to look exactly like a navbar
    st.markdown("""
    <style>
    /* Hide default radio circle */
    div[data-testid="stRadio"] > label { display: none; }
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        gap: 6px !important;
        align-items: center !important;
        flex-wrap: nowrap !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        display: flex !important;
        align-items: center !important;
        padding: 7px 18px !important;
        border-radius: 999px !important;
        border: 1.5px solid #e0dfdc !important;
        background: transparent !important;
        color: #3D3D3D !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        white-space: nowrap !important;
        transition: all 0.15s ease !important;
        margin: 0 !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
        background: #0A66C2 !important;
        color: white !important;
        border-color: #0A66C2 !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(10,102,194,0.25) !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover:not(:has(input:checked)) {
        background: #EBF3FB !important;
        border-color: #0A66C2 !important;
        color: #004182 !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label > div {
        display: none !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label > p {
        margin: 0 !important;
        font-size: 13px !important;
        line-height: 1 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    col_brand, col_nav, col_badge = st.columns([2, 5, 1.8])

    with col_brand:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:8px;padding:6px 0;">'
            '<span style="width:30px;height:30px;background:#0A66C2;color:white;border-radius:5px;'
            'display:inline-flex;align-items:center;justify-content:center;'
            'font-weight:900;font-size:16px;flex-shrink:0;">in</span>'
            '<span style="font-size:15px;font-weight:700;color:#0D0D0D;white-space:nowrap;">'
            'CareerMatch</span></div>',
            unsafe_allow_html=True)

    with col_nav:
        labels = [label for _, label in NAV_ITEMS]
        keys   = [key   for key, _ in NAV_ITEMS]
        current_label = next(l for k, l in NAV_ITEMS if k == current)
        selection = st.radio(
            "nav", labels,
            index=labels.index(current_label),
            horizontal=True,
            label_visibility="collapsed",
            key="navbar_radio"
        )
        if selection:
            selected_key = keys[labels.index(selection)]
            if selected_key != current:
                st.session_state["page"] = selected_key
                if selected_key == "recommend":
                    st.session_state["step"] = 1
                st.rerun()

    with col_badge:
        st.markdown(
            '<div style="text-align:right;padding:6px 0;">'
            '<span style="font-size:11px;color:#9CA3AF;background:#F9F9F8;'
            'border:1px solid #E9E8E4;border-radius:999px;padding:4px 10px;'
            'white-space:nowrap;">ETS Data Mining</span></div>',
            unsafe_allow_html=True)

    st.markdown(
        '<hr style="border:none;border-top:1px solid #E9E8E4;margin:4px 0 20px;">',
        unsafe_allow_html=True)