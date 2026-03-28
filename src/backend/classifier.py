import torch
import torch.nn as nn
from transformers import DistilBertModel, AutoTokenizer

# see training script for details 

class CustomIntentClassifier(nn.Module):
    def __init__(self, num_classes, dropout_rate=0.3):
        super(CustomIntentClassifier, self).__init__()

        self.bert = DistilBertModel.from_pretrained("distilbert-base-uncased")

        for param in self.bert.parameters():
            param.requires_grad = False

        self.dropout1 = nn.Dropout(dropout_rate)

        self.fc1 = nn.Linear(768, 512)
        self.relu1 = nn.ReLU()
        self.bn1 = nn.BatchNorm1d(512)
        self.dropout2 = nn.Dropout(dropout_rate)

        self.fc2 = nn.Linear(512, 256)
        self.relu2 = nn.ReLU()
        self.bn2 = nn.BatchNorm1d(256)
        self.dropout3 = nn.Dropout(dropout_rate)

        self.fc3 = nn.Linear(256, 128)
        self.relu3 = nn.ReLU()
        self.bn3 = nn.BatchNorm1d(128)
        self.dropout4 = nn.Dropout(dropout_rate)

        self.fc4 = nn.Linear(128, num_classes)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.last_hidden_state[:, 0, :]

        x = self.dropout1(pooled_output)

        x = self.fc1(x)
        x = self.relu1(x)
        x = self.bn1(x)
        x = self.dropout2(x)

        x = self.fc2(x)
        x = self.relu2(x)
        x = self.bn2(x)
        x = self.dropout3(x)

        x = self.fc3(x)
        x = self.relu3(x)
        x = self.bn3(x)
        x = self.dropout4(x)

        logits = self.fc4(x)
        return logits


class ManifestationJournalClassifier:
    def __init__(self, model, tokenizer, intent_to_id, id_to_intent, device):
        self.model = model
        self.tokenizer = tokenizer
        self.intent_to_id = intent_to_id
        self.id_to_intent = id_to_intent
        self.device = device
        self.model.eval()

    def _apply_rules(self, text, model_prediction, confidence):
        text_lower = text.lower().strip()

        suicide_keywords = [
            "kms", "kill myself", "end it all", "wanna die",
            "want to die", "no reason to live"]

        for keyword in suicide_keywords:
            if keyword in text_lower:
                return "struggling", 0.95, True

        exact_matches = {
            "omg": ("celebrating", 0.90),
            "yesss": ("celebrating", 0.90),
            "lets fucking go": ("celebrating", 0.92),
            "fuck yeah": ("celebrating", 0.92),
            "slay": ("celebrating", 0.88),
            "w": ("celebrating", 0.85),
            "lmao": ("neutral", 0.80),
            "lol": ("neutral", 0.80),
            "bruh": ("neutral", 0.75),
            "bye": ("ending", 0.92),
            "gtg": ("ending", 0.92),
            "ttyl": ("ending", 0.92),
            "gn": ("ending", 0.90),
            "nvm": ("ending", 0.85),
            "ugh": ("struggling", 0.80)}

        if text_lower in exact_matches:
            intent, conf = exact_matches[text_lower]
            return intent, conf, True

        if model_prediction == "celebrating":
            obvious_negatives = [
                "i hate", "hate this", "nothing works", "always fails",
                "cant even", "so done", "fuck this"]

            for neg in obvious_negatives:
                if neg in text_lower:
                    return "struggling", 0.80, True

        if text_lower.startswith("what if "):
            if model_prediction != "struggling":
                return "struggling", 0.78, True

        return model_prediction, confidence, False

    def predict(self, text):
        encoding = self.tokenizer(
            text,
            max_length=256,
            padding="max_length",
            truncation=True,
            return_tensors="pt")

        input_ids = encoding["input_ids"].to(self.device)
        attention_mask = encoding["attention_mask"].to(self.device)

        with torch.no_grad():
            logits = self.model(input_ids, attention_mask)
            probs = torch.nn.functional.softmax(logits, dim=-1)
            predicted_class = torch.argmax(probs, dim=-1).item()
            model_confidence = probs[0][predicted_class].item()

        model_intent = self.id_to_intent[predicted_class]

        final_intent, final_confidence, rule_applied = self._apply_rules(text, model_intent, model_confidence)

        return {
            "text": text,
            "intent": final_intent,
            "confidence": final_confidence,
            "model_prediction": model_intent,
            "model_confidence": model_confidence,
            "rule_override": rule_applied}


    @classmethod
    def load(cls, model_dir, device):
        print("INFO: loading model from directory:", model_dir)
        
        tokenizer = AutoTokenizer.from_pretrained(f"{model_dir}/tokenizer")
        print("INFO: tokenizer loaded")
        checkpoint = torch.load(f"{model_dir}/model.pt", map_location=device)
        print("INFO: checkpoint loaded")
        
        model = CustomIntentClassifier(
            num_classes=checkpoint["num_classes"],
            dropout_rate=checkpoint["dropout_rate"])
        print("INFO: model created")
        
        model.load_state_dict(checkpoint["model_state_dict"])
        model = model.to(device)
        model.eval()
        
        classifier = cls(
            model=model,
            tokenizer=tokenizer,
            intent_to_id=checkpoint["intent_to_id"],
            id_to_intent=checkpoint["id_to_intent"],
            device=device
        )
        
        print("okayy")
        return classifier