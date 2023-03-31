import streamlit as st
import requests
import json
import imageio
import urllib
import os
from transformers import GPTNeoForCausalLM, GPT2Tokenizer
from transformers import pipeline, set_seed
from PIL import Image

tokenizer = GPT2Tokenizer.from_pretrained("EleutherAI/gpt-neo-1.3B")

# Configuración de la API de Unsplash
UNSPLASH_ACCESS_KEY = os.environ.get("QKOHMYhWLib3jioqFghx2ZUJXpiH_f1K5aHt_1okJbI")
api_url = "https://api.unsplash.com/photos/random?orientation=landscape&per_page=1"

# Configuración de la API de ImageBB
IMGBB_API_KEY = os.environ.get("ec3a2919230df7600e65ff9e0e5523db")
IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"

# Configuración del modelo de generación de texto
model = pipeline('text-generation', model='EleutherAI/gpt-neo-1.3B', device=0)


def generate_story(idea):
    set_seed(42)
    story = model(idea, max_length=100, do_sample=True)
    return [sent.capitalize() for sent in story[0]['generated_text'].split('.')][:5]


def get_image():
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    response = requests.get(api_url, headers=headers)
    json_data = json.loads(response.text)
    image_url = json_data[0]["urls"]["regular"]
    return image_url


def generate_gif(image_urls):
    images = []
    for url in image_urls:
        image = Image.open(urllib.request.urlopen(url))
        image = image.resize((512, 512))
        images.append(image)
    imageio.mimsave("story.gif", images, duration=1)


def upload_to_imgbb(filename):
    with open(filename, "rb") as file:
        url = IMGBB_UPLOAD_URL
        payload = {"key": IMGBB_API_KEY, "image": file.read()}
        res = requests.post(url, payload)
        if res.ok:
            return res.json()["data"]["url"]
        else:
            return None


# Configuración de la interfaz de usuario con Streamlit
st.title("Generador de historias e imágenes")

option = st.sidebar.selectbox(
    "Selecciona una opción:",
    ("Escribir una idea", "Previsualizar la historia generada por IA", "Previsualizar el GIF resultado del programa")
)

if option == "Escribir una idea":
    idea = st.text_input("Escribe una idea para generar la historia:")
    st.write("Presiona el botón para generar la historia.")
    if st.button("Generar historia"):
        try:
            story = generate_story(idea)
            st.write("Historia generada:")
            for i, sent in enumerate(story):
                st.write(f"{i+1}. {sent}")
            st.session_state["story"] = story
        except Exception as e:
            st.write("Ocurrió un error al generar la historia.")
            st.write(e)

elif option == "Previsualizar la historia generada por IA":
    if "story" in st.session_state:
        story = st.session_state["story"]
        st.write("Historia generada:")
        for i, sent in enumerate(story):
            st.write(f"{i+1}. {sent}")
    else:
        st.write("Primero debes generar una historia.")

elif option == "Previsualizar el GIF resultado del programa":
    if "story" in st.session_state:
        story = st.session_state["story"]
        st.write("Generando imágenes...")
        image_urls = []

        for i in range(5):
            image_url = get_image()
            image_urls.append(image_url)

        generate_gif(image_urls)
        st.write("Subiendo GIF a ImageBB...")
        url = upload_to_imgbb("story.gif")
        st.write(f"¡Listo! Puedes ver tu GIF en {url}")
    else:
        st.write("Primero debes generar una historia.")