import streamlit as st
from googletrans import Translator
from gtts import gTTS
from pydub import AudioSegment
import os

st.title("日韓よみあげくん（完全安定版）")
st.write("日本語の文章を入力してください（改行で区切られます）")

text = st.text_area("日本語テキスト", height=200)

translator = Translator()

def tts_mp3(text, lang, filename):
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)

if st.button("音声生成"):
    if not text.strip():
        st.error("テキストを入力してください")
    else:
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        silence_3s = AudioSegment.silent(duration=3000)
        silence_5s = AudioSegment.silent(duration=5000)

        final_audio = AudioSegment.silent(duration=0)

        for i, line in enumerate(lines):
            # 翻訳
            ko = translator.translate(line, src="ja", dest="ko").text

            # ファイル名（行ごとに完全に別ファイル）
            jp_mp3 = f"jp_{i}.mp3"
            ko_mp3 = f"ko_{i}.mp3"

            # 日本語音声
            tts_mp3(line, "ja", jp_mp3)
            jp_audio = AudioSegment.from_mp3(jp_mp3)

            # 韓国語音声
            tts_mp3(ko, "ko", ko_mp3)
            ko_audio = AudioSegment.from_mp3(ko_mp3)

            # 結合：日本語 → 3秒 → 韓国語 → 5秒
            final_audio += jp_audio + silence_3s + ko_audio + silence_5s

            # 一時ファイル削除
            os.remove(jp_mp3)
            os.remove(ko_mp3)

        # 出力
        output = "output.mp3"
        final_audio.export(output, format="mp3")

        st.audio(output)
        st.success("読み上げデータを生成しました！")

        os.remove(output)
