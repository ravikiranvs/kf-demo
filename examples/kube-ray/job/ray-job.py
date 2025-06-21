import uuid
import ray
from ray.train import ScalingConfig, RunConfig, FailureConfig, Checkpoint
from ray.train.torch import TorchTrainer
import mlflow
import os
import ray.train.huggingface.transformers
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

def train_func():
    # Import inside function to avoid serialization issues
    from fine_tune import finetune
    
    print(f"Running on node: {os.uname().nodename}")
    print(f"CUDA_VISIBLE_DEVICES = {os.environ.get('CUDA_VISIBLE_DEVICES')}")
    
    model_name = "Qwen/Qwen2.5-Coder-7B"
    dataset_name = "neo4j/text2cypher-2025v1"
    finetune(model_name, dataset_name, "checkpoint_dir")

def save_model(train_result):
    # Optionally load best checkpoint:
    with train_result.checkpoint.as_directory() as checkpoint_dir:
        checkpoint_path = os.path.join(
            checkpoint_dir,
            ray.train.huggingface.transformers.RayTrainReportCallback.CHECKPOINT_NAME,
        )

        # Load base model and merge adapter
        model_name = "Qwen/Qwen2.5-Coder-1.5B"
        base = AutoModelForCausalLM.from_pretrained(model_name)
        merged_model = PeftModel.from_pretrained(base, checkpoint_path).merge_and_unload()
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        # merged_dir = os.path.join(checkpoint_path, "ft_merged")
        # os.makedirs(merged_dir, exist_ok=True)
        # merged_model.save_pretrained(merged_dir)
        # tokenizer.save_pretrained(merged_dir)

        gen_ai_pipeline = pipeline(
            "text-generation",
            model=merged_model,
            tokenizer=tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )
        
        mlflow.set_experiment("finetuned_qwen2.5")
        with mlflow.start_run():
            mlflow.transformers.log_model(
                transformers_model=gen_ai_pipeline,
                name="cypher-finetuned-qwen2.5-1b",
                registered_model_name="cypher_finetuned_qwen2.5_1b",
                artifact_path="model",
                pip_requirements=[
                    "accelerate",
                    "transformers[torch]",
                    "torch",
                ],
            )
            print("Checkpoint saved to MLFlow")

if __name__ == "__main__":
    ray.init()
    print(ray.available_resources())
    run_name = str(uuid.uuid4())
    trainer = TorchTrainer(
        train_loop_per_worker=train_func,
        scaling_config=ScalingConfig(num_workers=2, use_gpu=True, placement_strategy="SPREAD"),
        run_config=RunConfig(storage_path="/mnt/nfs", name=run_name, failure_config=FailureConfig(max_failures=3)),
    )
    result = trainer.fit()
    print("Training completed.")

    # save_model(result)
    
    