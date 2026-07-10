import sys
import logging
from src.ingestion import run_ingestion_pipeline
from src.rag_engine import evaluate_projects
from src.slide_generator import generate_presentation
from src.github_sync import push_json_to_github

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def job():
    logger.info("=== Starting Project Health Reporting Pipeline ===")
    
    # Phase 1: Ingestion & Normalisation
    raw_projects = run_ingestion_pipeline()
    if not raw_projects:
        logger.warning("Pipeline halted: No valid project data found.")
        return

    # Limit to 10 projects for lightweight local POC execution
    poc_sample = raw_projects[:10]
    logger.info(f"Sampled {len(poc_sample)} projects to prevent API rate limits.")

    # Phase 2: RAG Evaluation Engine
    evaluated_projects = evaluate_projects(poc_sample)
    
    # Phase 3: Executive Synthesis & Slides
    generate_presentation(evaluated_projects)
    
    # Phase 4: GitHub Automation
    push_json_to_github(evaluated_projects)
    
    logger.info("=== Pipeline Execution Complete ===")

def main():
    logger.info("Initializing Automated Project Health Reporting Agent...")
    job()
    sys.exit(0)

if __name__ == "__main__":
    main()