import google.generativeai as genai
import os

# Make sure to set your GOOGLE_API_KEY environment variable
# You can get a key from https://aistudio.google.com/app/apikey
genai.configure(api_key="AIzaSyApRFfr7ETL1mDv06p_23zyYOrqJ7lkJAM")

for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)
