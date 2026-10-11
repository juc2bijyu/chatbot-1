import streamlit as st
import google.generativeai as genai

# APIキー設定直後に挿入
#for m in genai.list_models():
#    if "generateContent" in m.supported_generation_methods:
#        st.write(m.name)

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses Google's Gemini model to generate responses. "
    "To use this app, you need to provide a Gemini API key, which you can get [here](https://aistudio.google.com/app/apikey). "
    "You can also store the API key in `.streamlit/secrets.toml` or Streamlit Community Cloud Secrets."
)

# Secretsに登録されているか確認し、なければテキスト入力で受け取る
api_key_from_secrets = st.secrets.get("GEMINI_API_KEY", None)

if api_key_from_secrets:
    gemini_api_key = api_key_from_secrets
else:
    gemini_api_key = st.text_input("Gemini API Key", type="password")

if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:
    # Geminiクライアントの設定
    genai.configure(api_key=gemini_api_key)
    #model = genai.GenerativeModel("gemini-1.5-flash")
    #model = genai.GenerativeModel("gemini-1.5-flash-latest")
    model = genai.GenerativeModel("gemini-2.5-flash-lite")


    # メッセージ履歴のセッションステート初期化
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 過去ログの描画
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ユーザー入力
    if prompt := st.chat_input("What is up?"):

        # ユーザーの発言を記録して表示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gemini用の履歴フォーマット（'assistant' を 'model' にマッピング）
        gemini_history = [
            {
                "role": "model" if m["role"] == "assistant" else "user",
                "parts": [m["content"]],
            }
            for m in st.session_state.messages[:-1]
        ]

        # チャットセッションを開始してストリーミング生成
        chat = model.start_chat(history=gemini_history)
        response_stream = chat.send_message(prompt, stream=True)

        # st.write_stream 用のジェネレータ
        def stream_generator():
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        # レスポンスのストリーミング表示と保存
        with st.chat_message("assistant"):
            response = st.write_stream(stream_generator())
        st.session_state.messages.append({"role": "assistant", "content": response})
