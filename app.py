import streamlit as st
from gtts import gTTS
from googletrans import Translator
import wave
import numpy as np
import os

translator = Translator()

# 無音を作る関数（秒数指定）
def generate_silence(seconds, sample_rate=44100):
    num_samples = int(seconds * sample_rate)
    silence = np.zeros(num_samples, dtype=np.int16)
    return silence.tobytes()

# WAV を読み込む
def read_wav(path):
    with wave.open(path, "rb") as wf:
        params = wf.getparams()
        frames = wf.readframes(wf.getnframes())
    return params, frames

# WAV を書き込む
def write_wav(path, params, frames):
    with wave.open(path, "wb") as wf:
        wf.setparams(params)
        wf.writeframes(frames)

st.title("日韓よみあげくん（Streamlit対応版）")

jp_text_input = st.text_area("日本語の文章を入力してください（改行で区切られます）")

if st.button("音声生成"):
    text_list = jp_text_input.split("\n")
    combined_frames = b""
    params = None

    for jp_text in text_list:
        if not jp_text.strip():
            continue

        # 日本語音声
        tts_jp = gTTS(text=jp_text, lang='ja')
        tts_jp.save("temp_jp.mp3")
        os.system("ffmpeg -y -i temp_jp.mp3 temp_jp.wav")

        # 韓国語翻訳
        ko_text = translator.translate(jp_text, dest='ko').text

        # 韓国語音声
        tts_ko = gTTS(text=ko_text, lang='ko')
        tts_ko.save("temp_ko.mp3")
        os.system("ffmpeg -y -i temp_ko.mp3 temp_ko.wav")

        # WAV 読み込み
        if params is None:
            params, jp_frames = read_wav("temp_jp.wav")
        else:
            _, jp_frames = read_wav("temp_jp.wav")

        _, ko_frames = read_wav("temp_ko.wav")

        # 結合
        combined_frames += jp_frames
        combined_frames += generate_silence(3)  # 3秒無音
        combined_frames += ko_frames
        combined_frames += generate_silence(5)  # 5秒無音

    # 出力
    output_path = "study_material.wav"
    write_wav(output_path, params, combined_frames)

    st.success("音声ファイルが完成しました！")
    audio_file = open(output_path, "rb")
    st.audio(audio_file.read(), format="audio/wav")
