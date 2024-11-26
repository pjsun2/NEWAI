import openai as client
import openai
import json
import redis

# 파일에서 API 키 읽기
with open(r"D:\Code\api_key.txt", "r") as file:
    client.api_key = file.read().strip()

class DataService:
    def __init__(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

    def pdf_to_embeddings(self, file: str):
        from PyPDF2 import PdfReader
        reader = PdfReader(file)
        chunks = []
        chunk_length = 1000
        for page in reader.pages:
            text = page.extract_text()
            if text:
                chunks.extend([text[i:i + chunk_length] for i in range(0, len(text), chunk_length)])

        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=chunks
        )

        return [
            {"id": i, "vector": chunk["embedding"], "text": chunks[i]}
            for i, chunk in enumerate(response["data"])
        ]
    
    def load_data_to_redis(self, embeddings):
        for embedding in embeddings:

            key = f"embedding:{embedding['id']}"

            vector_as_json = json.dumps(embedding["vector"])

            self.redis_client.hset(
                key, mapping={
                    "vector" : vector_as_json,
                    "text" : embedding["text"]
            }
        )
    
    


class IntentService:
    def get_intent(self, question: str):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"핵심 질문은 무엇인가요? {question}"}
            ]
        )
        return response['choices'][0]['message']['content']

class RedisService:
    def __init__(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

    def search_redis(self, intent:str):
        keys = self.redis_client.keys("embedding:*")
        results=[]
        for key in keys:
            data = self.redis_client.hgetall(key)
            if intent.lower() in data["text"].lower():
                results.append(data["text"])
        results=results

class ResponseService:
    def generate_response(self, facts, question):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role":"user",
                    "content": f"based on the following facts, answer the quetion: {facts}. Question: {question}"
                }
            ]
        )
        return response['choices'][0]['message']['content']
    
def run(question: str, file: str = 'ExplorersGuide.pdf'):
    data_service = DataService()
    data = data_service.pdf_to_embeddings(file)
    data_service.load_data_to_redis(data)

    intent_service = IntentService()
    intents = intent_service.get_intent(question)

    redis_service = RedisService()
    facts = redis_service.search_redis(intents)

    response_service = ResponseService()
    return response_service.generate_response(facts, question)

file = r"D:\Code\NEWAI\젤다의 전설 전문가 만들기\ExplorersGuide.pdf"
run("보물 상자를 어떻게 찾아야 하니?", file=file)