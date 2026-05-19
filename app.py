import streamlit as st
from googletrans import Translator
from gtts import gTTS
from pydub import AudioSegment
import os

st.title("日韓よみあげくん（Render 完全版）")
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
        # 翻訳
        result = translator.translate(text, src="ja", dest="ko")
        korean_text = result.text

        # 一時ファイル
        jp_file = "jp_temp.mp3"
        ko_file = "ko_temp.mp3"
        out_file = "output.mp3"

        # 音声生成
        generate_audio(text, "ja", jp_file)
        generate_audio(korean_text, "ko", ko_file)

        # pydub で読み込み
        jp_audio = AudioSegment.from_mp3(jp_file)
        ko_audio = AudioSegment.from_mp3(ko_file)

        # 結合（間に 0.5 秒の無音）
        combined = jp_audio + AudioSegment.silent(duration=500) + ko_audio

        # 出力
        combined.export(out_file, format="mp3")

        # 再生
        st.audio(out_file)

        # 翻訳結果表示
        st.success("翻訳結果： " + korean_text)

        # 一時ファイル削除
        os.remove(jp_file)
        os.remove(ko_file)
        os.remove(out_file)

