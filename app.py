import streamlit as st
import pandas as pd

# ページの設定
st.set_page_config(page_title="Swift Extract", page_icon="🥂", layout="wide")

# ==========================================
# 💎 カスタムCSSによる高級感の演出
# ==========================================
st.markdown("""
<style>
    /* Googleフォントから明朝体を読み込み */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@300;400;600&display=swap');

    /* 全体のフォントと背景色の設定 */
    html, body, [class*="css"] {
        font-family: 'Noto Serif JP', serif !important;
    }
    
    .stApp {
        background-color: #121212;
        color: #E0E0E0;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1A1A1A !important;
        border-right: 1px solid #333;
    }

    div[data-testid="stMetricValue"] {
        color: #D4AF37 !important; 
        font-weight: 600;
    }

    /* ダウンロードボタンの装飾を完全にゴールドへ統一 */
    div[data-testid="stDownloadButton"] > button {
        background-color: transparent !important;
        color: #D4AF37 !important;
        border: 1px solid #D4AF37 !important;
        border-radius: 2px !important;
        transition: all 0.3s ease;
        padding: 0.5rem 1rem;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        background-color: #D4AF37 !important;
        color: #121212 !important;
        border-color: #D4AF37 !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# メイン画面（ヘッダー部分）
# ==========================================
st.markdown("<h1 style='color: #D4AF37; font-weight: 300;'>Swift Extract</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #A0A0A0; font-size: 1.2rem;'>催促リスト抽出システム</p>", unsafe_allow_html=True)
st.divider()

# ==========================================
# サイドバー（操作パネル）
# ==========================================
st.sidebar.markdown("<h3 style='color: #D4AF37;'>操作パネル</h3>", unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("1. CSVファイルをアップロード", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
