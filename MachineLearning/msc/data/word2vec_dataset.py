# Can take csv and json files as input

import os
import csv
import re
import json
import nltk

from msc.utils.utility import get_root_path

nltk.download('stopwords')                                                                  # Download the 'stopwords' resource from the Natural Language Toolkit (NLTK)
nltk.download('punkt')                                                                      # Download the 'punkt' resource from the NLTK

DATA_PATH = os.path.join(get_root_path(), 'data')                                           # Define the data path using the root path
TRAIN_PATH = os.path.join(DATA_PATH, 'word2vec')                                            # Define the training data path as a subdirectory of the data path
EXTRA_STOPWORDS_PATH = os.path.join(get_root_path(), 'msc', 'resources', 'stopwords.txt')   # Define the path for extra stopwords

def read_json(json_path):
    with open(json_path, 'r') as f:
        json_file = json.load(f)                                                            # Load the JSON file
        sentences = nltk.sent_tokenize(json_file['text'])                                   # Tokenize the text into sentences
        tokens = [preprocess_text(sentence) for sentence in sentences]                      # Preprocess each sentence and store as tokens
        return tokens                                                                       # Return the list of tokens
    
def preprocess_text(text: str):
    stopwords = nltk.corpus.stopwords.words('danish')                                       # Load the Danish stopwords from NLTK
    with open(EXTRA_STOPWORDS_PATH, 'r') as f:
        stopwords.extend(f.read().splitlines())                                             # Load extra stopwords from the specified file and add to the list
    stopwords = set(stopwords)                                                              # Convert the list of stopwords to a set for faster lookup
    # remove numbers and special characters
    text = re.sub("[^A-Za-z]+", " ", text)                                                  # Remove non-alphabetic characters from the text
    tokens = nltk.word_tokenize(text)                                                       # Tokenize the text into words
    tokens = [token.lower() for token in tokens if token.lower() not in stopwords]          # Convert words to lowercase and remove stopwords
    return tokens                                                                           # Return the list of preprocessed tokens
    
def read_article_body(filename):
    tokens = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                sentences = nltk.sent_tokenize(row['article_body'])                         # Tokenize the article body into sentences
                tokens.extend([preprocess_text(sentence) for sentence in sentences])        # Preprocess each sentence and store as tokens
            except (UnicodeDecodeError, UnicodeEncodeError):
                pass                                                                        # Skip any rows that encounter encoding errors
    return tokens                                                                           # Return the list of tokens

def load_data(path = TRAIN_PATH):
    files = os.listdir(path)                                                                # Get the list of files in the specified path
    tokens = []                                                                             # Initialize an empty list to store tokens
    for file in files:
        if file.endswith('.json'):                                                          # If the file is a JSON file
            tokens.extend(read_json(os.path.join(path, file)))                              # Load and preprocess the JSON file
        elif file.endswith('.csv'):                                                         # If the file is a CSV file
            tokens.extend(read_article_body(os.path.join(path, file)))                      # Load and preprocess the CSV file
    return tokens                                                                           # Return the list of tokens

if __name__ == '__main__':
    tokens = load_data() # Load the data and preprocess it into tokens
    print(tokens[0:50]) # Print the first 50 tokens for testing purposes
