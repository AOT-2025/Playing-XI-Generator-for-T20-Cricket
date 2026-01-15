import streamlit as st

# Page config
st.set_page_config(
    page_title="Cricket XI Predictor",
    page_icon="🏏",
    layout="centered"
)

# CSS styling including sidebar customization and updated button effects
from stylesheet import apply_custom_style1
apply_custom_style1()

# Sidebar content
st.sidebar.markdown("""
    <h2 style='color: white; font-size: 22px;'>Build Your Dream Team</h2>
    <p style='color: white; font-size: 16px;  text-align: justify'>You’ll find the <strong>System-Generated</strong> and <strong>Manual Selection</strong> buttons on the main page too.<br>
    We’ve added them here in the nav bar above so you can quickly jump to the selection page whenever you want — no need to scroll!<br><br>
    Feel free to start building your perfect team anytime. Let’s get going! ✨</p>
""", unsafe_allow_html=True)


# Header box
st.markdown("""
<div class="header-box">
    <h1>🏏 Optimal Playing XI Predictor</h1>
    <p>Smart and simple way to find the perfect cricket team</p>
</div>
""", unsafe_allow_html=True)

# Frosted body with welcome content
with st.container():
    st.markdown("""
    <div class="frosted-body">
        <p>
        Welcome to our Cricket Analytics app! 🎉 <br><br>
        Discover the <strong>optimal Playing XI</strong> tailored to match conditions and smart data-driven predictions.  
        <br><br>
        You can create your team in two simple ways:
        <ul>
            <li><strong>System Generated:</strong> Let our model automatically select the ideal team for you.</li>
            <li><strong>Manual Selection:</strong> Select the number of batters, spinners, pacers, all-rounders and more to build your perfect XI.</li>
        </ul>
        </p>
    """, unsafe_allow_html=True)

    # Buttons layout
    st.markdown('<div class="buttons-flex">', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    # System Generated button
    with col1:
        st.markdown('<div class="button-wrapper">', unsafe_allow_html=True)
        st.markdown("""
            <a href="/System_Generated" target="_self">
                <button class="button-style">🎯 System Generated</button>
            </a>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Manual Selection button
    with col2:
        st.markdown('<div class="button-wrapper">', unsafe_allow_html=True)
        st.markdown("""
            <a href="/Manual_Selection" target="_self">
                <button class="button-style">🛠️ Manual Selection</button>
            </a>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
 
