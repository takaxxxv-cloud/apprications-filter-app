import streamlit as st
import pandas as pd
import plotly.express as px

# ページの設定
st.set_page_config(page_title="Swift Extract", page_icon="🥂", layout="wide")

# ==========================================
# 💎 カスタムCSS（ブラック＆ゴールド）
# ==========================================
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@300;400;600&display=swap');

    html, body, [class*="css"] { font-family: 'Noto Serif JP', serif !important; }
    .stApp { background-color: #0A0A0A; color: #F2F2F2; }
    [data-testid="stSidebar"] { background-color: #141414 !important; border-right: 1px solid #332918; }
    
    div[data-testid="stMetricValue"] { color: #C5A059 !important; font-weight: 600; }
    
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
st.markdown("<p style='color: #8C8C8C; font-size: 1.1rem; letter-spacing: 1px;'>催促リスト抽出・分析ダッシュボード</p>", unsafe_allow_html=True)
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
    
    st.sidebar.markdown("<div style='color: #C5A059; font-size: 0.95rem; margin-top: -10px; margin-bottom: 20px;'>✔️ 読み込み完了</div>", unsafe_allow_html=True)
    
    required_columns = ['割当口数', '状態', '入金額']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        err_msg = f"<div style='color: #B35B5B; border-left: 3px solid #B35B5B; padding-left: 10px;'>エラー: 以下の項目が見つかりません<br>{', '.join(missing_columns)}</div>"
        st.sidebar.markdown(err_msg, unsafe_allow_html=True)
    
    else:
        # ==========================================
        # 💡 データ全体の前処理（グラフにも使うため先に処理）
        # ==========================================
        df['割当口数'] = df['割当口数'].astype(str).str.replace(',', '', regex=False).str.replace('，', '', regex=False)
        df['割当口数'] = pd.to_numeric(df['割当口数'], errors='coerce').fillna(0)
        
        df['入金額'] = df['入金額'].astype(str)
        for sym in [',', '，', '¥', '￥', '円']:
            df['入金額'] = df['入金額'].str.replace(sym, '', regex=False)
        df['入金額'] = pd.to_numeric(df['入金額'], errors='coerce').fillna(0)

        # ==========================================
        # 📊 全体サマリーダッシュボード
        # ==========================================
        st.markdown("<h3 style='color: #F2F2F2; font-weight: 300;'>📊 全体サマリー</h3>", unsafe_allow_html=True)
        
        # 上段：全体KPIメトリクス
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(label="総リスト登録数", value=f"{len(df)} 名")
        with m2:
            st.metric(label="総割当口数", value=f"{df['割当口数'].sum():,.0f} 口")
        with m3:
            st.metric(label="総入金額", value=f"¥ {df['入金額'].sum():,.0f}")
        
        # 中段：グラフエリア
        c1, c2 = st.columns(2)
        
        with c1:
            # ドーナツグラフ（状態の割合）
            status_counts = df['状態'].value_counts().reset_index()
            status_counts.columns = ['状態', '人数']
            fig_pie = px.pie(status_counts, names='状態', values='人数', hole=0.7)
            fig_pie.update_layout(
                title=dict(text='ステータス分布', font=dict(color='#C5A059')),
                paper_bgcolor='rgba(0,0,0,0)', # 背景透過
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#8C8C8C'),
                margin=dict(t=50, b=20, l=20, r=20)
            )
            # ゴールドやグレーのグラデーションカラーを設定
            fig_pie.update_traces(marker=dict(colors=['#C5A059', '#8C8C8C', '#4A4A4A', '#2B2B2B']))
            st.plotly_chart(fig_pie, use_container_width=True)

        with c2:
            # 棒グラフ（状態ごとの割当口数）
            shares_by_status = df.groupby('状態')['割当口数'].sum().reset_index()
            fig_bar = px.bar(shares_by_status, x='状態', y='割当口数', text_auto=True)
            fig_bar.update_layout(
                title=dict(text='ステータス別 割当口数', font=dict(color='#C5A059')),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#8C8C8C'),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#333333'),
                margin=dict(t=50, b=20, l=20, r=20)
            )
            fig_bar.update_traces(marker_color='#C5A059')
            st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        # ==========================================
        # 🎯 抽出アクション
        # ==========================================
        st.sidebar.divider()
        target_type = st.sidebar.radio(
            "2. 抽出対象の選択",
            ["未選択", "出資未確定者リスト", "未入金者リスト"]
        )

        if target_type != "未選択":
            if target_type == "出資未確定者リスト":
                filtered_df = df[(df['割当口数'] != 0) & (df['状態'] == '応募')]
            elif target_type == "未入金者リスト":
                filtered_df = df[(df['割当口数'] != 0) & (df['状態'] == '同意') & (df['入金額'] == 0)]

            st.markdown(f"<h3 style='color: #F2F2F2; font-weight: 300;'>📋 {target_type} の抽出結果</h3>", unsafe_allow_html=True)
            
            f1, f2 = st.columns(2)
            with f1:
                st.metric(label="対象者数", value=f"{len(filtered_df)} 名")
            with f2:
                st.metric(label="対象割当口数 合計", value=f"{filtered_df['割当口数'].sum():,.0f} 口")
            
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
                st.markdown("<div style='border-left: 2px solid #C5A059; padding-left: 15px; color: #8C8C8C; margin-top: 20px;'>該当する対象者が0名でした。</div>", unsafe_allow_html=True)

else:
    st.markdown("<div style='border-left: 2px solid #C5A059; padding-left: 15px; color: #8C8C8C; margin-top: 20px;'>左側のパネルよりCSVファイルをアップロードしてください。</div>", unsafe_allow_html=True)
