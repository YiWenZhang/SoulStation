from unsloth import FastLanguageModel
import torch
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# === 1. 配置参数 ===
max_seq_length = 2048 # 支持的长文本长度
dtype = None # 自动检测
load_in_4bit = True # 4bit 量化加载，显存占用极低，一张 T4/3090 都能跑

# === 2. 加载基座模型 (Qwen2.5-7B-Instruct) ===
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Qwen2.5-7B-Instruct", # 自动从 HuggingFace 下载
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# === 3. 配置 LoRA 适配器 (微调的核心) ===
model = FastLanguageModel.get_peft_model(
    model,
    r = 16, # LoRA 秩，越大越强但越慢，16 是性价比之选
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj",],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
    use_rslora = False,
    loftq_config = None,
)

# === 4. 加载你的数据集 ===
# 确保 dataset.json 和脚本在同一目录下
dataset = load_dataset("json", data_files="dataset.json", split="train")

# 格式化 prompt (Qwen 格式)
def formatting_prompts_func(examples):
    instructions = examples["instruction"]
    inputs       = examples["input"]
    outputs      = examples["output"]
    texts = []
    for instruction, input, output in zip(instructions, inputs, outputs):
        # 构建 prompt，这里简单处理，你可以根据需要调整
        text = f"User: {instruction}\n{input}\n\nAssistant: {output}"
        texts.append(text)
    return { "text" : texts, }

dataset = dataset.map(formatting_prompts_func, batched = True,)

# === 5. 设置训练参数 ===
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    packing = False,
    args = TrainingArguments(
        per_device_train_batch_size = 2, # 如果显存不够，改小这个
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 60, # 训练步数，数据少的话 60 步够演示了
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
    ),
)

# === 6. 开始训练 ===
print("开始训练...")
trainer_stats = trainer.train()
print("训练完成！")

# === 7. 导出为 GGUF (关键一步！) ===
print("正在导出为 GGUF 格式...")
# q4_k_m 是推荐的量化精度，体积小速度快，精度损失小
model.save_pretrained_gguf("model_soul_expert", tokenizer, quantization_method = "q4_k_m")
print("导出完成！请查看 model_soul_expert-unsloth.Q4_K_M.gguf")