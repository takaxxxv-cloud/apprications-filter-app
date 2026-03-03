import streamlit as st
import pandas as pd

# ページの設定
st.set_page_config(page_title="SE", layout="wide")

st.title("Swift Extract")
st.write("CSVをアップロードして、抽出したいリストのボタンを押すだけで完了します。")

# 1. CSVファイルのアップロード
uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded_file is not None:
    # 文字コード対策（Shift-JISとUTF-8の両方に対応）
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding='shift_jis')
    
    st.success("ファイルの読み込みに成功しました！")
    
    # ⚠️ 必須の列（項目名）がCSVに存在するかチェック
    required_columns = ['割当口数', '状態', '入金額']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        # もし列名が違っていたらエラーメッセージを出す
        st.error(f"エラー: アップロードされたCSVに以下の項目名が見つかりません: {', '.join(missing_columns)}")
        st.info("※CSVの1行目の項目名が「割当口数」「状態」「入金額」と完全に一致しているか（スペースなどが混じっていないか）確認してください。")
    
    else:
        st.subheader("📋 抽出メニュー")
        
        # 2. リストの種類を選択（ワンクリックで切り替え）
        target_type = st.radio(
            "作成するリストを選択してください",
            ["未選択", "出資未確定者リスト", "未入金者リスト"],
            horizontal=True
        )

        if target_type != "未選択":
            
            # --- 3. プログラムによる自動抽出 ---
            
            # 安全に計算できるように、データの中に空白（空欄）があれば「0」として扱う設定
            df['割当口数'] = pd.to_numeric(df['割当口数'], errors='coerce').fillna(0)
            df['入金額'] = pd.to_numeric(df['入金額'], errors='coerce').fillna(0)

            if target_type == "出資未確定者リスト":
                # 定義: 割当口数 ≠ 0, かつ 状態 = 応募
                filtered_df = df[(df['割当口数'] != 0) & (df['状態'] == '応募')]
                
            elif target_type == "未入金者リスト":
                # 定義: 割当口数 ≠ 0, かつ 状態 = 同意, かつ 入金額 = 0
                filtered_df = df[(df['割当口数'] != 0) & (df['状態'] == '同意') & (df['入金額'] == 0)]

            # --- 4. 結果の表示とダウンロード ---
            st.write(f"###  {target_type} の一覧 ({len(filtered_df)}名)")
            st.dataframe(filtered_df)

            if len(filtered_df) > 0:
                # ダウンロード用のデータを作成
                csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label=f"✅ {target_type}のCSVをダウンロード",
                    data=csv_data,
                    file_name=f"{target_type}.csv",
                    mime="text/csv",
                )
            else:
                st.warning("該当する対象者が0名でした。")
