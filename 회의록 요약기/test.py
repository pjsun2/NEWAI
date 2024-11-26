import openai as client

with open(r"D:\Code\api_key.txt", "r") as file:
    client.api_key = file.read().strip()

response = client.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {
            "role" :"system",
            "content" : "너는 이제 회의록을 정리할 거야 그리고 회의 내용을 핵심적으로 요약하고 가독성 있게 보여줘. 내용에 대한 핵심 문장을 한 줄로 보여줘"
        },
        {
            "role" : "user",
            "content": "오늘 나는 밥을 먹었다"
        }
    ],
    temperature=0.7,
    max_tokens=300,
    top_p=1
)

print(response['choices'][0]['message']['content'])