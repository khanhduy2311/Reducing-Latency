import requests
import json

# URL của Flask API (chạy local)
API_URL = "http://127.0.0.1:5000/api/ask"

# Bộ dữ liệu test gồm nhiều câu hỏi + premises
qa_dataset = [
    {
        "question": "Who created Python?",
        "premises": "Python was created by Guido van Rossum and released in 1991."
    },
    {
        "question": "What is the capital of France?",
        "premises": "Paris is the capital and most populous city of France."
    },
    {
        "question": "What does CPU stand for?",
        "premises": "The CPU stands for Central Processing Unit, which is the brain of the computer."
    }
]

# Danh sách để lưu kết quả trả về
results = []

for item in qa_dataset:
    try:
        response = requests.post(API_URL, json=item)
        response.raise_for_status()  # Gây lỗi nếu có HTTP error

        data = response.json()
        result = {
            "question": item["question"],
            "premises": item["premises"],
            "answer": data.get("answer", "No answer"),
            "score": data.get("score", None)
        }

        print(f"✅ Q: {item['question']} → A: {result['answer']}")
        results.append(result)

    except requests.exceptions.RequestException as e:
        print(f"❌ Lỗi gọi API cho câu: {item['question']}")
        print(e)

# Ghi kết quả vào file JSON
with open("qa_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n📁 Kết quả đã lưu vào qa_results.json")
