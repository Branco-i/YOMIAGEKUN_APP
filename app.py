import streamlit as st
from googletrans import Translator
from gtts import gTTS
from pydub import AudioSegment
import os
import random

st.title("日中韓よみあげくん（拡張版）")
st.write("日本語の文章を1行ずつ入力してください（1行 = 1ペア）")

text = st.text_area("日本語テキスト", height=200)

# ===== 設定UI =====

mode = st.selectbox(
    "モードを選んでください",
    ["通常モード（上から順に読み上げ）", "小テストモード（行の順番をランダムに読み上げ）"],
)

target_lang_label = st.selectbox(
    "翻訳先の言語",
    ["韓国語", "中国語（簡体）", "中国語（繁体）"],
)

order_label = st.selectbox(
    "読み上げ順",
    ["日本語 → 外国語", "外国語 → 日本語"],
)

silence_between_ms = st.slider(
    "日本語と外国語の間の無音（ミリ秒）",
    min_value=0,
    max_value=5000,
    value=3000,
    step=500,
)

silence_after_pair_ms = st.slider(
    "1ペアのあとに入れる無音（ミリ秒）",
    min_value=0,
    max_value=8000,
    value=5000,
    step=500,
)

speed = st.slider(
    "音声速度（1.0 が通常）",
    min_value=0.5,
    max_value=1.5,
    value=1.0,
    step=0.1,
)

translator = Translator()


def get_lang_code(label: str) -> str:
    if label == "韓国語":
        return "ko"
    if label == "中国語（簡体）":
        return "zh-CN"
    if label == "中国語（繁体）":
        return "zh-TW"
    return "ko"


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


if st.button("音声生成"):
    if not text.strip():
        st.error("日本語のテキストを入力してください。")
    else:
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        if not lines:
            st.error("有効な行がありません。")
        else:
            # 小テストモードなら行の順番をランダムに
            if mode == "小テストモード（行の順番をランダムに読み上げ）":
                random.shuffle(lines)

            target_lang = get_lang_code(target_lang_label)
            silence_between = AudioSegment.silent(duration=silence_between_ms)
            silence_after_pair = AudioSegment.silent(duration=silence_after_pair_ms)

            final_audio = AudioSegment.silent(duration=0)
            used_pairs = []

            for i, jp_line in enumerate(lines):
                # 翻訳
                try:
                    result = translator.translate(jp_line, src="ja", dest=target_lang)
                    foreign_line = result.text
                except Exception:
                    # 翻訳に失敗した行はスキップ
                    continue

                # ファイル名
                jp_mp3 = f"jp_{i}.mp3"
                fr_mp3 = f"fr_{i}.mp3"

                # 日本語音声
                ok_jp = tts_to_mp3(jp_line, "ja", jp_mp3)
                # 外国語音声
                ok_fr = tts_to_mp3(foreign_line, target_lang, fr_mp3)

                if not (ok_jp and ok_fr):
                    # どちらかが失敗したらこのペアはスキップ
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

                # 速度調整
                jp_audio = change_speed(jp_audio, speed)
                fr_audio = change_speed(fr_audio, speed)

                # 読み上げ順
                if order_label == "日本語 → 外国語":
                    pair_audio = jp_audio + silence_between + fr_audio
                else:  # 外国語 → 日本語
                    pair_audio = fr_audio + silence_between + jp_audio

                # ペアのあとに無音
                pair_audio = pair_audio + silence_after_pair

                final_audio += pair_audio
                used_pairs.append((jp_line, foreign_line))

                # 一時ファイル削除
                for f in [jp_mp3, fr_mp3]:
                    if os.path.exists(f):
                        os.remove(f)

            if len(used_pairs) == 0:
                st.error("音声を生成できた行がありませんでした。翻訳や通信が不安定な可能性があります。")
            else:
                output_file = "output.mp3"
                try:
                    final_audio.export(output_file, format="mp3")
                    st.audio(output_file)

                    # ペア一覧も表示（学習用）
                    st.success(f"読み上げペア数：{len(used_pairs)}")
                    for jp_line, foreign_line in used_pairs:
                        st.write(f"**日本語:** {jp_line}")
                        st.write(f"**{target_lang_label}:** {foreign_line}")
                        st.write("---")

                    # ダウンロードボタン（オフライン用）
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
