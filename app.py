import streamlit as st
import pandas as pd

# ページの設定
st.set_page_config(page_title="Swift Extract", page_icon="🥂", layout="wide")

# ==========================================
# 💎 カスタムCSSによる高級感の演出（ブラック＆ゴールド）
# ==========================================
custom_css = """
<style>
    /* Googleフォントから明朝体を読み込み */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@300;400;600&display=swap');

    /* 全体のフォントと背景色の設定 */
    html, body, [class*="css"] {
        font-family: 'Noto Serif JP', serif !important;
    }
    
    /* より深い漆黒の背景色 */
    .stApp {
        background-color: #0A0A0A;
        color: #F2F2F2;
    }
    
    /* サイドバーの背景色とゴールドの区切り線 */
    [data-testid="stSidebar"] {
        background-color: #141414 !important;
        border-right: 1px solid #332918;
    }

    /* メトリクス（強調される数字）をシャンパンゴールドに */
    div[data-testid="stMetricValue"] {
        color: #C5A059 !important; 
        font-weight: 600;
    }

    /* ダウンロードボタンの装飾を完全にゴールドへ統一 */
    div[data-testid="stDownloadButton"] > button {
        background-color: transparent !important;
        color: #C5A059 !important;
        border: 1px solid #C5A059 !important;
        border-radius: 2px !important;
        transition: all 0.4s ease;
        padding: 0.5rem 1.5rem;
        letter-spacing: 1px;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        background-color: #C5A059 !important;
        color: #0A0A0A !important;
        border-color: #C5A059 !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# メイン画面（ヘッダー部分）
# ==========================================
st.markdown("<h1 style='color: #C5A059; font-weight: 300; letter-spacing: 2px;'>Swift Extract</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #8C8C8C; font-size: 1.1rem; letter-spacing: 1px;'>催促リスト抽出システム</p>", unsafe_allow_html=True)
st.divider()

# ==========================================
# サイドバー（操作パネル）
# ==========================================
st.sidebar.markdown("<h3 style='color: #C5A059; font-weight: 400;'>操作パネル</h3>", unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("1. CSVファイルをアップロード", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding='shift_jis')
    
    # 💡 成功メッセージ（構文エラー対策済）
    success_msg = "<div style='color: #C5A059; font-size: 0.95rem; margin-top: -10px; margin-bottom: 20px;'>✔️ ファイルの読み込みが完了しました</div>"
    st.sidebar.markdown(success_msg, unsafe_allow_html=True)
    
    required_columns = ['割当口数', '状態', '入金額']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        # 💡 エラーメッセージ（構文エラー対策済）
        err_msg = f"<div style='color: #B35B5B; border-left: 3px solid #B35B5B; padding-left: 10px;'>エラー: 以下の項目名が見つかりません<br>{', '.join(missing_columns)}</div>"
        st.sidebar.markdown(err_msg, unsafe_allow_html=True)
    
    else:
        st.sidebar.divider()
        
        target_type = st.sidebar.radio(
            "2. 抽出対象の選択",
            ["未選択", "出資未確定者リスト", "未入金者リスト"]
        )

        if target_type != "未選択":
            
            # --- 前処理（データクレンジング） ---
            df['割当口数'] = df['割当口数'].astype(str)
            df['割当口数'] = df['割当口数'].str.replace(',', '', regex=False).str.replace('，', '', regex=False)
            df['割当口数'] = pd.to_numeric(df['割当口数'], errors='coerce').fillna(0)
            
            df['入金額'] = df['入金額'].astype(str)
            symbols_to_remove = [',', '，', '¥', '￥', '円']
            for sym in symbols_to_remove:
                df['入金額'] = df['入金額'].str.replace(sym, '', regex=False)
            df['入金額'] = pd.to_numeric(df['入金額'], errors='coerce').fillna(0)
            # ----------------------------------------

            # フィルタリング
            if target_type == "出資未確定者リスト":
                filtered_df = df[(df['割当口数'] != 0) & (df['状態'] == '応募')]
                
            elif target_type == "未入金者リスト":
                filtered_df = df[(df['割当口数'] != 0) & (df['状態'] == '同意') & (df['入金額'] == 0)]

            # ==========================================
            # メイン画面（結果表示エリア）
            # ==========================================
            st.markdown(f"<h3 style='color: #F2F2F2; font-weight: 300;'>{target_type} の抽出結果</h3>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="対象者数", value=f"{len(filtered_df)} 名")
            with col2:
                total_kuchi = filtered_df['割当口数'].sum()
                st.metric(label="対象割当口数 合計", value=f"{total_kuchi:,.0f} 口")
            
            st.dataframe(filtered_df, use_container_width=True)

            if len(filtered_df) > 0:
                csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button(
                    label=f"CSVファイルをダウンロード",
                    data=csv_data,
                    file_name=f"{target_type}.csv",
                    mime="text/csv"
                )
            else:
                # 💡 対象者0名のメッセージ（構文エラー対策済）
                zero_msg = "<div style='border-left: 2px solid #C5A059; padding-left: 15px; color: #8C8C8C; margin-top: 20px;'>該当する対象者が0名でした。</div>"
                st.markdown(zero_msg, unsafe_allow_html=True)

else:
    # 💡 初期案内メッセージ（構文エラー対策済）
    info_msg = "<div style='border-left: 2px solid #C5A059; padding-left: 15px; color: #8C8C8C; margin-top: 20px;'>左側のパネルよりCSVファイルをアップロードしてください。</div>"
    st.markdown(info_msg, unsafe_allow_html=True)
