import os
import json
import base64
import requests
import logging
from src.config import GITHUB_PAT, GITHUB_OWNER, GITHUB_REPO, OUTPUT_DIR

logger = logging.getLogger(__name__)

def push_json_to_github(projects):
    output_file = os.path.join(OUTPUT_DIR, "project_health_report.json")
    try:
        with open(output_file, 'w') as f:
            json.dump(projects, f, indent=4)
        logger.info(f"Report saved locally to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save JSON locally: {e}")
        return False

    if not GITHUB_PAT or GITHUB_PAT == "mock_pat_for_simulation":
        logger.info("GitHub PAT is missing or mock. Simulating GitHub push instead of actual API call.")
        logger.info(f"Simulated Push: {len(projects)} records committed to {GITHUB_OWNER}/{GITHUB_REPO}.")
        return True

    file_path = "data/output/project_health_report.json"
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{file_path}"
    headers = {
        "Authorization": f"token {GITHUB_PAT}",
        "Accept": "application/vnd.github.v3+json"
    }

    content_str = json.dumps(projects, indent=4)
    content_b64 = base64.b64encode(content_str.encode('utf-8')).decode('utf-8')

    sha = None
    try:
        logger.info("Checking if file exists on GitHub to get SHA...")
        get_resp = requests.get(url, headers=headers)
        if get_resp.status_code == 200:
            sha = get_resp.json().get('sha')
    except Exception as e:
        logger.warning(f"Could not retrieve existing file SHA: {e}")

    payload = {
        "message": "Automated weekly update: Project Health Report",
        "content": content_b64,
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha

    try:
        logger.info("Pushing to GitHub...")
        put_resp = requests.put(url, headers=headers, json=payload, timeout=15.0)
        if put_resp.status_code in [200, 201]:
            logger.info("Successfully pushed JSON to GitHub repository.")
            return True
        else:
            logger.warning(f"GitHub API Error [{put_resp.status_code}]: {put_resp.text}")
            return False
    except Exception as e:
        logger.warning(f"Failed to push to GitHub due to network restrictions: {e}")
        return False
