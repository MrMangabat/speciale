import os                                                                               # Import the 'os' module for working with operating system-related functionalities.
from transformers import pipeline                                                       # Import the 'pipeline' class from the 'transformers' library for using pre-trained models.
from msc.utils.utility import get_root_path                                             # Import the 'get_root_path' function from the 'msc.utils.utility' module.

token_classifier = pipeline(
    "token-classification",                                                             # Specify the task as "token-classification", which is named entity recognition (NER).
    model=os.path.join(get_root_path(), 'data', 'models', 'xlm-roberta-base-ner'),      # Specify the path to the pre-trained model for NER.
    aggregation_strategy="simple"                                                       # Specify the strategy for aggregating predictions. Here, "simple" aggregation strategy is used.
)

print(token_classifier("My name is Sylvain and I work at Hugging Face in Brooklyn."))   # Use the 'token_classifier' pipeline to perform NER on the given input text and print the result.

da_text = """
De systemiske banker har fortsat en solid likviditets
situation. Alle de systemiske banker har en overle
velseshorisont med positiv overskudslikviditet på
mindst fem måneder i Nationalbankens følsomheds
analyse, hvor kundernes efterspørgsel efter likviditet
stiger, men bankerne ikke kan udstede ny nansie
ring.
"""
print(token_classifier(da_text))                                                        # Use the 'token_classifier' pipeline to perform NER on the given Danish input text and print the result.
