import os
import openai



# XLM Roberta Large - transformer model containing only the encoder of part of the transformer architecture
# T5 or MT5 model for abstract summarization
#https://huggingface.co/course/chapter1/9?fw=pt

# if index placement end is the same as start, create logic that makes these two values the same



# from langchain.chains.summarize import load_summarize_chain

# export OPENAI_API_KEY='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'
secret_key = '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'
os.environ["OPENAI_API_KEY"] = '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'
# openai.api_key = secret_key

