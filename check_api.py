from transformers import AutoTokenizer

token = "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"  # token thật của bạn
model_name = "meta-llama/Meta-Llama-3-8B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=token)
