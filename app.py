import streamlit as st
import pandas as pd

# アプリのタイトル
st.title("顧客データ抽出システム")

# 1. CSVファイルのアップロード
uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded_file is not None:
    # 💡 ここが修正ポイントです！文字コードのエラーを防ぎます
    try:
        # まずは標準のUTF-8で読み込んでみる
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except UnicodeDecodeError:
        # エラーが出たら、Excel標準のShift-JISで読み直す
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding='shift_jis')
    
    st.write("【元のデータ】", df.head()) # 最初の5行だけ表示

    st.subheader("抽出条件の設定")
    
    # 2. 絞り込みたい列（項目）を選択
    column_to_filter = st.selectbox("どの項目で絞り込みますか？", df.columns)
    
    # 3. 検索するキーワードを入力
    search_keyword = st.text_input(f"「{column_to_filter}」に含まれるキーワードを入力してください")
    
    # 4. 抽出の実行
    if search_keyword:
        # 条件に一致するデータだけを抽出
        filtered_df = df[df[column_to_filter].astype(str).str.contains(search_keyword, na=False)]
        
        st.write(f"【抽出結果】 {len(filtered_df)}件見つかりました")
        st.dataframe(filtered_df)
        
        # 5. 結果をCSVでダウンロード（文字化け防止のため utf-8-sig に変更）
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="抽出結果をCSVでダウンロード",
            data=csv,
            file_name="filtered_data.csv",
            mime="text/csv",
        )
