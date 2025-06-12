import ray
from ray import train
from ray.train.huggingface import TransformersTrainer
from ray.train import ScalingConfig
import os

# Call your training function (from fine_tune.py)
from fine_tune import finetune

def train_fn():
    model_name = "Qwen/Qwen2.5-Coder-1.5B"
    dataset_name = "neo4j/text2cypher-2025v1"
    output_dir = "./finetuned_model"
    finetune(model_name, dataset_name, output_dir)

if __name__ == "__main__":
    ray.init()
    train_fn()
