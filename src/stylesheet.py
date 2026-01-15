import streamlit as st

def apply_custom_style1():
    st.markdown("""
    <style>
    /* Sidebar background and text color */
    [data-testid="stSidebar"] {
        background-color: #17a2b8 !important;  /* Teal shade */
        color: white !important;
        padding: 20px;
    }

    /* Sidebar text */ 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] div {
        color: white !important;
        font-size: 20px !important;
    }

    [data-testid="stSidebar"] span
        {
        color: white !important;
        font-size: 21px !important;
    }
    /* Sidebar headings specifically */
    [data-testid="stSidebar"] h2 {
        font-size: 26px !important;
        font-weight: 800 !important;
    }

    /* Sidebar links color */
    [data-testid="stSidebar"] a {
        color: white !important;
        text-decoration: none;
        font-size: 24px !important;     
        font-weight: 800; 
    }

    [data-testid="stSidebar"] a:hover, [data-testid="stSidebar"] a:focus, [data-testid="stSidebar"] a:active {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.4), rgba(214, 241, 246, 0.1)) !important;
        transform: scale(1.03);
        box-shadow: 0 0 10px 3px rgba(255, 255, 255, 0.4);  
        font-weight: 900;
        text-decoration: none;
        border-radius: 6px;
        padding: 4px 8px;
    }


    /* Wider sidebar */
    [data-testid="stSidebar"] {
        min-width: 430px !important;
        max-width: 430px !important;
        padding-right: 0px !important;
        background-color: #17a2b8 !important;
        color: white !important;
        box-shadow: 4px 0 10px rgba(0, 0, 0, 0.1);
    }

    /* Sidebar scrollable area */
    [data-testid="stSidebar"] > div {
        height: 100vh;
        overflow-y: scroll !important;
        padding-right: 20px;
    }

    /* White thin scrollbar */
    [data-testid="stSidebar"] > div::-webkit-scrollbar {
        width: 10px;
        background-color: transparent;
    }

    [data-testid="stSidebar"] > div::-webkit-scrollbar-track {
        background: transparent;
    }

    [data-testid="stSidebar"] > div::-webkit-scrollbar-thumb {
        background-color: white;
        border-radius: 12px;
        border: 2px solid transparent;
        background-clip: content-box;
    }

    [data-testid="stSidebar"] > div::-webkit-scrollbar-thumb:hover {
        background-color: #cccccc;
    }

    /* Main page background */
    .stApp {
        background-image: url("https://t4.ftcdn.net/jpg/08/57/58/07/360_F_857580708_sBcXjt4G3l1mDQ6slwuhzfwg0KQz8JX8.jpg");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }


    /* Header styling */
    .header-box {
        background: rgba(255, 255, 255, 0.65);
        padding: 1.5rem;
        border-radius: 18px;
        text-align: center;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.3);
        margin: 2rem auto 1rem auto;
        max-width: 850px;
    }

    .header-box h1 {
        color: #0b5394;
        font-size: 42px;
        margin-bottom: 10px;
        font-weight: 800;
    }

    .header-box p {
        color: #444;
        font-size: 20px;
        font-weight: 500;
        margin-top: -10px;
    }

    /* Frosted body styling */
    .frosted-body {
        background: rgba(0, 0, 0, 0.65);
        padding: 2rem;
        border-radius: 18px;
        margin: 2rem auto 0.8rem auto;
        max-width: 850px;
        color: white !important;
        font-weight: 600;
        font-size: 18px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }

    .frosted-body p {
        color: white !important;
        font-size: 20px;
        line-height: 1.5;
        font-weight: 600;
        margin-bottom: 0.3rem; 
    }

    .frosted-body ul {
        margin-left: 1.3rem;
        margin-bottom: 1rem;
    }

    .frosted-body li {
        margin-bottom: 0.5rem;
    }

    /* Buttons container flex */
    .buttons-flex {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 0.2rem;
    }

    /* Button wrapper to control width */
    .button-wrapper {
        width: 180px;
    }

    /* Button style */
    .button-style {
        font-size: 20px;
        font-weight: 900;
        padding: 18px 40px;
        background: linear-gradient(135deg, #1db954, #17a2b8);
        color: white;
        border-radius: 12px;
        width: 100%;
        cursor: pointer;
        box-shadow: 0 4px 8px rgba(29, 185, 84, 0.6);
        border: 2px solid transparent;
        transition: all 0.35s ease;
        text-shadow: 0 1px 2px rgba(0,0,0,0.5);
        border: none;
        text-decoration: none; /* no underline by default */
    }
                

    /* Button hover effects: glow and bold */
    .button-style:hover {
        background: linear-gradient(135deg, #17a2b8, #1db954);
        transform: scale(1.08);
        box-shadow: 0 0 14px 4px rgba(23, 162, 184, 0.8);
        font-weight: 1000; 
        text-decoration: none; 
    }

    /* Remove underline on focus and active states */
    .button-style:focus,
    .button-style:active,
    .button-style:visited {
        text-decoration: none;
        outline: none; 
    }
                
    </style>
    """, unsafe_allow_html=True)
    
def apply_custom_style2():
    st.markdown("""
    <style>
    /* Sidebar background and text color */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500&display=swap');

    table {
        font-family: 'Poppins', sans-serif;
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
        margin-left: auto;
        margin-right: auto;
    }

    thead th {
        background-color: #007a8a; /* lighter teal */
        color: #ffffff;            /* white text */
        font-size: 19px;
        font-weight: 500;
        padding: 14px 25px;
        text-align: center;
        position: relative;
        user-select: none;
    }

    thead th:first-child {
        border-top-left-radius: 12px;
    }

    thead th:last-child {
        border-top-right-radius: 12px;
    }

    tbody td {
        background-color: #fff;
        font-size: 17px;
        color: #444;
        padding: 12px 25px;
        border-top: 1px solid #e5e5e5;
        transition: background-color 0.25s ease;
        text-align: left;
        font-weight: 400;
    }

    tbody tr:nth-child(even) td {
        background-color: #f7fbff;
    }

    tbody tr:hover td {
        background-color: #d7ebff;
        cursor: default;
    }

    tbody td.Position {
        text-align: center !important;
        font-weight: 500;
        color: #1a73e8;
    }
    [data-testid="stSidebar"]{
        background-color: #17a2b8 !important;  /* Teal shade */
        color: white !important;
        padding: 20px;
    }

    /* Sidebar text */ 
    [data-testid="stSidebar"] p ,[data-testid="stSidebar"] span{
        color: white !important;
        font-size: 20px !important;
    }
                    
    #To make Match Location and Pitch Type font black          
    [data-testid="stSidebar"] select option {
        color: black !important;
        background-color: white !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] > div:first-child {
        color: black !important;
        background-color: white !important;
    }
    [data-testid="stSidebar"] select {
        color: black !important;
        background-color: white !important;
    }       
                
    /* Sidebar headings specifically */
                
    section[data-testid="stSidebar"] h1 {
    font-size: 26px !important;
    font-weight: 900 !important;
    }

    /* Make all sidebar subheaders larger */
    section[data-testid="stSidebar"] h3 {
    font-size: 24px !important;
    font-weight: 800 !important;
    }            

    /* Sidebar links color */
    [data-testid="stSidebar"] a {
        color: white !important;
        text-decoration: none;
        font-size: 24px !important;     
        font-weight: 800; 
    }

    [data-testid="stSidebar"] a:hover, [data-testid="stSidebar"] a:focus, [data-testid="stSidebar"] a:active {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.4), rgba(214, 241, 246, 0.1)) !important;
        transform: scale(1.03);
        box-shadow: 0 0 10px 3px rgba(255, 255, 255, 0.4);  
        font-weight: 900;
        text-decoration: none;
        border-radius: 6px;
        padding: 4px 8px;
    }

    /* ---- Styling the Confirm Selection button ---- */
    button[kind="secondary"] {
        background: linear-gradient(135deg, #d4f9ff, #c3ecff) !important;  /* Very light blue gradient */
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        border: 2px solid #99dfff !important;  /* Soft cyan border */
        padding: 13px 26px !important;
        text-align: center !important;
        box-shadow: 0 0 15px 4px rgba(150, 220, 255, 0.8);  /* stronger glow */
        transition: all 0.3s ease-in-out;
        cursor: pointer;
    }

    button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #b3f0ff, #99dfff) !important;  /* slightly brighter on hover */
        box-shadow: 0 0 25px 6px rgba(135, 210, 255, 1);  /* more intense glow */
        transform: scale(1.05);
        border-color: #66ccff !important;
    }

    /* ---Button text colour change ---*/         
    /* 1) Catch the nested <div> inside each sidebar button */
    section[data-testid="stSidebar"] button > div > div {
        color: #1392a0 !important;
        font-weight: 700 !important;
    }

    /* 2) Fallback: any other elements inside a sidebar button */
    section[data-testid="stSidebar"] button * {
        color: #1392a0 !important;
        font-weight: 700 !important;
    }
                
    .confirm-msg {
    background-color: #b3ffb3;
    color: #006644;
    font-weight: bold;
    border-left: 6px solid #00cc66;
    padding: 12px;
    border-radius: 6px;
    margin-bottom: 10px;
    box-shadow: 0 0 8px rgba(0, 204, 102, 0.3);
    }
    .warning-msg {
    background-color: #ffe6e6;
    color: #990000;
    font-weight: bold;
    border-left: 6px solid #ff4d4d;
    padding: 12px;
    border-radius: 6px;
    margin-bottom: 10px;
    box-shadow: 0 0 8px rgba(255, 77, 77, 0.3);
    }
    .info-msg {
    background-color: #e0f7f9;
    color: #007c91;
    font-weight: bold;
    border-left: 6px solid #3399ff;
    padding: 12px;
    border-radius: 6px;
    margin-bottom: 10px;
    box-shadow: 0 0 8px rgba(51, 153, 255, 0.3);
    }  

    /* Wider sidebar */
    [data-testid="stSidebar"] {
        min-width: 430px !important;
        max-width: 430px !important;
        padding-right: 0px !important;
        background-color: #17a2b8 !important;
        color: white !important;
        box-shadow: 4px 0 10px rgba(0, 0, 0, 0.1);
    }

    /* Sidebar scrollable area */
    [data-testid="stSidebar"] > div {
        height: 100vh;
        overflow-y: scroll !important;
        padding-right: 20px;
    }

    /* White thin scrollbar */
    [data-testid="stSidebar"] > div::-webkit-scrollbar {
        width: 10px;
        background-color: transparent;
    }

    [data-testid="stSidebar"] > div::-webkit-scrollbar-track {
        background: transparent;
    }

    [data-testid="stSidebar"] > div::-webkit-scrollbar-thumb {
        background-color: white;
        border-radius: 12px;
        border: 2px solid transparent;
        background-clip: content-box;
    }

    [data-testid="stSidebar"] > div::-webkit-scrollbar-thumb:hover {
        background-color: #cccccc;
    }

    /* Main page background */
    .stApp {
        background-image: url("https://static.vecteezy.com/system/resources/thumbnails/007/784/841/small/health-and-science-medical-innovation-concept-abstract-geometric-futuristic-background-from-hexagons-pattern-light-blue-radiant-background-illustration-vector.jpg");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }
    [data-testid="stAppViewContainer"] {
        font-size: 20px !important;  /* Adjust as you like */
        line-height: 1.5 !important;
    }

    /* Increase headers sizes */
    h1 {
        font-size: 3rem !important;
    }
    h2 {
        font-size: 2.5rem !important;
    }
    h3 {
        font-size: 2rem !important;
    }
    h4 {
        font-size: 1.75rem !important;
    }
    h5 {
        font-size: 1.5rem !important;
    }
    h6 {
        font-size: 1.25rem !important;
    }

    /* Increase paragraph font size */
    p {
        font-size: 1.1rem !important;
    }

    </style>
    """, unsafe_allow_html=True)