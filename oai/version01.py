#!/usr/bin/env python

import logging
import os
import signal
import sys

import dotenv
import openai
import pyttsx3
import speech_recognition as sr

import ctrl_c_handler as ctrl_c

# intialize logger
FORMATTER = logging.Formatter(
    "%(asctime)s — %(filename)s:%(lineno)d — %(levelname)s — %(message)s"
)
log = logging.getLogger(__name__)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(FORMATTER)
log.addHandler(console_handler)
log.setLevel(logging.DEBUG)
log.propagate = False

# .env file
dotenv.load_dotenv()
# OpenAI API key
openai.api_key = os.getenv("api_key")
# Initialize text2speech engine
engine = pyttsx3.init()


def transcribe_audio_to_text(filename):
    log.debug("transcribe...")
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio)
        except:
            print("Skipping unknown error!")


def generate_reponse(prompt):
    log.debug("generate response...")
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=4000,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response["choices"][0]["text"]


def speak_text(text):
    log.debug("speak text...")
    engine.say(text)
    engine.runAndWait()


def main():
    # store the original SIGINT handler
    ctrl_c.original_sigint = signal.getsignal(signal.SIGINT)
    # intercept now
    signal.signal(signal.SIGINT, ctrl_c.exit_gracefully)
    while True:
        # Wait for the trigger word "genius"
        print("Say 'computer' to start recording your question...")
        with sr.Microphone() as source:
            recognizer = sr.Recognizer()
            audio = recognizer.listen(source)
            try:
                transcription = recognizer.recognize_google(audio)
                log.debug(f"transcription: {transcription}")
                if transcription.lower() == "exit":
                    ctrl_c.just_exit()
                if transcription.lower() == "computer":
                    log.debug("recognized trigger word")
                    speak_text("What can I do for you?")
                    # Record audio
                    filename = "input.wav"
                    with sr.Microphone() as source:
                        recognizer = sr.Recognizer()
                        source.pause_threshold = 1
                        audio = recognizer.listen(
                            source, phrase_time_limit=None, timeout=None
                        )
                        with open(filename, "wb") as f:
                            log.debug("writing audio file...")
                            f.write(audio.get_wav_data())

                    # Transcribe the recorded audio to text
                    text = transcribe_audio_to_text(filename)
                    if text:
                        print(f"You said: {text}")

                        # Generate response using GPT-3
                        response = generate_reponse(text)
                        print(f"GPT-3 says: {response}")

                        # Read response using text2speech
                        speak_text(response)
            except Exception as e:
                print("An error ocurred: {}".format(e))


if __name__ == "__main__":
    main()
