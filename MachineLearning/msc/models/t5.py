import os
import re
import json
import evaluate
import numpy as np

from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Seq2SeqTrainingArguments, Seq2SeqTrainer
from transformers import DataCollatorForSeq2Seq

from msc.utils.utility import get_root_path

CHECKPOINT = "t5-small"                                                                         # Define the name of the model checkpoint to be used

PREFIX = "summarize: "                                                                      # Define a prefix to be used for text generation

TOKENIZER = AutoTokenizer.from_pretrained(CHECKPOINT, 
                                          use_fast=False, 
                                          model_max_length=1024, 
                                          truncation_side="left",
                                          )                                                     # Initialize a tokenizer from the pretrained model with specified configurations

ROUGE = evaluate.load("rouge")                                                                  # Load the Rouge evaluation metric for text summarization

def main():                                                                                     # Define the main function for training and evaluating the model

    # Load data
    dataset = create_train_test_split()                                                         # Create a train-test split of the dataset
    tokenized_dataset = dataset.map(preprocess_function, batched=True)                          # Tokenize the dataset using the tokenizer
    data_collator = DataCollatorForSeq2Seq(tokenizer=TOKENIZER, model=CHECKPOINT)               # Create a data collator for preparing data for training

    # Load Model
    model = AutoModelForSeq2SeqLM.from_pretrained(CHECKPOINT)                                   # Load the pretrained model for sequence-to-sequence language modeling

    # Define training arguments
    training_args = Seq2SeqTrainingArguments(
        output_dir=os.path.join(get_root_path(), 'data', 'models', 'checkpoint'),
        evaluation_strategy="epoch",
        learning_rate=1e-5,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        weight_decay=0.01,
        save_total_limit=3,
        num_train_epochs=24,
        predict_with_generate=True,
        fp16=False,
        push_to_hub=False,
    )                                                                                           # Define arguments for training the model, such as output directory, evaluation strategy, batch size, etc.

    # Train model
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["test"],
        tokenizer=TOKENIZER,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )                                                                                           # Initialize a trainer for training the model with specified arguments
    trainer.train()                                                                             # Train the model
    trainer.save_model(output_dir=os.path.join(get_root_path(), 'data', 'models', CHECKPOINT))  # Save the trained model to a specified directory


def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    decoded_preds = TOKENIZER.batch_decode(predictions, skip_special_tokens = True)                 # Decode the predicted sequences to get the text
    labels = np.where(labels != -100, labels, TOKENIZER.pad_token_id)                               # Replace padding tokens with the tokenizer's pad token ID
    decoded_labels = TOKENIZER.batch_decode(labels, skip_special_tokens=True)                       # Decode the ground truth sequences to get the text
    result = ROUGE.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)  # Compute ROUGE scores between the predicted and ground truth text
    prediction_lens = [np.count_nonzero(pred != TOKENIZER.pad_token_id) for pred in predictions]    # Count the number of non-padding tokens in each predicted sequence
    result["gen_len"] = np.mean(prediction_lens)                                                    # Compute the average number of non-padding tokens in the predicted sequences
    return {k: round(v, 4) for k, v in result.items()}                                              # Round the ROUGE scores and return them as a dictionary


def create_train_test_split(train_size=0.7, use_billsum=False):
    if use_billsum:
        dataset = Dataset.from_dict({"text": text, "summary": summary})                             # Create a dataset from text and summary data
        dataset.train_test_split(train_size=train_size)                                             # Split the dataset into train and test sets
    text = []
    summary = []
    data_path = os.path.join(get_root_path(), 'data', 'json')                                       # Get the path to the data directory
    
    for pdf in os.listdir(data_path):
        with open(os.path.join(data_path, pdf), 'r') as f:
            data = json.load(f)                                                                     # Load data from a JSON file
            text.append(re.sub('[^a-zA-ZæøåÆØÅ.]+', ' ', data['text']))                             # Extract text from the data and remove non-alphabetic characters
            summary.append(re.sub('[^a-zA-ZæøåÆØÅ.]+', ' ', data['summary']))                       # Extract summary from the data and remove non-alphabetic characters
    dataset = Dataset.from_dict({"text": text, "summary": summary})                                 # Create a dataset from text and summary data
    return dataset.train_test_split(train_size=train_size)                                          # Split the dataset into train and test sets


def preprocess_function(examples):
    inputs = [PREFIX + doc for doc in examples["text"]]                                             # Add the prefix "summarize: " to each input text
    model_inputs = TOKENIZER(inputs, max_length=1024, truncation=True)                              # Tokenize the input text and limit the length to 1024 tokens
    labels = TOKENIZER(text_target=examples["summary"], max_length=128, truncation=True)            # Tokenize the ground truth summary text and limit the length to 128 tokens
    model_inputs["labels"] = labels["input_ids"]                                                    # Add the tokenized ground truth summary text to the model inputs as "labels"
    return model_inputs
    

if __name__ == "__main__":
    main() # Call the main function if the script is run as the main program