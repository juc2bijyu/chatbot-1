import streamlit as st
from openai import OpenAI

# タイトルと説明文
st.title("💬 Chatbot")

# StreamlitのSecretsからAPIキーを取得
if "GEMINI_API_KEY" not in st.secrets:
    st.error("APIキーが設定されていません。StreamlitのSecretsに GEMINI_API_KEY を登録してください。")
    st.stop()

gemini_api_key = st.secrets["GEMINI_API_KEY"]

# Geminiのエンドポイントを指定したOpenAIクライアント
client = OpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# メッセージ履歴のセッション初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# 過去ログの描画
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ユーザー入力欄
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Gemini へのリクエスト（ストリーミング）
        stream = client.chat.completions.create(
            model="gemini-flash-latest",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # レスポンスの描画と保存
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

    except Exception as e:
        st.error(f"APIエラー: {e}")
