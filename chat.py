import random
import json
import torch
import re

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load intents from file with error handling
try:
    with open('intents.json', 'r') as json_data:
        intents = json.load(json_data)
except FileNotFoundError:
    print("Error: intents.json file not found.")
    exit()
except json.JSONDecodeError:
    print("Error: Failed to parse intents.json file.")
    exit()

# Load data from pre-trained model file
try:
    FILE = "data.pth"
    data = torch.load(FILE)
except FileNotFoundError:
    print("Error: Pre-trained model file 'data.pth' not found.")
    exit()

# Extract data from loaded file
input_size = data.get("input_size")
hidden_size = data.get("hidden_size")
output_size = data.get("output_size")
all_words = data.get('all_words')
tags = data.get('tags')
model_state = data.get("model_state")

# Initialize and load model
model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Clarkie"

def get_response(msg, threshold=0.75):
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > threshold:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                response = random.choice(intent['responses'])
                # if "http" in response and "<a" not in response:
                #     # Format the link to be clickable
                #     #response = re.sub(r'(http[s]?://\S+)', r'<a href="\1">\1</a>', response)
                #     #response = re.sub(r'(http[s]?://\S+)', r'<a href="\1">\1</a>', response, count=1)
                #    return response

                return response
    
    return "Please visit clark website for more details <a> https://www.clarku.edu</a>"

if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        sentence = input("You: ")
        if sentence.lower() == "quit":
            break

        resp = get_response(sentence)
        print(resp)
