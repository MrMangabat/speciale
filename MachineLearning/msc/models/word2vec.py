import os

from gensim.models import Word2Vec

from msc.data.word2vec_dataset import load_data
from msc.utils.utility import get_root_path


def main():
    tokens = load_data()                                                    # Load data, presumably a list of tokenized sentences, into the 'tokens' variable.
    save_path = os.path.join(get_root_path(), 'data', 'models', 'word2vec') # Generate a file path for saving the trained Word2Vec model by joining multiple directory and file name components using the os.path.join() function.
    if not os.path.exists(save_path):                                       # Check if the directory for saving the model does not exist.
        os.makedirs(save_path)                                              # If not, create the directory using os.makedirs() function.
    model = Word2Vec(sentences=tokens, 
                     vector_size=100, 
                     max_vocab_size=50_000,
                     window=5, 
                     min_count=3,
                     sg=1, 
                     workers=-1)                                            # Create a Word2Vec model with the specified parameters, including the input tokenized sentences, vector size of 100, maximum vocabulary size of 50,000, window size of 5, minimum count of 3, using skip-gram (sg=1) algorithm, and utilizing all available CPU workers for training.
    model.save(os.path.join(save_path, 'word2vec.model'))                   # Save the trained Word2Vec model to the specified file path using the save() method.

if __name__ == '__main__':
    main()  # If the script is being executed as the main module (i.e., not imported as a module in another script), call the main() function to start the training and saving of the Word2Vec model.
