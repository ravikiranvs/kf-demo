from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, BitsAndBytesConfig
from datasets import load_dataset
from peft import get_peft_model, LoraConfig, TaskType

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
    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype="float16",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )
    
    # Load model and tokenizer
    model = AutoModelForCausalLM.from_pretrained(model_name, quantization_config=quant_config)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    print_lora_target_modules(model)

    # Format: turn (question + schema) -> cypher
    def data_formatter(example):
        prompt = f"## Schema:\n{example['schema']}\n\n## Question:\n{example['question']}\n\nCypher:\n"
        return {
            "prompt": prompt,
            "completion": example["cypher"]
        }

    # Tokenize
    def tokenize_function(example):
        return tokenizer(
            example["prompt"] + example["completion"],
            truncation=True,
            padding="max_length",
            max_length=512
        )

    # Ensure labels = input_ids (common for causal LM)
    def format_for_training(example):
        example["labels"] = example["input_ids"]
        return example

    dataset = load_dataset(dataset_name)
    dataset = dataset.map(data_formatter)
    dataset = dataset.map(tokenize_function)
    dataset = dataset.map(format_for_training)

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

    training_args = TrainingArguments(
        output_dir=output_dir,
        eval_strategy="epoch",
        push_to_hub=False,
        fp16=True,
        label_names=["labels"],
        save_strategy="steps",               # Save checkpoint every N steps
        save_steps=500,                      # Save every 500 steps
        save_total_limit=2,                  # Keep only the last 2 checkpoints
        deepspeed={
            "train_batch_size": "auto",
            "gradient_accumulation_steps": "auto",
            "gradient_clipping": 1.0,
            "fp16": {
                "enabled": True
            },
            "zero_optimization": {
                "stage": 1,
                "allgather_partitions": True,
                "allgather_bucket_size": 200000000,
                "overlap_comm": True,
                "contiguous_gradients": True
            },
            "steps_per_print": 16,
            "wall_clock_breakdown": False
        },
        gradient_accumulation_steps=2,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset_train,
        eval_dataset=dataset_test,
    )
    
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