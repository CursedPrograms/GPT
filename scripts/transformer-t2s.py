import transformers
from transformers import TFAutoModelForCausalLM, AutoTokenizer
from gtts import gTTS
import subprocess
import tensorflow as tf
import logging
import os
from bs4 import BeautifulSoup

transformers.logging.set_verbosity_error()
tf.get_logger().setLevel(logging.ERROR)

def generate_text(prompt, model, tokenizer, max_length=50):
    inputs = tokenizer.encode(prompt, return_tensors="tf", max_length=max_length, truncation=True)
    attention_mask = tf.ones_like(inputs)
    outputs = model.generate(
        inputs,
        max_length=max_length,
        num_beams=5,
        no_repeat_ngram_size=2,
        top_k=50,
        top_p=None,
        do_sample=True,
        attention_mask=attention_mask
    )
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_text

def clean_text(text):
    # Remove HTML tags
    soup = BeautifulSoup(text, "html.parser")
    cleaned_text = soup.get_text(separator=" ")

    # Remove unwanted characters
    cleaned_text = cleaned_text.replace("\n", " ").strip()

    return cleaned_text

def text_to_speech(text):
    cleaned_text = clean_text(text)
    tts = gTTS(text=cleaned_text, lang='en', slow=False)
    
    audio_path = "../output/output.mp3"

    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)

    tts.save(audio_path)

    # Open the audio file with the default media player
    try:
        subprocess.run(["start", audio_path], check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

def main():
    model_name = "gpt2"
    model = TFAutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name, pad_token_id=50256)

    while True:
        prompt = input("Enter a prompt (type 'exit' to end): ")
        
        if prompt.lower() == 'exit':
            print("Exiting the program.")
            break

        generated_text = generate_text(prompt, model, tokenizer)

        print("Generated Text:")
        print(generated_text)

        text_to_speech(generated_text)

if __name__ == "__main__":
    main()
