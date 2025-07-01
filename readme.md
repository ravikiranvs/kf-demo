# Kubeflow Demos

This repository provides practical examples and code to help you explore and understand **Kubeflow (KF) workflows and experiments**.

---

## Features

* **Example Jupyter Notebooks:** Hands-on demonstrations of Kubeflow pipelines and various features.
* **Ready-to-Run Demos:** Quickly spin up experiments and learn by doing.
* **Beginner-Friendly:** Clear, concise examples designed to help you get started with Kubeflow.

---

## Requirements

Before you begin, ensure you have the following:

* **Charmed Kubeflow** installed on a cluster with **GPU(s)**.
* **MLFlow** integrated with your Kubeflow setup.
* **KServe** installed for model serving within Kubeflow.
* **Hugging Face Login** for accessing models.
* **(Optional)** **Milvus** installed for vector database operations.

---

## Getting Started

1.  **Create a Kubeflow Notebook:**
    * Create a new Kubeflow Notebook instance.
    * Select **"No GPU"** for this notebook.
    * In the advanced options, ensure you enable access to both **Kubeflow Pipelines** and **MLFlow**.
2.  **Clone this Repository:**
    * Within your newly created Kubeflow Notebook, use the source control option to clone this repository.

---

## Examples

| Example               | Details                                                                    |
| :-------------------- | :------------------------------------------------------------------------- |
| **[Inferencing](./examples/inferencing/)** | Deploy and serve a Hugging Face model using KServe.                        |
| **[RAG Ingestion](./examples/rag-ingest/)** | A pipeline for loading documents into a vector database for Retrieval-Augmented Generation. |
| **[LLM Finetuning](./examples/kube-ray/)** | Distributed finetuning of a Hugging Face Large Language Model (LLM) using LoRA, DeepSpeed, Ray, MLFlow, and KServe. |
| **[Katib Tuning](./examples/katib-tuning/)** | Hyperparameter tuning examples leveraging Kubeflow Katib.                  |
| **[ML Model Training](./examples/ml-pipeline/)** | Train a traditional Machine Learning model with pipelines, integrated with MLFlow and KServe. |