import ray
from ray.train import ScalingConfig, RunConfig
from ray.train.torch import TorchTrainer
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
        run_config=RunConfig(storage_path="./ray_results")
    )
    result = trainer.fit()
    print("Training completed.")
    # Optionally load best checkpoint:
    # ckpt = result.checkpoint.as_directory()
    # print("Checkpoint saved at:", ckpt)