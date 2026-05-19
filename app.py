import streamlit as st
from googletrans import Translator
from gtts import gTTS
from pydub import AudioSegment
import os
import random

# ====== ページ設定 ======
st.set_page_config(
    page_title="日中韓よみあげくん",
    page_icon="🎧",
    layout="centered",
)

# ====== スタイル ======
CUSTOM_CSS = """
<style>
    body {
        background-color: #f5f8ff;
    }
    .main {
        background-color: #f5f8ff;
    }
    .app-title {
        font-size: 28px;
        font-weight: 700;
        color: #1f3c88;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .app-subtitle {
        font-size: 14px;
        color: #5f6f94;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 10px rgba(31, 60, 136, 0.06);
    }
    .card-title {
        font-size: 16px;
        font-weight: 600;
        color: #1f3c88;
        margin-bottom: 0.6rem;
    }
    .small-label {
        font-size: 13px;
        color: #5f6f94;
        margin-bottom: 0.2rem;
    }
    .pair-line {
        font-size: 14px;
        color: #333333;
        margin-bottom: 0.2rem;
    }
    .pair-separator {
        border-bottom: 1px dashed #d0d7f2;
        margin: 0.4rem 0 0.6rem 0;
    }
    .stButton>button {
        background-color: #1f3c88;
        color: white;
        border-radius: 999px;
        padding: 0.4rem 1.4rem;
        border: none;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #27489e;
        color: white;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ====== タイトル ======
st.markdown('<div class="app-title">日中韓よみあげくん</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">日本語のフレーズから、韓国語・中国語の音声教材をつくるよ 🎧</div>', unsafe_allow_html=True)

# ====== 入力カード ======
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">① 日本語のフレーズを入力</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-label">1行につき1フレーズ（例：お姉さんですか？）</div>', unsafe_allow_html=True)
    text = st.text_area("", height=200, placeholder="お姉さんですか？\n無料です\nいつ行きますか？")
    st.markdown('</div>', unsafe_allow_html=True)

# ====== 設定カード ======
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">② 設定</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        mode = st.selectbox(
            "モード",
            ["通常モード（上から順に読み上げ）", "小テストモード（行の順番をランダムに読み上げ）"],
        )
    with col2:
        target_lang_label = st.selectbox(
            "翻訳先の言語",
            ["韓国語", "中国語（簡体）", "中国語（繁体）"],
        )

    col3, col4 = st.columns(2)
    with col3:
        order_label = st.selectbox(
            "読み上げ順",
            ["日本語 → 外国語", "外国語 → 日本語"],
        )
    with col4:
        speed = st.slider(
            "音声速度（1.0 が通常）",
            min_value=0.5,
            max_value=1.5,
            value=1.0,
            step=0.1,
        )

    st.markdown('<div class="small-label">無音の長さ（ミリ秒）</div>', unsafe_allow_html=True)
    col5, col6 = st.columns(2)
    with col5:
        silence_between_ms = st.slider(
            "日本語と外国語の間",
            min_value=0,
            max_value=5000,
            value=3000,
            step=500,
        )
    with col6:
        silence_after_pair_ms = st.slider(
            "1ペアのあと",
            min_value=0,
            max_value=8000,
            value=5000,
            step=500,
        )

    st.markdown('</div>', unsafe_allow_html=True)

# ====== ヘルパー関数 ======
translator = Translator()


def get_lang_code(label: str) -> str:
    if label == "韓国語":
        return "ko"
    if label == "中国語（簡体）":
        return "zh-CN"
    if label == "中国語（繁体）":
        return "zh-TW"
    return "ko"


# 🔥 翻訳を1行ずつ安全に行う（リトライ付き）
def safe_translate(text, target_lang, retries=3):
    for _ in range(retries):
        try:
            result = translator.translate(text, src="ja", dest=target_lang)
            return result.text
        except Exception:
            continue
    return None  # 翻訳失敗


def change_speed(audio: AudioSegment, speed: float) -> AudioSegment:
    if speed == 1.0:
        return audio
    new_frame_rate = int(audio.frame_rate * speed)
    changed = audio._spawn(audio.raw_data, overrides={"frame_rate": new_frame_rate})
    return changed.set_frame_rate(audio.frame_rate)


def tts_to_mp3(text: str, lang: str, filename: str) -> bool:
    text = text.strip()
    if not text:
        return False
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(filename)
        return True
    except Exception:
        return False


# ====== 実行カード ======
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">③ 音声を生成</div>', unsafe_allow_html=True)

    generate = st.button("音声をつくる 🎧")

    if generate:
        if not text.strip():
            st.error("日本語のテキストを入力してください。")
        else:
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            if not lines:
                st.error("有効な行がありません。")
            else:
                indices = list(range(len(lines)))
                if mode == "小テストモード（行の順番をランダムに読み上げ）":
                    random.shuffle(indices)

                target_lang = get_lang_code(target_lang_label)

                # ===== 翻訳（1行ずつ安全に） =====
                pairs = []
                for idx in indices:
                    jp_line = lines[idx]
                    foreign_line = safe_translate(jp_line, target_lang)

                    if foreign_line is None:
                        # 翻訳失敗 → スキップ
                        continue

                    pairs.append((jp_line, foreign_line))

                if not pairs:
                    st.error("翻訳に失敗しました。時間をおいて再度お試しください。")
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.stop()

                silence_between = AudioSegment.silent(duration=silence_between_ms)
                silence_after_pair = AudioSegment.silent(duration=silence_after_pair_ms)

                audio_segments = []
                used_pairs = []

                for i, (jp_line, foreign_line) in enumerate(pairs):
                    jp_mp3 = f"jp_{i}.mp3"
                    fr_mp3 = f"fr_{i}.mp3"

                    ok_jp = tts_to_mp3(jp_line, "ja", jp_mp3)
                    ok_fr = tts_to_mp3(foreign_line, target_lang, fr_mp3)

                    if not (ok_jp and ok_fr):
                        for f in [jp_mp3, fr_mp3]:
                            if os.path.exists(f):
                                os.remove(f)
                        continue

                    try:
                        jp_audio = AudioSegment.from_mp3(jp_mp3)
                        fr_audio = AudioSegment.from_mp3(fr_mp3)
                    except Exception:
                        for f in [jp_mp3, fr_mp3]:
                            if os.path.exists(f):
                                os.remove(f)
                        continue

                    jp_audio = change_speed(jp_audio, speed)
                    fr_audio = change_speed(fr_audio, speed)

                    if order_label == "日本語 → 外国語":
                        pair_audio = jp_audio + silence_between + fr_audio
                    else:
                        pair_audio = fr_audio + silence_between + jp_audio

                    pair_audio = pair_audio + silence_after_pair

                    audio_segments.append(pair_audio)
                    used_pairs.append((jp_line, foreign_line))

                    for f in [jp_mp3, fr_mp3]:
                        if os.path.exists(f):
                            os.remove(f)

                if not audio_segments:
                    st.error("音声を生成できた行がありませんでした。")
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.stop()

                final_audio = audio_segments[0]
                for seg in audio_segments[1:]:
                    final_audio += seg

                output_file = "output.mp3"
                try:
                    final_audio.export(output_file, format="mp3")
                except Exception:
                    st.error("音声ファイルの生成に失敗しました。")
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.stop()

                st.audio(output_file)

                st.markdown('<div class="small-label">読み上げたペア一覧</div>', unsafe_allow_html=True)
                st.write(f"ペア数：{len(used_pairs)}")
                for jp_line, foreign_line in used_pairs:
                    st.markdown(f'<div class="pair-line"><b>日本語：</b> {jp_line}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="pair-line"><b>{target_lang_label}：</b> {foreign_line}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="pair-separator"></div>', unsafe_allow_html=True)

                try:
                    with open(output_file, "rb") as f:
                        st.download_button(
                            label="音声ファイルをダウンロード（MP3）",
                            data=f.read(),
                            file_name="yomiage.mp3",
                            mime="audio/mpeg",
                        )
                finally:
                    if os.path.exists(output_file):
                        os.remove(output_file)

    st.markdown('</div>', unsafe_allow_html=True)
