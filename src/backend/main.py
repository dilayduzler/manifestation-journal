from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
import json
import random
from pathlib import Path
from .classifier import ManifestationJournalClassifier
 
app = FastAPI(title="Manifestation Journal API")

#allow frontend to access the backend 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

classifier = None
responses = None


@app.on_event("startup")
def load_model():
    """Loading the model and responses when server starts"""
    global classifier, responses
    
    #i had lots of prints bc the model loading was taking a while and i wanted to make sure it was working and not just hanging. cleaned most of them though, turns out my computer didnt have space.. 
    print("INFO: loading model and responses")
    
    device = torch.device("cpu")
    
    #load the model from the dir
    classifier = ManifestationJournalClassifier.load(
        "src/backend/model/complete_classifier",
        device
    )
    
    with open("src/backend/responses.json", "r") as f:
        responses = json.load(f)
    
    print("INFO:model and responses loaded")


class Message(BaseModel):
    text: str


@app.get("/")
def root():
    return {
        "message": "API is running",
        "status": "good"
    }


@app.post("/predict")
def predict(message: Message):
    if classifier is None:
        return {"error": "Model not loaded"}
    
    text = message.text.lower().strip()
    
    greetings = ["hi", "hey", "hello", "sup", "wassup", "yo", "hii", "heyy"]
    
    # if message is a greeting, return a greeting response with high confidence without even using the model 
    # later gonna handle greetings differently, not in main, with more variety
    if text in greetings:
        return {
            "intent": "greeting",
            "confidence": 0.99,
            "response": random.choice(responses["greeting"]),
            "text": message.text
        }
    
    result = classifier.predict(message.text)
    model_intent = result["intent"]
    model_confidence = result["confidence"]
    
    # same thing as greetings, i added these last minute.. might train the model for story starters maybe?? or make a rule based system for stuff like that using spacy and regex
    story_starters = [
        "you wont believe", "u wont believe", "omg you cant believe", "guess what", "so like", "ok so"
    ]
    
    story_starter_confidence = 0.0
    for starter in story_starters:
        if text.startswith(starter):

            length_factor = max(0.3, 1.0 - (len(text) / 100))
            story_starter_confidence = 0.85 * length_factor
            break
    
    if story_starter_confidence > model_confidence:
        return {
            "intent": "story_starter",
            "confidence": story_starter_confidence,
            "response": random.choice(responses["story_starter"]),
            "text": message.text
        }
    else:
        return {
            "intent": model_intent,
            "confidence": model_confidence,
            "response": random.choice(responses[model_intent]),
            "text": result["text"]
        }