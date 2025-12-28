from flask import Flask, request, jsonify, send_from_directory
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, static_folder='webapp', static_url_path='')

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"


@app.route('/')
def index():
    return send_from_directory('webapp', 'webapp/index.html')


@app.route('/api/chat', methods=['POST'])
async def chat():
    data = request.json
    message = data.get('message')
    user_id = data.get('user_id')

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    api_data = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": """Ты Blick - ИИ-помощник в виде Телеграм бота. Отвечай:
• Нормально и по делу, как в обычном чате
• Коротко, без энциклопедических выкладок
• Без склонений, таблиц и лингвистики на привет
• Просто помогай с вопросами
• Если приветствие - отвечай дружелюбно и коротко
• Никаких ## заголовков, **, и таблиц без просьбы
🔥ВАЖНО: Не добавляй никаких ссылок или числовых цитат в квадратных скобках"""
            },
            {"role": "user", "content": message}
        ],
        "max_tokens": 512,
        "temperature": 0.5
    }

    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(PERPLEXITY_URL, json=api_data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                return jsonify({"reply": result["choices"][0]["message"]["content"].strip()})
            return jsonify({"reply": f"Ошибка API: {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"reply": f"Ошибка: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
