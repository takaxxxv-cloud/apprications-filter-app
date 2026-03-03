import streamlit as st
import pandas as pd

# ページの設定
st.set_page_config(page_title="InvEx Engine", layout="wide")

st.title("Swift Extract - 催促リスト抽出ツール")
st.write("CSVをアップロードして、抽出したいリストのボタンを押すだけで完了します。")

# 1. CSVファイルのアップロード
uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded_file is not None:
    # 文字コード対策
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding='shift_jis')
    
    st.success("ファイルの読み込みに成功しました！")
    
    required_columns = ['割当口数', '状態', '入金額']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"エラー: アップロードされたCSVに以下の項目名が見つかりません: {', '.join(missing_columns)}")
    
    else:
        st.subheader("📋 抽出メニュー")
        
        target_type = st.radio(
            "作成するリストを選択してください",
            ["未選択", "出資未確定者リスト", "未入金者リスト"],
            horizontal=True
        )

        if target_type != "未選択":
            
            # --- 💡 ここが今回の修正ポイントです ---
            # カンマ(,)や円マーク(¥)などの文字を削除してから、純粋な数値に変換します
            
            # 割当口数の前処理
            df['割当口数'] = df['割当口数'].astype(str).str.replace(',', '', regex=False)
            df['割当口数'] = pd.to_numeric(df['割当口数'], errors='coerce').fillna(0)
            
            # 入金額の前処理（カンマや記号を消す！）
            df['入金額'] = df['入金額'].astype(str).str.replace(',', '', regex=False).str.replace('¥', '', regex=False).str.replace('円', '', regex=False)
            df['入金額'] = pd.to_numeric(df['入金額'], errors='coerce').fillna(0)
            # ----------------------------------------

            if target_type == "出資未確定者リスト":
                filtered_df = df[(df['割当口数'] != 0) & (df['状態'] == '応募')]
                
            elif target_type == "未入金者リスト":
                # 入金額が純粋な「0」の人だけを正確に抽出します
                filtered_df = df[(df['割当口数'] != 0) & (df['状態'] == '同意') & (df['入金額'] == 0)]

            # 結果の表示とダウンロード
            st.write(f"### 🔍 {target_type} の一覧 ({len(filtered_df)}名)")
            st.dataframe(filtered_df)

            if len(filtered_df) > 0:
                csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label=f"✅ {target_type}のCSVをダウンロード",
                    data=csv_data,
                    file_name=f"{target_type}.csv",
                    mime="text/csv",
                )
            else:
                st.warning("該当する対象者が0名でした。")
