from transformers import pipeline

def get_qa_pipeline():
    model_name = "deepset/roberta-base-squad2"  # change model khác nếu đủ RAM
    device = -1  # CPU (để tránh lỗi bộ nhớ ảo)
    
    qa_pipeline = pipeline("question-answering", model=model_name, device=device)
    
    return qa_pipeline

qa = get_qa_pipeline()
