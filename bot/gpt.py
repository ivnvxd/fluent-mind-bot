from os import getenv
import openai

from dotenv import load_dotenv


load_dotenv()

API_KEY = getenv('OPENAI_API_KEY')
openai.api_key = API_KEY


def gpt3_completion(request):

    completion = openai.Completion.create(
        engine=request['engine'],
        prompt=request['prompt'],
        temperature=request['temperature'],
        max_tokens=request['max_tokens'],
        top_p=1,
        n=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    text = completion.choices[0].text[2:]
    tokens_used = completion.usage.total_tokens

    answer = f'{text} \n\n<i>Tokens used: {tokens_used}</i>'

    print('Human:', request['prompt'])
    print('GPT-3:', text)

    return text


def gpt3_edit(input):

    edit = openai.Edit.create(
        engine="text-davinci-edit-001",
        input=input,
        instruction="translate this sentence",
        temperature=0.5,
        top_p=1,
        n=1
    )

    return edit