import streamlit as st
import pandas as pd

# ページの設定（タブのアイコンも追加）
st.set_page_config(page_title="Swift Extract", page_icon="🔋", layout="wide")

# ==========================================
# メイン画面（ヘッダー部分）
# ==========================================
st.title("🔋 Swift Extract")
st.markdown("#### 催促リスト抽出ツール")
st.write("左側のサイドバーからCSVをアップロードし、抽出したいリストを選択してください。")
st.divider() # 区切り線を入れてスッキリさせる

# ==========================================
# サイドバー（操作パネル）
# ==========================================
st.sidebar.header("⚙️ 操作パネル")
uploaded_file = st.sidebar.file_uploader("1. CSVファイルをアップロード", type="csv")

if uploaded_file is not None:
    # 文字コード対策
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding='shift_jis')
    
    st.sidebar.success("ファイルの読み込み成功！")
    
    required_columns = ['割当口数', '状態', '入金額']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"エラー: アップロードされたCSVに以下の項目名が見つかりません: {', '.join(missing_columns)}")
    
    else:
        st.sidebar.divider()
        
        target_type = st.sidebar.radio(
            "2. 作成するリストを選択",
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
            st.markdown(f"### 📋 {target_type} の抽出結果")
            
            # 数字をダッシュボード風に強調表示
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="対象者数", value=f"{len(filtered_df)} 名")
            with col2:
                total_kuchi = filtered_df['割当口数'].sum()
                st.metric(label="対象割当口数 合計", value=f"{total_kuchi:,.0f} 口")
            
            # データフレームの表示（画面幅に合わせて表示）
            st.dataframe(filtered_df, use_container_width=True)

            # ダウンロードボタンの配置
            if len(filtered_df) > 0:
                csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
                
                # 少し余白を空けてからボタンを配置
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button(
                    label=f"✅ {target_type}のCSVをダウンロード",
                    data=csv_data,
                    file_name=f"{target_type}.csv",
                    mime="text/csv",
                    type="primary"  # ボタンを目立たせる（テーマのメインカラーになる）
                )
            else:
                st.info("該当する対象者が0名でした。")

else:
    # ファイルがアップロードされる前のプレースホルダー
    st.info("👈 左側のサイドバーからCSVファイルをアップロードして開始してください。")
