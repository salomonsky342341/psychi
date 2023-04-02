import streamlit as st
import transformers
import numpy as np
import imageio
from transformers import GPTNeoForCausalLM, GPT2Tokenizer
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Cargar el modelo GPT-Neo y el tokenizador
model_name = "EleutherAI/gpt-neo-125M"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model_text = GPTNeoForCausalLM.from_pretrained(model_name)

# Cargar el modelo InceptionV3
model_inception = InceptionV3(include_top=False, pooling='avg')

# Función para generar texto
def generate_text(prompt):
    input_ids = tokenizer.encode(prompt, return_tensors='tf')
    text = model_text.generate(input_ids=input_ids, max_length=100, do_sample=True, temperature=0.7)
    return tokenizer.decode(text[0])

# Función para generar texto e imágenes
def generate_text_and_images(idea):
    # Generar el texto
    text = generate_text(idea)

    # Dividir el texto en párrafos
    paragraphs = text.split('\n\n')

    # Generar las imágenes
    images = []
    for paragraph in paragraphs:
        # Generar la imagen utilizando GAN
        noise = np.random.normal(0, 1, (1, 2048))
        text_sequence = tokenizer.texts_to_sequences([paragraph])
        text_padded = pad_sequences(text_sequence, maxlen=2048, padding='post', truncating='post')
        text_feature = model_text([tf.constant(text_padded), tf.constant(noise)])
        img = text_feature.numpy()[0]
        img = img.reshape(299, 299, 3)
        img = np.uint8(img * 255)

        # Preprocesar la imagen utilizando ImageIO
        img_inception = imageio.imresize(img, (299, 299)).astype('float32') / 255.0
        feature = model_inception.predict(np.expand_dims(img_inception, axis=0))

        # Agregar la imagen a la lista de imágenes
        images.append(feature)

    # Unir las imágenes en un GIF
    gif = np.concatenate(images, axis=0)
    gif = np.uint8(gif * 255)
    gif = imageio.mimwrite('generated.gif', [gif], fps=10)

    return paragraphs, gif

# Crear interfaz de usuario con Streamlit
st.title('Generador de Texto e Imágenes')

# Pedir la idea del usuario
idea = st.text_input('Escribe tu idea aquí', '')

# Generar el texto y las imágenes
if idea:
    paragraphs, gif = generate_text_and_images(idea)

    # Mostrar los párrafos
    st.write('**Texto generado:**')
    for paragraph in paragraphs:
        st.write(paragraph)

    # Mostrar el GIF
    st.write('**GIF generado:**')
    with st.spinner('Generando GIF...'):
        st.image('generated.gif', use_column_width=True)
