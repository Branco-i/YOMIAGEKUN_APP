import streamlit as st
from gtts import gTTS
from pydub import AudioSegment
from googletrans import Translator
import os

translator = Translator()

st.title("読み上げくん")
st.write("日本語 → 無音3秒 → 韓国語 → 無音5秒 の音声を自動生成します")

# 入力欄
jp_text_input = st.text_area("日本語を1行ずつ入力してください（複数行OK）")

if st.button("音声を作成"):
    if not jp_text_input.strip():
        st.warning("日本語を入力してください")
    else:
        text_list = jp_text_input.split("\n")

        combined = AudioSegment.empty()

        for jp_text in text_list:
            if not jp_text.strip():
                continue

            # 日本語音声
            tts_jp = gTTS(text=jp_text, lang='ja')
            tts_jp.save("temp_jp.mp3")

            # 韓国語翻訳
            ko_text = translator.translate(jp_text, dest='ko').text

            # 韓国語音声
            tts_ko = gTTS(text=ko_text, lang='ko')
            tts_ko.save("temp_ko.mp3")

            # 結合
            combined += AudioSegment.from_mp3("temp_jp.mp3")
            combined += AudioSegment.silent(duration=3000)
            combined += AudioSegment.from_mp3("temp_ko.mp3")
            combined += AudioSegment.silent(duration=5000)

        # 出力
        output_path = "study_material.mp3"
        combined.export(output_path, format="mp3")

        st.success("音声ファイルが完成しました！")
        audio_file = open(output_path, "rb")
        st.audio(audio_file.read(), format="audio/mp3")

        st.download_button(
            label="ダウンロード",
            data=open(output_path, "rb").read(),
            file_name="study_material.mp3",
            mime="audio/mp3"
        )
