import os
import re
import json
import evaluate
import numpy as np

from datasets import Dataset, load_dataset
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Seq2SeqTrainingArguments, Seq2SeqTrainer
from transformers import MT5ForConditionalGeneration, MT5Tokenizer
from transformers import DataCollatorForSeq2Seq

from msc.utils.utility import get_root_path


MAX_INPUT_LENGTH = 1024                                                                                 # Maximum length of input text for tokenization
MAX_TARGET_LENGTH = 60                                                                                  # Maximum length of target summary for tokenization
CHECKPOINT = "google/mt5-small"                                                                         # Pretrained model checkpoint to use

TOKENIZER = MT5Tokenizer.from_pretrained(CHECKPOINT, use_fast=False)                                    # Load tokenizer from pretrained checkpoint

ROUGE = evaluate.load("rouge")                                                                          # Load ROUGE metric for evaluation

def main():
    dataset = create_train_test_split()                                                                 # Create train/test split of dataset
    tokenized_dataset = dataset.map(preprocess_function, batched=True)                                  # Tokenize dataset using preprocess_function
    tokenized_dataset = tokenized_dataset.remove_columns(dataset["train"].column_names)                 # Remove unnecessary columns from tokenized dataset
    model = MT5ForConditionalGeneration.from_pretrained(CHECKPOINT)                                     # Load model from pretrained checkpoint
    data_collator = DataCollatorForSeq2Seq(tokenizer=TOKENIZER, model=CHECKPOINT, return_tensors="pt")  # Create data collator for Seq2Seq training
    
    training_args = Seq2SeqTrainingArguments(
        output_dir=os.path.join(get_root_path(), 'data', 'models', 'checkpoint'),                       # Output directory for saving trained model
        evaluation_strategy="epoch",                                                                    # Evaluation strategy during training
        learning_rate=1e-4,                                                                             # Learning rate for training
        per_device_train_batch_size=4,                                                                  # Batch size per device for training
        per_device_eval_batch_size=4,                                                                   # Batch size per device for evaluation
        weight_decay=0.01,                                                                              # Weight decay for training
        save_total_limit=3,                                                                             # Maximum number of saved checkpoints
        num_train_epochs=4,                                                                             # Number of training epochs
        push_to_hub=False,                                                                              # Whether to push the trained model to Hugging Face model hub
        predict_with_generate=True,                                                                     # Whether to use generate() method for predictions during evaluation
        fp16=False,                                                                                     # Whether to use mixed-precision training with FP16 (default is False due to potential numerical instability)
    )
    # Train model
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["test"],
        tokenizer=TOKENIZER,
        data_collator=data_collator,
        # compute_metrics=compute_metrics                                                               # Consumes more GPU memory, 
    )
    trainer.train()                                                                                     # Train the model
    trainer.save_model(output_dir=os.path.join(get_root_path(), 'data', 'models', CHECKPOINT))          # Save the trained model to output directory
    

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    decoded_preds = TOKENIZER.batch_decode(predictions, skip_special_tokens=True)                       # Decode predicted summaries
    labels = np.where(labels != -100, labels, TOKENIZER.pad_token_id)                                   # Replace padding tokens with pad_token_id
    decoded_labels = TOKENIZER.batch_decode(labels, skip_special_tokens=True)                           # Decode ground truth summaries
    result = ROUGE.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)      # Compute ROUGE scores
    prediction_lens = [np.count_nonzero(pred != TOKENIZER.pad_token_id) for pred in predictions]        # Compute length of generated summaries
    result["gen_len"] = np.mean(prediction_lens)                                                        # Add average summary length as a metric

    return {k: round(v, 4) for k, v in result.items()}                                                  # Return computed metrics with rounded values

def create_train_test_split(train_size=0.7, use_billsum=False):
    if use_billsum:
        dataset = load_dataset("billsum", split="ca_test")                                              # change dataset
        return dataset.train_test_split(train_size=train_size)
        
    text = []
    summary = []
    data_path = os.path.join(get_root_path(), 'data', 'json')
    
    for pdf in os.listdir(data_path):
        with open(os.path.join(data_path, pdf), 'r') as f:
            data = json.load(f)
            text.append(re.sub('[^a-zA-ZæøåÆØÅ.]+', ' ', data['text']))
            summary.append(re.sub('[^a-zA-ZæøåÆØÅ.]+', ' ', data['summary']))
    dataset = Dataset.from_dict({"text": text, "summary": summary})                                     # Create a dataset from text and summary
    return dataset.train_test_split(train_size=train_size)                                              # Split the dataset into train and test sets with the specified train_size

def preprocess_function(examples):
    model_inputs = TOKENIZER(
        examples["text"],
        max_length=MAX_INPUT_LENGTH,
        truncation=True,
    )                                                                                                   # Tokenize the text with a maximum length of MAX_INPUT_LENGTH and truncation
    labels = TOKENIZER(
        examples["summary"], max_length=MAX_TARGET_LENGTH, truncation=True
    )                                                                                                   # Tokenize the summary with a maximum length of MAX_TARGET_LENGTH and truncation
    model_inputs["labels"] = labels["input_ids"]                                                        # Add the tokenized summary to the model_inputs with the key "labels"
    return model_inputs

if __name__ == "__main__":
    main() # Call the main function if this script is run as the main program
