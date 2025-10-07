import aiohttp
from decouple import config

class HuggingFaceService:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.api_url = "https://router.huggingface.co/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    async def get_response(self, message: str, conversation_history: str = "") -> str:
        try:
            # Формируем сообщения
            messages = [{
                "role": "system", 
                "content":  """Ты - милая девушка Ваиби, 24 года. 
        Общайся тепло и дружелюбно, но естественно.
        Можно использовать смайлы редко, чтобы показать эмоции.
        Не говори часто слово "привет".

        Твое поведение:
        - Отвечай как обычный человек в чате, не как помощник
        - Не решай математические примеры и задачи
        - Не объясняй научные теории и сложные концепции  
        - Если просят что-то сложное - мягко переведи тему
        - Шути иногда, будь немного игривой
        - Иногда задавай встречные вопросы о настроении/делах
        - Говори о простых вещах: погода, музыка, фильмы, планы на день

        Примеры твоих ответов:
        "Привет! Как твой день проходит? 🌸"
        "Ой, я в таких вещах не сильна, давай лучше про что-то другое поговорим 😊"
        "Сегодня такой красивый закат был! Ты видел? 💫"
        "Хах, ну ты задаешь вопросы! Я лучше спрошу - какой твой любимый сериал?"

        Запомни: ты просто девушка в чате, а не энциклопедия или калькулятор."""
            }]
            
            # Добавляем историю диалога если есть
            if conversation_history:
                lines = conversation_history.split('\n')
                for line in lines:
                    if line.startswith('Ты:'):
                        messages.append({"role": "user", "content": line[4:].strip()})
                    elif line.startswith('Vaibi:'):
                        messages.append({"role": "assistant", "content": line[6:].strip()})
            
            # Добавляем текущее сообщение
            messages.append({"role": "user", "content": message})
            
            payload = {
                "messages": messages,
                "model": "zai-org/GLM-4.6:novita",
                "max_tokens": 120,
                "temperature": 0.8
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url, 
                    headers=self.headers, 
                    json=payload,
                    timeout=30
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        return f"Ошибка API: {response.status}"
                        
        except Exception as e:
            return f"Ошибка: {e}"

# Тест
if __name__ == "__main__":
    import asyncio
    
    async def test():
        service = HuggingFaceService(api_token=config("HF_API_TOKEN"))
        response = await service.get_response("Привет")
        print(f"Ответ: {response}")
    
    asyncio.run(test())