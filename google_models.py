import google.generativeai as genai

genai.configure(api_key="AIzaSyApRFfr7ETL1mDv06p_23zyYOrqJ7lkJAM")

models = genai.list_models()
for m in models:
    print(m.name)
