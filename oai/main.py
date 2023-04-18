#!/usr/bin/env python

import openai
import pyttsx3
import speech_recognition as sr
import dotenv
import os

# .env file
dotenv.load_dotenv()
# OpenAI API key
openai.api_key = os.getenv("api_key")
