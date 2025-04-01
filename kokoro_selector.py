import streamlit as st
from openai import OpenAI
from datetime import datetime
import os

# --- ☀️ ページ設定 ---
st.set_page_config(page_title="こころノート - AI相方切り替え", layout="centered")

# --- 🔐 OpenAI APIキーの設定（環境変数から取得） ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- 🧑‍💻 ログイン欄 ---
st.sidebar.title("🔐 ログイン")
username = st.sidebar.text_input("ユーザー名を入力してください")
password = st.sidebar.text_input("パスワード（任意）", type="password")

if not username:
    st.warning("まずはサイドバーにユーザー名を入力してください。")
    st.stop()

# --- 会話履歴をセッションで保持 ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- ☁️ キャラメニュー UI ---
st.title("今日は誰に話す？")
st.markdown("""
#### あなたの気分に合わせて、今話したい“こころの相方”を選んでください。
""")

character = st.selectbox(
    "キャラクター選択",
    ("やさしいこころAI", "オネエ先生", "神様")
)

# --- キャラごとの導入メッセージ ---
if character == "やさしいこころAI":
    st.markdown("""
    _ここは、あなたの気持ちにそっと寄り添う場所です。_
    うまく言葉にできなくても、ただ感じたことをそのまま書いてみてくださいね。
    どんなあなたの言葉も、否定されることはありません。
    """)
elif character == "オネエ先生":
    st.markdown("""
    _さあさあ、遠慮せずに言ってごらんなさい！_
    涙も怒りもグチもOK、アタシが全部受け止めてハグしてあげるわよ♡
    """)
elif character == "神様":
    st.markdown("""
    _悩み、嘆き、迷い…なんでも申してみよ。_
    わしが全てを静かに聞こう。まずは心の中をそのまま言葉にしてみるがよいぞ。
    """)

st.markdown("---")

# --- 入力欄（広めに設定） ---
user_input = st.text_area("いまの気持ちを話してみよう", height=240)

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
            "語尾に『〜なのよ』『〜だわよ』『〜じゃないの！』などを取り入れて、キャラの一貫性を保ってください。もっと濃くてもOK！"
        )
    elif character == "神様":
        return (
            "あなたは厳かで思慮深く、慈愛に満ちた神様です。"
            "『よう語ってくれたのう』『まずは心の内を表すことが、何よりの第一歩じゃ』など、静かに心を受け止める言葉から始めてください。"
            "すぐに導こうとせず、相手の語りを十分に受け止めた後で、ゆっくりと道を照らすような語りに進めてください。"
        )
    else:
        return "あなたは優しいAIです。"

# --- 会話履歴保存関数 ---
def save_conversation(username, character, user_input, reply):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"{username}_chat_log.txt"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}]\n【{character}】\nユーザー: {user_input}\nAI: {reply}\n---\n")

# --- 過去の会話を表示（セッション） ---
if st.sidebar.checkbox("💬 過去の会話を見る"):
    for entry in st.session_state.chat_history:
        st.sidebar.markdown(f"**あなた：** {entry['user']}\n\n**{character}：** {entry['ai']}\n\n---")

# --- 送信ボタン ---
if st.button("話しかける"):
    if user_input.strip():
        if not os.getenv("OPENAI_API_KEY"):
            st.error("OpenAI APIキーが設定されていません。環境変数 'OPENAI_API_KEY' を設定してください。")
        else:
            with st.spinner(f"{character}が返事を考え中です…少々お待ちくださいね。"):
                try:
                    messages = [
                        {"role": "system", "content": get_system_prompt(character)}
                    ]
                    for chat in st.session_state.chat_history:
                        messages.append({"role": "user", "content": chat['user']})
                        messages.append({"role": "assistant", "content": chat['ai']})
                    messages.append({"role": "user", "content": user_input})

                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        temperature=0.85
                    )
                    reply = response.choices[0].message.content
                    st.session_state.chat_history.append({"user": user_input, "ai": reply})

                    save_conversation(username, character, user_input, reply)

                    st.markdown(f"""
                        <div style='padding: 1rem; background-color: #f9f9f9; border-left: 4px solid #ccc; border-radius: 0.5rem;'>
                        <strong>{character}：</strong><br><br>
                        {reply}
                        </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
    else:
        st.warning("何か一言だけでも、話してみてね。")
