import ray
from ray.train import ScalingConfig, RunConfig, FailureConfig
from ray.train.torch import TorchTrainer
import mlflow
import os

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
    ckpt = result.checkpoint.as_directory()
    mlflow.set_experiment("finetuned-qwen2.5")
    with mlflow.start_run():
        mlflow.log_artifacts(ckpt_dir, artifact_path="model")
        print("Checkpoint saved to MLFlow")