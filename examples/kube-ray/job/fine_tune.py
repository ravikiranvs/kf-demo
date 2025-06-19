import os
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, BitsAndBytesConfig
from datasets import load_dataset
from peft import get_peft_model, LoraConfig, TaskType
import ray.train.huggingface.transformers
import deepspeed

# Print candidate target modules for LoRA injection
def print_lora_target_modules(model):
    target_modules = set()
    for name, module in model.named_modules():
        if "linear" in module.__class__.__name__.lower() or "Linear" in str(type(module)):
            target_modules.add(name.split('.')[-1])
    print("Available LoRA target modules (sampled from layer names):")
    print(sorted(list(target_modules)))

def finetune(model_name: str, dataset_name: str, output_dir: str):
    """
    Fine-tune a pre-trained model on a specific dataset.
    
    Args:
        model_name (str): The name of the pre-trained model to download.
        dataset_name (str): The name of the dataset to download.
    """
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype="float16",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )
    
    # Load model and tokenizer
    model = AutoModelForCausalLM.from_pretrained(model_name, quantization_config=quant_config)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token

    print_lora_target_modules(model)

    # Format: turn (question + schema) -> cypher
    def data_formatter(example):
        prompt = f"## Schema:\n{example['schema']}\n\n## Question:\n{example['question']}\n\nCypher:\n"
        return {
            "prompt": prompt,
            "completion": example["cypher"]
        }

    def tokenize_function(example):
        tokenized = tokenizer(
            example["prompt"] + example["completion"],
            truncation=True,
            padding="max_length",             # or "longest"
            max_length=1024                   # or 4096, adjust accordingly
        )
        raw_prompt_ids = tokenizer(example["prompt"], truncation=True, max_length=1024).input_ids
        prompt_len = len(raw_prompt_ids)
        labels = tokenized["input_ids"].copy()
        labels[:prompt_len] = [-100] * prompt_len
        tokenized["labels"] = labels
        return tokenized

    # dataset = load_dataset(dataset_name)
    dataset = load_dataset(
        dataset_name,
        split={
            "train": "train[:5%]",
            "test":  "test[:5%]"
        }
    )
    dataset = dataset.map(data_formatter)
    dataset = dataset.map(tokenize_function)

    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],  # adjust based on your model
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    dataset_train = dataset["train"].shuffle(seed=47)
    dataset_test = dataset["test"].shuffle(seed=47)

    deepspeed_cfg = {
      "train_micro_batch_size_per_gpu": 1,
      "gradient_accumulation_steps": 2,
      "zero_optimization": {
        "stage": 2,
        "offload_param": {"device": "cpu"},
        "offload_optimizer": {"device": "cpu"},
        "gather_16bit_weights_on_model_save": False
      },
      "fp16": {"enabled": True},
    }

    training_args = TrainingArguments(
        output_dir=output_dir,
        eval_strategy="epoch",
        push_to_hub=False,
        fp16=True,
        label_names=["labels"],
        save_strategy="steps",               # Save checkpoint every N steps
        save_steps=500,                      # Save every 500 steps
        save_total_limit=2,                  # Keep only the last 2 checkpoints
        gradient_accumulation_steps=2,
        per_device_train_batch_size=1,
        ddp_find_unused_parameters=False,
        deepspeed=deepspeed_cfg,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset_train,
        eval_dataset=dataset_test,
    )

    callback = ray.train.huggingface.transformers.RayTrainReportCallback()
    trainer.add_callback(callback)
    trainer = ray.train.huggingface.transformers.prepare_trainer(trainer)
    
    # Resume only if a checkpoint is available
    checkpoint_path = None
    if os.path.exists(output_dir):
        subdirs = [d for d in os.listdir(output_dir) if d.startswith("checkpoint-")]
        if subdirs:
            latest_ckpt = sorted(subdirs, key=lambda x: int(x.split("-")[-1]))[-1]
            checkpoint_path = os.path.join(output_dir, latest_ckpt)
            print(f"Resuming from checkpoint: {checkpoint_path}")
        else:
            print("No checkpoints found. Starting fresh.")
    else:
        print("Output directory does not exist. Starting fresh.")

    trainer.train(resume_from_checkpoint=checkpoint_path)