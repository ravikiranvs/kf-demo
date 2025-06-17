import ray
from ray.train import ScalingConfig, RunConfig, FailureConfig, Checkpoint
from ray.train.torch import TorchTrainer
import mlflow
import os
import ray.train.huggingface.transformers
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

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
        
        mlflow.set_experiment("finetuned-qwen2.5")
        with mlflow.start_run():
            mlflow.transformers.log_model(
                transformers_model=checkpoint_path,
                artifact_path="transformers_model",
                task="text-generation",
                save_pretrained=True  # set False if you prefer reference-only logging :contentReference[oaicite:1]{index=1}
            )
            print("Checkpoint saved to MLFlow")