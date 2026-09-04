from g4f.client import Client

client = Client()

def get_gpt_answer(content: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": content}],
        web_search=True
    )
    answer = response.choices[0].message.content
    return answer