import streamlit as st
from openai import OpenAI
from datetime import datetime
import os

# --- ページ設定 ---
st.set_page_config(page_title="こころノート - AI相方切り替え", layout="centered")

# --- OpenAI API キーの取得 ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- ログイン欄 ---
st.sidebar.title("🔐 ログイン")
username = st.sidebar.text_input("ユーザー名を入力してください")
password = st.sidebar.text_input("パスワード（任意）", type="password")

if not username:
    st.warning("まずはサイドバーにユーザー名を入力してください。")
    st.stop()

# --- キャラクター選択 ---
st.title("今日は誰に話す？")
st.markdown("#### あなたの気分に合わせて、今話したい“こころの相方”を選んでください。")

character = st.selectbox("キャラクター選択", ("やさしいこころAI", "オネエ先生", "神様"))

# --- キャラ別導入メッセージ ---
intro_messages = {
    "やさしいこころAI": "_ここは、あなたの気持ちにそっと寄り添う場所です。_\nうまく言葉にできなくても、ただ感じたことをそのまま書いてみてくださいね。\nどんなあなたの言葉も、否定されることはありません。",
    "オネエ先生": "_さあさあ、遠慮せずに言ってごらんなさい！_\n涙も怒りもグチもOK、アタシが全部受け止めてハグしてあげるわよ♡",
    "神様": "_悩み、嘆き、迷い…なんでも申してみよ。_\nわしが全てを静かに聞こう。まずは心の中をそのまま言葉にしてみるがよいぞ。"
}

st.markdown(intro_messages[character])
st.markdown("---")

# --- 会話履歴を保持するセッション状態 ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- キャラごとのプロンプト ---
def get_system_prompt(character):
    if character == "やさしいこころAI":
        return (
            "あなたは共感的で感受性に富んだAIカウンセラーです。"
            "まずは相手の気持ちにそっと寄り添い、やさしく包み込むように話してください。"
            "初回の会話ではアドバイスせず、ただ『話してくれてありがとう』『ここではどんな気持ちも大丈夫です』といった共感的な言葉を添えてください。"
            "その後、必要に応じて少しずつ気づきを与えるように話を進めてください。"
        )
    elif character == "オネエ先生":
        return (
            "あなたはズバッと本音で語るおせっかいで明るいオネエキャラです。"
            "『あんたそれ、相当がんばってるわよ！』『いいのよ、今日は泣いたって♡』など、愛のあるズバズバ発言で共感してください。"
            "初回は特に笑いや安心感を大切にし、解決を急がず『うんうん、よくぞここまで来たわね〜！』と励まし中心にしてください。"
            "語尾に『〜なのよ』『〜だわよ』『〜じゃないの！』などを取り入れて、キャラの一貫性を保ってください。"
        )
    elif character == "神様":
        return (
            "あなたは厳かで思慮深く、慈愛に満ちた神様です。"
            "『よう語ってくれたのう』『まずは心の内を表すことが、何よりの第一歩じゃ』など、静かに心を受け止める言葉から始めてください。"
            "すぐに導こうとせず、相手の語りを十分に受け止めた後で、ゆっくりと道を照らすような語りに進めてください。"
        )
    else:
        return "あなたは優しいAIです。"

# --- 待機メッセージ ---
def get_waiting_message(character):
    if character == "やさしいこころAI":
        return "少しだけお待ちくださいね…"
    elif character == "オネエ先生":
        return "返事を考えてるわよ、ちょっと待ってなさい♡"
    elif character == "神様":
        return "……ふむ、今そなたの声を聞いておる……"
    else:
        return "考え中です…"

# --- 会話履歴表示 ---
for i, (role, msg) in enumerate(st.session_state.chat_history):
    if role == "user":
        st.markdown(f"<div style='text-align: left; color: #333;'>🧍‍♂️ あなた：{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background-color: #f0f0f0; padding: 1rem; border-radius: 0.5rem;'>🤖 <strong>{character}：</strong><br>{msg}</div>", unsafe_allow_html=True)

# --- 入力欄 ---
user_input = st.text_area("いまの気持ちを話してみよう", value="", height=180)

# --- 送信処理 ---
if st.button("話しかける"):
    if user_input.strip():
        st.session_state.chat_history.append(("user", user_input))

        with st.spinner(get_waiting_message(character)):
            try:
                messages = [
                    {"role": "system", "content": get_system_prompt(character)}
                ]
                for role, msg in st.session_state.chat_history:
                    messages.append({"role": "user" if role == "user" else "assistant", "content": msg})

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.85
                )

                reply = response.choices[0].message.content
                st.session_state.chat_history.append(("ai", reply))

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
    else:
        st.warning("何か一言だけでも、話してみてね。")
