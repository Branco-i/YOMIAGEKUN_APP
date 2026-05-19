import streamlit as st
from googletrans import Translator
from gtts import gTTS
import wave
import os

st.title("日韓よみあげくん（WAV版・Streamlit対応）")
st.write("日本語の文章を入力してください（改行で区切られます）")

text = st.text_area("日本語テキスト", height=200)

translator = Translator()

# WAV を読み込む関数
def read_wav(path):
    with wave.open(path, "rb") as wf:
        params = wf.getparams()
        frames = wf.readframes(params.nframes)
    return params, frames

# WAV を書き出す関数
def write_wav(path, params, frames):
    with wave.open(path, "wb") as wf:
        wf.setparams(params)
        wf.writeframes(frames)

if st.button("音声生成"):
    if not text.strip():
        st.error("テキストを入力してください")
    else:
        # 翻訳
        result = translator.translate(text, src="ja", dest="ko")
        korean_text = result.text

        # 一時ファイル
        jp_wav = "jp.wav"
        ko_wav = "ko.wav"
        out_wav = "output.wav"

        # 日本語音声生成
        gTTS(text=text, lang="ja").save(jp_wav)

        # 韓国語音声生成
        gTTS(text=korean_text, lang="ko").save(ko_wav)

        # WAV 読み込み
        jp_params, jp_frames = read_wav(jp_wav)
        ko_params, ko_frames = read_wav(ko_wav)

        # 結合（単純に frames をつなげる）
        combined_frames = jp_frames + ko_frames

        # 出力
        write_wav(out_wav, jp_params, combined_frames)

        # 再生
        st.audio(out_wav)

        # 翻訳結果表示
        st.success("翻訳結果： " + korean_text)

        # 一時ファイル削除
        os.remove(jp_wav)
        os.remove(ko_wav)
        os.remove(out_wav)
