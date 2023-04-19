import openai

openai.api_key = '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'
models = openai.Model.list()
print(models)