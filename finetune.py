import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig
from trl import SFTTrainer

# 1. 모델 설정 (Hugging Face 승인 필요)
model_id = "google/gemma-2-2b-it"

# 2. 4비트 양자화 설정 (VRAM 절약)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

# 3. 모델 및 토크나이저 로드
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token # 패딩 토큰 설정

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.bfloat16
)

# 4. LoRA 설정 (가중치 중 극히 일부만 학습)
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "o_proj", "k_proj", "v_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    task_type="CAUSAL_LM",
)

# 5. 데이터셋 로드 및 포맷팅
def formatting_func(example):
    # Gemma 2 대화 형식에 맞춤
    text = f"<start_of_turn>user\n{example['instruction']}<end_of_turn>\n<start_of_turn>model\n{example['output']}<end_of_turn>"
    return {"text": text}

dataset = load_dataset("json", data_files="train.jsonl", split="train")
dataset = dataset.map(formatting_func)

# 6. 트레이너 설정 및 학습 시작
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    args=TrainingArguments(
        output_dir="./gemma2-output",
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        warmup_steps=2,
        max_steps=50, # 테스트용으로 50회만 진행
        learning_rate=2e-4,
        fp16=True, # Windows/NVIDIA 환경
        logging_steps=1,
        optim="paged_adamw_8bit"
    ),
    peft_config=lora_config,
    dataset_text_field="text",
)

print("학습을 시작합니다...")
trainer.train()

# 7. 결과 저장 (LoRA 어댑터만 저장됨)
trainer.model.save_pretrained("./gemma2-lora-adapter")
print("학습 완료 및 저장되었습니다!")