import streamlit as st
from googletrans import Translator
from gtts import gTTS
from pydub import AudioSegment
import os

st.title("日韓よみあげくん（Streamlit対応版）")
st.write("日本語の文章を入力してください（改行で区切られます）")

text = st.text_area("日本語テキスト", height=200)

translator = Translator()

def generate_audio(text, lang, filename):
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)

if st.button("音声生成"):
    if not text.strip():
        st.error("テキストを入力してください")
    else:
        # 日本語 → 韓国語 翻訳
        result = translator.translate(text, src="ja", dest="ko")
        korean_text = result.text

        # 一時ファイル名
        jp_file = "jp_temp.mp3"
        ko_file = "ko_temp.mp3"
        out_file = "output.mp3"

        # 音声生成
        generate_audio(text, "ja", jp_file)
        generate_audio(korean_text, "ko", ko_file)

        # pydub で読み込み
        jp_audio = AudioSegment.from_mp3(jp_file)
        ko_audio = AudioSegment.from_mp3(ko_file)

        # 結合
        combined = jp_audio + Audio