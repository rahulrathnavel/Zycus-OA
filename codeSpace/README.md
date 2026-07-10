# Zycus Project Health Reporting Agent

An enterprise-grade, automated data pipeline designed to evaluate and synthesize project health across large portfolios. The system ingests raw project data, applies deterministic mathematical models, leverages live Large Language Models for qualitative synthesis, and autonomously generates executive presentations and repository artifacts.

## Technology Stack

- Language: Python 3.9+
- Data Normalisation: Pandas, NumPy
- AI Gateway: OpenRouter (meta-llama/llama-3-8b-instruct)
- Presentation Generation: python-pptx
- Orchestration & Automation: Requests, GitHub REST API, python-dotenv

## System Architecture Workflow

```text
+--------------------+       +--------------------+       +--------------------+
|   Raw Data CSV     | ----> |    ingestion.py    | ----> |   rag_engine.py    |
| (Messy, Null Data) |       | (Pandas Cleansing) |       | (Math + LLM Eval)  |
+--------------------+       +--------------------+       +---------+----------+
                                                                    |
+--------------------+       +--------------------+                 |
|    GitHub Repo     | <---- |   github_sync.py   | <---------------+
|   (JSON Artifact)  |       |  (REST API Push)   |                 |
+--------------------+       +--------------------+                 v
                                                          +--------------------+
                                                          | slide_generator.py |
                                                          |  (LLM Synthesis &  |
                                                          |    python-pptx)    |
                                                          +--------------------+
```

## Setup Instructions

1. Clone the repository to your local environment.
2. Initialize a virtual environment and install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory mirroring the following structure:
   ```env
   OPENROUTER_API_KEY="your_openrouter_api_key"
   GITHUB_PAT="your_github_personal_access_token"
   GITHUB_OWNER="your_github_username"
   GITHUB_REPO="your_repository_name"
   ```
4. Place your weekly raw project data files (.csv) into the `data/input/` directory.

## Execution

The pipeline is designed as a single-execution orchestration script perfectly suited for OS-level cron scheduling.

Run the pipeline directly from your terminal:
```bash
python main.py
```

The system will parse the inputs, generate the `Project_Health_Report.pptx` in the `data/output/` directory, and sync the JSON results directly to your designated GitHub repository.
