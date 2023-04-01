import streamlit as st
import requests
from io import BytesIO
from deepdreamgenerator import deepdreamgenerator
from moviepy.editor import *

os.environ['IMAGEIO_FFMPEG_EXE'] = os.path.join("path", "to", "ffmpeg.exe")

WPM = 200 # palabras por minuto
CLIP_DURATION = 5 # duración en segundos de cada clip de video

def generate_story(length):
    response = requests.get(f"https://api.chatterscan.com/gpt3?model=curie-instruct-beta-001&length={length}")
    return response.json()["text"].split("\n\n")

def generate_voiceover(paragraph):
    # Generar una voz en off a partir del párrafo usando una API de síntesis de voz
    # (por ejemplo, Google Text-to-Speech o Amazon Polly)
    voiceover = ... # código para generar la voz en off
    return voiceover

def generate_video(story):
    clips = []
    for i, paragraph in enumerate(story):
        # Generar la imagen de sueño profundo correspondiente al párrafo
        imagebytes = deepdreamgenerator(paragraph)
        imageclip = ImageClip(BytesIO(imagebytes)).resize(height=720)

        # Generar la voz en off correspondiente al párrafo y calcular la duración del clip
        voiceover = generate_voiceover(paragraph)
        num_words = len(paragraph.split())
        clip_duration = num_words / WPM

        # Crear el clip de video compuesto por la imagen y la voz en off
        audio = AudioFileClip(voiceover).set_duration(clip_duration)
        audio = audio.set_start(0) # empezar al principio del clip
        imageclip = imageclip.set_duration(clip_duration)
        imageclip = imageclip.set_start(0) # empezar al principio del clip
        compositeclip = CompositeVideoClip([imageclip, audio.set_pos(('center', 'bottom'))])

        clips.append(compositeclip)

    # Concatenar los clips de video para crear el video completo
    videoclip = concatenate_videoclips(clips)

    # Guardar el video en un archivo
    videofilename = "story.mp4"
    videoclip.write_videofile(videofilename, fps=24)

    return videofilename


st.title("Generador de Historias")
st.write("Este es un generador automático de historias. Ingresa tu idea principal y presiona el botón para generar una historia aleatoria y un video personalizado.")
idea_principal = st.text_input("Ingresa tu idea principal")
if st.button("Generar Historia"):
    length = 5
    story = generate_story(idea_principal, length)
    st.write("Historia generada:")
    for i, paragraph in enumerate(story):
        st.write(f"{i+1}. {paragraph}")
    st.write("Generando video…")
    videofilename = generate_video(story)
    st.write("Video generado:")
    videofile = open(videofilename, "rb")
    videobytes = videofile.read()
    st.video(videobytes)
    st.write("Previsualizando video…")
    preview_clip = VideoFileClip(videofilename).subclip(0, 10)
    preview_clip = preview_clip.resize(height=360)
    preview_file = "preview.mp4"
    preview_clip.write_videofile(preview_file, fps=24)
    preview_file = open(preview_file, "rb")
    preview_bytes = preview_file.read()
    st.video(preview_bytes)
else:
    st.write("Ingresa tu idea principal y presiona el botón para generar una historia y video personalizados.")
