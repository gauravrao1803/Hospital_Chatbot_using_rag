from fastapi import FastAPI
from pydantic import BaseModel
from deep_translator import GoogleTranslator

# Safe import
try:
    from model import ask_question
    print("Model imported successfully ✅")
except Exception as e:
    print(f"Model import error: {e}")
    def ask_question(q):
        return "Model Error"

app = FastAPI()

# -------------------------
# Request Schema
# -------------------------

class Question(BaseModel):
    question: str
    lang: str = "en"   # "en" or "hi"

# -------------------------
# Translation Helpers
# -------------------------

def translate_to_english(text, source_lang):
    if source_lang == "en":
        return text
    try:
        return GoogleTranslator(source=source_lang, target="en").translate(text)
    except:
        return text

def translate_from_english(text, target_lang):
    if target_lang == "en":
        return text
    try:
        return GoogleTranslator(source="en", target=target_lang).translate(text)
    except:
        return text

# -------------------------
# API Endpoint
# -------------------------

@app.post("/ask")
def ask_question_endpoint(q: Question):

    user_question = q.question
    user_lang = q.lang.lower()

    print(f"Incoming Question: {user_question} | Language: {user_lang}")

    # Step 1: Translate Hindi → English
    english_query = translate_to_english(user_question, user_lang)

    # Step 2: Get answer from model
    english_answer = ask_question(english_query)

    # Step 3: Translate back to Hindi if needed
    final_answer = translate_from_english(english_answer, user_lang)

    return {"answer": final_answer}

# -------------------------
# Root Route
# -------------------------

@app.get("/")
def root():
    return {"message": "Hospital RAG Server Running ✅"}

# -------------------------
# Run Server
# -------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)