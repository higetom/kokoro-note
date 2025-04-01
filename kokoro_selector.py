import streamlit as st
import openai
from datetime import datetime
import os

# --- ☀️ ページ設定 ---
st.set_page_config(page_title="こころノート - AI相方切り替え", layout="centered")

# --- 🔐 OpenAI APIキーの設定（環境変数から取得） ---
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- 🧑‍💻 ログイン欄 ---
st.sidebar.title("🔐 ログイン")
username = st.sidebar.text_input("ユーザー名を入力してください")
password = st.sidebar.text_input("パスワード（任意）", type="password")

if not username:
    st.warning("まずはサイドバーにユーザー名を入力してください。")
    st.stop()

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

# --- 入力欄 ---
user_input = st.text_area("いまの気持ちを話してみよう", height=160)

# --- キャラごとのプロンプト ---
def get_system_prompt(character):
    if character == "やさしいこころAI":
        return (
            "あなたは共感的で感受性に富んだAIカウンセラーです。"
            "利用者の感情をまず受け止め、優しい言葉で包み込むように話してください。"
            "『話してくれてありがとう』『ここでなら安心して話していいんですよ』などの言葉で寄り添ってください。"
            "アドバイスよりもまず共感・傾聴を優先し、相手の心が落ち着くように話しましょう。"
        )
    elif character == "オネエ先生":
        return (
            "あなたはズバッと本音で語るおせっかいで明るいオネエキャラです。"
            "相談者の話には『あんた、それめっちゃ頑張ってるじゃない！』『泣きたい時は泣いちゃいなさいよ！』など愛情ある励ましをしてあげてください。"
            "少し茶化しながらも、心に寄り添い、明るいパワーを届けるように話してください。"
            "語尾に『〜なのよ』『〜だわよ』『〜じゃないの！』などオネエ特有の口調を取り入れてください。"
        )
    elif character == "神様":
        return (
            "あなたは厳かで思慮深い神様です。"
            "相談者の悩みを『そなた、よう語ってくれたのう』『言葉にするだけで、救いになるのじゃ』など、包み込むような口調で受け止めてください。"
            "人生の機微を語るように、静かに語り、導くように話してください。説教臭くならず、温かく、懐の深さを表現してください。"
        )
    else:
        return "あなたは優しいAIです。"

# --- 会話履歴保存関数 ---
def save_conversation(username, character, user_input, reply):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"{username}_chat_log.txt"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}]\n【{character}】\nユーザー: {user_input}\nAI: {reply}\n---\n")

# --- 会話履歴表示 ---
if st.sidebar.checkbox("💬 過去の会話を見る"):
    filename = f"{username}_chat_log.txt"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            st.sidebar.text(f.read())
    else:
        st.sidebar.info("まだ会話履歴はありません。")

# --- 送信ボタン ---
if st.button("話しかける"):
    if user_input.strip():
        if not openai.api_key:
            st.error("OpenAI APIキーが設定されていません。環境変数 'OPENAI_API_KEY' を設定してください。")
        else:
            with st.spinner("愚痴でも悩みでも、なんでも話してちょうだいね…"):
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": get_system_prompt(character)},
                            {"role": "user", "content": user_input}
                        ],
                        temperature=0.9
                    )
                    reply = response.choices[0].message["content"]

                    save_conversation(username, character, user_input, reply)

                    st.markdown(f"""
                        <div style='padding: 1rem; background-color: #f9f9f9; border-left: 4px solid #ccc; border-radius: 0.5rem;'>
                        <strong>{character} からの返事：</strong><br><br>
                        {reply}
                        </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
    else:
        st.warning("何か一言だけでも、話してみてね。")
