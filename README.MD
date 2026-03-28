# Manifestation Journal App / Intent Classification

## Technical Documentation

**Download the model here:** [Complete Classifier](https://drive.google.com/drive/folders/10gxCpjF708ktU1kyUAlIptGUJRSYoG2c?usp=share_link)

After downloading place the `complete_classifier` folder in:
```
src/backend/model/complete_classifier/
├── model.pt
└── tokenizer/
```
---

## 1. PROJECT OBJECTIVES

### General
This project implements an intent classification model for manifestation journaling. The application analyzes user journal entries and categorizes them into six intentional states: celebrating, struggling, grateful, questioning, ending, and neutral.

### Primary Goals
- Develop a neural network-based intent classifier capable of understanding manifestation-related language and emotional states
- Create a REST API that provides real-time intent classification for journal entries
- Build an accessible web interface that mimics a chatting experience
- Provide contextually appropriate responses based on detected user intent

### Motivation
Creating a texting-app like app for journaling/affirmation stuff your thoughts without using genrative ai for privacy and marketing worries. 
Creating a journaling and affirmations app that feels like a texting app while avoiding generative AI because of privacy concerns and because the use of genAI can be a marketing disadvantage.

---

## 2. DATA

### Data Collection

#### Sources
The current training dataset contains 1,865 labeled examples collected from two main sources. This dataset is temporary and will likely be revised later. At this stage, the goal was to build an initial version quickly and move forward with experimentation.

1. **Reddit Entries**
- Reddit examples were collected manually from different subreddits. 
- Since API access was not available at the time, the data was gathered by hand and manually labeled.

2. **AI-generated**
- More data were generated using several genAI chatbots (ChatGPT, Claude, Gemini, Grok, Mistral)
- Three different prompts were used for each system, and duplicate entries were removed afterward. This helped expand the dataset quickly, but AI-generated examples are not very good quality. 
 
3. **Manual Entries**
- A smaller number of examples were also written manually.

### Planned Improvements
I want to improve the dataset in future. A more suitable source would be comments collected from Tiktok videos related to journaling, affirmations, and manifestation content. And also, At the moment, the dataset covers 6 intents, but this label set could be expanded if the project continues.

#### Legal Status of Data
- AI-generated examples are considered safe to use.
- Reddit data may require further verification regarding reuse and compliance with platform policies.

### Data Format

#### Structure
CSV format with two columns:
```
text,intent
"OMG I got the job!!",celebrating
"I don't know what to do anymore",struggling
"So grateful for my family today",grateful
```

### Data Quality Considerations

#### Strengths
- Balanced class distribution
- Covers common manifestation language patterns
- Includes edge cases
- Diverse message lengths

#### Limitations
- Primarily AI-generated, not fully represent real user language
- Limited sarcasm and cultural context
- No temporal or conversational context
- English-only dataset

#### Output Data Limitations
- The responses JSON file has already been created, but its content is still incomplete. For now, the responses associated with each intent are only temporary placeholder entries.

---

## 3. METHODOLOGY

#### Model Development
- Data collection and labeling
- Model architecture design
- Training on Google Colab (GPU acceleration)
- Hyperparameter tuning
- Rule-based override system development (dropped)

#### Backend Development
- FastAPI application structure

#### Phase 4: Frontend Development
- React application setup
- Chat interface
- Multi-page navigation

### Solved Problems

#### Problem: Greeting Misclassification
**Problem**: Simple greetings ("hi", "hey") classified as "ending" by model
- Model lacks context
- Short messages difficult to classify without context

**Solution**: Pre-classification keyword detection
- Check for exact-match greetings before calling model
- Check for story starters ("you won't believe", "guess what")

**Result**: Natural conversation flow maintained

#### Challenge 4: Response System Design
**Problem**: Need varied, contextually appropriate responses
- Avoid repetitive responses
- Maintain supportive tone
- Handle different intents appropriately

**Solution**: JSON-based response templates
- Response variations
- Random selection on each prediction
- Easy to update without code changes

### Development Environment

#### Training Environment
- **Platform**: Google Colab
- **Hardware**: Tesla T4 GPU (15GB VRAM)
- **Python**: 3.10
- **Key Libraries**: PyTorch 2.1.0, Transformers 4.36.0

#### Deployment Environment
- **Platform**: MacBook Air M1 (8GB RAM)
- **Python**: 3.11.14
- **Backend**: FastAPI + Uvicorn
- **Frontend**: React (Node.js 18+)

---

## 4. IMPLEMENTATION

### Architecture Overview

The system consists of three main components:

```
┌─────────────────┐
│  React Frontend │ (localhost:3000)
│  - Chat UI      │
│  - Home Screen  │
└────────┬────────┘
         │ 
┌─────────────────┐
│  FastAPI API    │ (localhost:8000)
│  - /predict     │
│  - Rule system  │
└────────┬────────┘
         │
┌─────────────────┐
│  Neural Network │
│  - DistilBERT   │
│  - Custom layers│
└─────────────────┘
```

### Neural Network Architecture

#### Model: CustomIntentClassifier

**Base Model**: DistilBERT (distilbert-base-uncased)

**Custom Classification Head**:
```
Input: DistilBERT embeddings (768-dim)
   |
Dropout(0.3)
   |
Layer 1: Linear(768 → 512) + ReLU + BatchNorm1d + Dropout(0.3)
   |
Layer 2: Linear(512 → 256) + ReLU + BatchNorm1d + Dropout(0.3)
   |
Layer 3: Linear(256 → 128) + ReLU + BatchNorm1d + Dropout(0.3)
   |
Output Layer: Linear(128 → 6)
   |
Softmax → Intent probabilities
```

- Frozen DistilBERT: Pre-trained language understanding without overfitting
- Decreasing layer sizes: Progressive dimensionality reduction
- Batch normalization
- Dropout (30%): Regularization to hinder overfitting
- ReLU activation

#### Training Configuration

**Optimizer**: Adam
- Learning rate: 0.001
- Weight decay: 0.01

**Loss Function**: CrossEntropyLoss

**Training Results Observtions**: Overfitting after epoch 7, changed epoch number to 7.

### Rule-Based Override System

#### ManifestationJournalClassifier Wrapper

***WORK IN PROGRESS***

Implements hybrid classification:
1. Get neural network prediction + confidence
2. Apply rule checks
3. Return rule override if confidence higher than model
4. Otherwise return model prediction
#### Rule Categories

**1. Mental Health Safety** 

**2. Exact Match Slang** 

**3. Negative Phrase Override** 

**4. Doubt Phrases** 

### Backend API (FastAPI)

#### API Endpoints

**GET /**
- Health check endpoint
- Returns: `{"message": "API running", "status": "good"}`

**POST /predict**
- Main classification endpoint
- Request body:
  ```json
  {
    "text": "user message here"
  }
  ```
- Response:
  ```json
  {
    "intent": "celebrating",
    "confidence": 0.87,
    "response": "YES!! I'm so proud of you!",
    "text": "original user message"
  }
  ```

#### Pre-Classification Handlers

**Greeting Detection**:
- Exact matches: "hi", "hey", "hello", "sup", "yo"
- Returns greeting responses without calling model

**Story Starter Detection**:
- Phrases: "you won't believe", "guess what", "ok so"
- Length-based confidence calculation
- Compares with model confidence, uses higher

#### Response Template System
- JSON file: `responses.json`
- Random selection using Python's `random.choice()`

### Frontend (React)

#### Application Structure

**App.js** - Main Router
- Manages current page state
- Routes between: Home, Chat, Notes, Help

**Home.js** - Landing Page
- Three main buttons: Chat, Notes, Help
- Card-based layout

**Chat.js** - Main Interface
- Real-time API communication
- Loading states
- Starter message on mount

#### Chat Component Logic

**State Management**:
```javascript
const [messages, setMessages] = useState([
  { sender: 'universe', text: 'Hey! What\'s on your mind?' }
]);
const [input, setInput] = useState('');
const [loading, setLoading] = useState(false);
```

**Message Flow**:
1. User types message
2. Press Enter or click Send
3. Add user message to state
4. Clear input, set loading
5. POST to /predict endpoint
6. Receive response
7. Add message to state

### File Structure

```
Manifestation_Journal_App/
├── pyproject.toml                    
├── README.md                         #You're here!
├── .gitignore
│
├── journal/                          #Virtual environment
│
├── data/
│   └── some_example_data.csv
│
├── notebooks/
│   └── training/
│       └── intentclf.ipynb
│
├── src/
│   └── backend/
│       ├── __init__.py
│       ├── main.py                   
│       ├── classifier.py             
│       ├── responses.json            
│       └── model/
│           └── complete_classifier/
│               ├── model.pt          
│               └── tokenizer/       
│
├── frontend/
│   ├── package.json
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.js
│       ├── App.css
│       ├── Home.js
│       ├── Home.css
│       ├── Chat.js
│       ├── Chat.css
│       └── index.js
│
└── visualizations/
    ├── confusion_matrix.png
    ├── confidence_analysis.png
    └── evaluation_metrics.txt

```

---

## 5. RESULTS AND DISCUSSION

### Model Performance

#### Quantitative Results

**Overall Test Accuracy**: 85.3%

**Per-Class Performance**:

| Intent       | Precision | Recall | F1-Score | Support |
|--------------|-----------|--------|----------|---------|
| celebrating  | 0.74      | 0.77   | 0.76     | 70      |
| struggling   | 0.87      | 0.75   | 0.80     | 71      |
| grateful     | 0.86      | 0.93   | 0.90     | 60      |
| questioning  | 0.93      | 0.86   | 0.89     | 63      |
| ending       | 0.90      | 0.96   | 0.93     | 53      |
| neutral      | 0.85      | 0.89   | 0.87     | 56      |


**Analysis**:
- Best performance: "ending" (F1: 0.93)
- Most balanced: "grateful"
- Lowest: "celebrating" 
- All categories remains above 75%

**Confuion Matrix**: 
The main confusion appears between struggling and celebrating. This is the most problematic error, because these two intents represent very different emotional states. Other notable confusions include celebrating - grateful, celebrating - ending, and questioning - struggling. In comparison, confusion between celebrating and grateful is less critical, as those categories are emotionally closer and may still lead to acceptable responses in practice.

### What Worked Well

1. **Transfer Learning Approach**
   - DistilBERT provided a good base features
   - Custom layers learned task-specific patterns

2. **Hybrid Classification System**
   - Neural network handles general cases
   - Rules will cover edge cases and safety

3. **FastAPI Backend**
   - Simple and fast

4. **React Frontend**
   - Component-based architecture
   - Easy state management
   - Clean UI

5. **Response Template System**
   - Separates classification from response generation
   - Easy to update responses
   - Maintains variety through randomization

### Limitations and Challenges

#### Data Quality
- **Primarily AI-generated**: Doesn't fully represent real user language
- **Limited diversity**: English-only, limited cultural contexts
- **Bias**: AI-generated data might have inherent biases

#### Model Limitations
- **No context memory**: Each message classified independently
- **Sarcasm detection**: Poor performance on sarcastic statements
- **Mixed emotions**: Struggles with messages containing multiple intents

#### Technical Constraints
- **Resource requirements**: 8GB RAM minimum for model loading
- **Loading time**: takes long initial model load

#### Scope Limitations
- **No user accounts**: Can't save conversation history for now
- **No notes feature**: Planned but not implemented
- **No help page**: Planned but not implemented
- **Single language**: English only

### What Could Be Improved

#### Data Collection
- **Scrape real data**: Tiktok and other various sources
- **User studies**: Collect real journal entries with consent
- **More categories**: Add "excited", "anxious", "hopeful", etc.

#### Model Architecture
- **Context window**: Use last 3-5 messages for context
- **Fine-tune BERT**: Unfreeze top layers for task-specific tuning

#### Features
- **Conversation history**: Save past conversations
- **Export functionality**: Download journal
- **Notes app**: Implement planned notes feature
- **Help page**: User guide and documentation

#### Deployment
- **Production hosting**: Deploy to cloud
- **Authentication**: User accounts 
- **Mobile app**: 
- **Model optimization**: 

### Academic Stuff

1. **Practical NLP Application**: Real-world use case for intent classification
2. **Hybrid Systems**: Combining ML with rule-based approaches
3. **Full-Stack Development**: End-to-end system from model to UI

---

## 6. INSTALLATION AND USAGE

### Backend 

```bash
# Clone repository
# Create virtual environment
# Install dependencies

# Run backend
cd src/backend
uvicorn main:app --reload
```

Backend will start on `http://localhost:8000`

### Frontend 

```bash
# In new terminal window go to frontend

# Run frontend
npm start
```

Frontend will open at `http://localhost:3000`
