import os
import openai

from dotenv import load_dotenv


load_dotenv()


openai.api_key = os.getenv('OPENAI_API_KEY')


# Set the model and prompt
# Models: text-davinci-003,text-curie-001,text-babbage-001,text-ada-001
model_engine = "text-davinci-003"
prompt = "What colors can the dachshunds be?"

# Set the maximum number of tokens to generate in the response
max_tokens = 256

# Generate a response
completion = openai.Completion.create(
    engine=model_engine,
    prompt=prompt,
    max_tokens=max_tokens,
    temperature=0.5,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
)

# Print the response
print(completion)
print(completion.choices[0].text)
