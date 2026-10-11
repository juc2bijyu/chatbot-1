import streamlit as st
import google.generativeai as genai

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
    # Geminiクライアントの設定（REST通信に固定）
    genai.configure(api_key=gemini_api_key, transport="rest")
    model = genai.GenerativeModel("models/gemini-2.5-flash")

    # メッセージ履歴の初期化
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 過去ログの描画
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ユーザー入力欄
    if prompt := st.chat_input("What is up?"):
        # ユーザーの発言を履歴に追加して画面に表示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gemini用の会話履歴データを生成
        gemini_contents = [
            {
                "role": "model" if m["role"] == "assistant" else "user",
                "parts": [m["content"]],
            }
            for m in st.session_state.messages
        ]

        # 直接 generate_content でストリーミング生成
        response_stream = model.generate_content(gemini_contents, stream=True)

        def stream_generator():
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        # レスポンスの描画と履歴への保存
        with st.chat_message("assistant"):
            response = st.write_stream(stream_generator())
        st.session_state.messages.append({"role": "assistant", "content": response})
