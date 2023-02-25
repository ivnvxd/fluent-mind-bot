from os import getenv
import openai

from dotenv import load_dotenv


load_dotenv()

API_KEY = getenv('OPENAI_API_KEY')
openai.api_key = API_KEY


def gpt3_request(request):

    completion = openai.Completion.create(
        engine=request['engine'],
        prompt=request['prompt'],
        temperature=request['temperature'],
        max_tokens=request['max_tokens'],
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    text = completion.choices[0].text[2:]
    tokens_used = completion.usage.total_tokens

    answer = f'{text} \n\n<i>Tokens used: {tokens_used}</i>'

    print('Human:', request['prompt'])
    print('GPT-3:', text)

    return answer
