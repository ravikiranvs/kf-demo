import ray
from ray.train import ScalingConfig, RunConfig, FailureConfig, Checkpoint
from ray.train.torch import TorchTrainer
import mlflow
import os
import ray.train.huggingface.transformers
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

def train_func():
    # Import inside function to avoid serialization issues
    from fine_tune import finetune
    model_name = "Qwen/Qwen2.5-Coder-1.5B"
    dataset_name = "neo4j/text2cypher-2025v1"
    output_dir = "./finetuned_model"
    finetune(model_name, dataset_name, output_dir)

if __name__ == "__main__":
    ray.init()
    trainer = TorchTrainer(
        train_loop_per_worker=train_func,
        scaling_config=ScalingConfig(num_workers=2, use_gpu=True),
        run_config=RunConfig(failure_config=FailureConfig(max_failures=3)),
    )
    result = trainer.fit()
    print("Training completed.")
    
    # Optionally load best checkpoint:
    with result.checkpoint.as_directory() as checkpoint_dir:
        checkpoint_path = os.path.join(
            checkpoint_dir,
            ray.train.huggingface.transformers.RayTrainReportCallback.CHECKPOINT_NAME,
        )

        # Load base model and merge adapter
        base = AutoModelForCausalLM.from_pretrained(model_name)
        merged = PeftModel.from_pretrained(base, checkpoint_path).merge_and_unload()
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        merged_dir = os.path.join(checkpoint_path, "ft_merged")
        os.makedirs(merged_dir, exist_ok=True)
        merged.save_pretrained(merged_dir)
        tokenizer.save_pretrained(merged_dir)
        
        mlflow.set_experiment("finetuned-qwen2.5")
        with mlflow.start_run():
            mlflow.transformers.log_model(
                transformers_model=merged_dir,
                artifact_path="transformers_model",
                task="text-generation",
                save_pretrained=True
            )
            print("Checkpoint saved to MLFlow")