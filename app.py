import streamlit as st
from googletrans import Translator
from gtts import gTTS
from pydub import AudioSegment
import os

st.title("日韓よみあげくん（行ごとペア読み上げ版）")
st.write("日本語の文章を入力してください（改行で区切られます）")

text = st.text_area("日本語テキスト", height=200)

translator = Translator()

def tts_to_wav(text, lang, filename):
    mp3_file = filename.replace(".wav", ".mp3")
    tts = gTTS(text=text, lang=lang)
    tts.save(mp3_file)
    AudioSegment.from_mp3(mp3_file).export(filename, format="wav")
    os.remove(mp3_file)

if st.button("音声生成"):
    if not text.strip():
        st.error("テキストを入力してください")
    else:
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        silence_3s = AudioSegment.silent(duration=3000)
        silence_5s = AudioSegment.silent(duration=5000)

        final_audio = AudioSegment.silent(duration=0)

        for line in lines:
            # 翻訳
            ko = translator.translate(line, src="ja", dest="ko").text

            # 一時ファイル
            jp_wav = "jp.wav"
            ko_wav = "ko.wav"

            # 日本語音声
            tts_to_wav(line, "ja", jp_wav)
            jp_audio = AudioSegment.from_wav(jp_wav)

            # 韓国語音声
            tts_to_wav(ko, "ko", ko_wav)
            ko_audio = AudioSegment.from_wav(ko_wav)

            # 結合：日本語 → 3秒 → 韓国語 → 5秒
            final_audio += jp_audio + silence_3s + ko_audio + silence_5s

            # 一時ファイル削除
            os.remove(jp_wav)
            os.remove(ko_wav)

        # 出力
        output = "output.mp3"
        final_audio.export(output, format="mp3")

        st.audio(output)
        st.success("読み上げデータを生成しました！")

        os.remove(output)
