import json
import logging
from openai import OpenAI
from src.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODELS

logger = logging.getLogger(__name__)

def get_llm_client():
    if not OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY not found. LLM calls will fail.")
    return OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY, timeout=30.0, max_retries=0)

def analyze_blockers_and_reasoning(project_data):
    client = get_llm_client()
    
    prompt = f"""
    You are an expert Project Manager AI. Analyze the following project data:
    Project Name: {project_data.get('Project Name', 'Unknown')}
    Comments / Status: {project_data.get('Comments', 'None')}
    Schedule Variance: {project_data.get('Schedule Variance', 0)} days
    Burn Health Ratio: {project_data.get('Burn Health Ratio', 1.0):.2f}
    
    Task:
    1. Extract explicit blockers from the comments (e.g., "mapping is pending", "dates are impacted").
    2. Weigh their severity and assign a blocker_score between 0.0 (no blockers) and 1.0 (critical blockers).
    3. Provide a concise, plain-English reasoning for the project's health based on Slippage, Burn, and Blockers.
    
    Output strictly valid JSON in the following format:
    {{
        "blocker_score": 0.5,
        "reasoning": "Plain English reasoning here..."
    }}
    """
    
    try:
        completion = client.chat.completions.create(
            model=MODELS["evaluation"],
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            top_p=0.95,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        response_content = completion.choices[0].message.content
        return json.loads(response_content)
    except Exception as e:
        logger.error(f"Error during LLM evaluation: {e}")
        return {"blocker_score": 0.5, "reasoning": "Could not evaluate project health due to API error."}

def calculate_rag_status(project):
    try:
        variance = float(project.get('Schedule Variance', 0))
    except (ValueError, TypeError):
        variance = 0.0

    if variance <= 0:
        slippage_score = 0.0
    else:
        slippage_score = min(variance / 30.0, 1.0)
        
    try:
        burn_ratio = float(project.get('Burn Health Ratio', 1.0))
    except (ValueError, TypeError):
        burn_ratio = 1.0

    if burn_ratio >= 1.0:
        burn_score = 0.0
    else:
        burn_score = 1.0 - burn_ratio 

    llm_eval = analyze_blockers_and_reasoning(project)
    blocker_score = float(llm_eval.get('blocker_score', 0.5))
    
    total_risk = (0.45 * slippage_score) + (0.25 * burn_score) + (0.30 * blocker_score)
    
    if total_risk < 0.33:
        status = "Green"
    elif total_risk < 0.66:
        status = "Amber"
    else:
        status = "Red"
        
    project['Slippage_Score'] = slippage_score
    project['Burn_Score'] = burn_score
    project['Blocker_Score'] = blocker_score
    project['Total_Risk'] = total_risk
    project['RAG_Status'] = status
    project['AI_Reasoning'] = llm_eval.get('reasoning', 'No reasoning provided.')
    
    return project

def evaluate_projects(projects):
    evaluated = []
    logger.info(f"Starting evaluation of {len(projects)} projects...")
    for idx, proj in enumerate(projects):
        logger.info(f"Evaluating project {idx+1}/{len(projects)}: {proj.get('Project Name', 'Unknown')}")
        evaluated_proj = calculate_rag_status(proj)
        evaluated.append(evaluated_proj)
    logger.info("Evaluation complete.")
    return evaluated
