import streamlit as st
from openai import OpenAI

# タイトルと説明文
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses Google's Gemini model to generate responses. "
    "To use this app, you need to provide a Gemini API key, which you can get [here](https://aistudio.google.com/app/apikey). "
    "You can also store the API key in `.streamlit/secrets.toml` or Streamlit Community Cloud Secrets."
)

# APIキーの取得（Secrets または 画面入力）
api_key_from_secrets = st.secrets.get("GEMINI_API_KEY", None)

if api_key_from_secrets:
    gemini_api_key = api_key_from_secrets
else:
    gemini_api_key = st.text_input("Gemini API Key", type="password")

if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:
    # Geminiのエンドポイントを指定したOpenAIクライアントを作成
    client = OpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    # メッセージ履歴の初期化
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

        # Gemini 2.5 Flash でストリーミング生成
        stream = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # レスポンスの描画と履歴への保存
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
