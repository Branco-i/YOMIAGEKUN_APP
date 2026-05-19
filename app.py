import streamlit as st
from googletrans import Translator
from gtts import gTTS
from pydub import AudioSegment
import os

st.title("日韓よみあげくん（安定版）")
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
        # 複数行を1つの文章にまとめる
        jp_text = text.replace("\n", "。")

        # 翻訳
        result = translator.translate(jp_text, src="ja", dest="ko")
        ko_text = result.text

        # 一時ファイル
        jp_mp3 = "jp.mp3"
        ko_mp3 = "ko.mp3"
        jp_wav = "jp.wav"
        ko_wav = "ko.wav"
        out_wav = "out.wav"
        out_mp3 = "output.mp3"

        # 音声生成
        generate_audio(jp_text, "ja", jp_mp3)
        generate_audio(ko_text, "ko", ko_mp3)

        # mp3 → wav に変換（無音が確実に入るように）
        AudioSegment.from_mp3(jp_mp3).export(jp_wav, format="wav")
        AudioSegment.from_mp3(ko_mp3).export(ko_wav, format="wav")

        # WAV 読み込み
        jp_audio = AudioSegment.from_wav(jp_wav)
        ko_audio = AudioSegment.from_wav(ko_wav)

        # 無音 0.7 秒を確実に挟む
        silence = AudioSegment.silent(duration=700)

        # 結合（順番固定）
        combined = jp_audio + silence + ko_audio

        # 出力
        combined.export(out_mp3, format="mp3")

        # 再生
        st.audio(out_mp3)

        # 翻訳結果表示
        st.success("翻訳結果： " + ko_text)

        # 一時ファイル削除
        for f in [jp_mp3, ko_mp3, jp_wav, ko_wav, out_mp3]:
            if os.path.exists(f):
                os.remove(f)
