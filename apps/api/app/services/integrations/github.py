import httpx
from app.services.integrations.base import BaseIntegrationAdapter
from app.core.logging import logger

class GitHubActionsIntegrationAdapter(BaseIntegrationAdapter):
    """Adapter class implementing GitHub Actions workflow dispatch triggers."""
    
    def get_slug(self) -> str:
        return "github"
        
    async def send_notification(self, payload: dict, settings: dict) -> bool:
        repo_owner = settings.get("repo_owner")
        repo_name = settings.get("repo_name")
        workflow_id = settings.get("workflow_id", "main.yml")
        github_token = settings.get("github_token")
        branch = settings.get("branch", "main")
        
        if not (repo_owner and repo_name and github_token):
            logger.error("GitHub Actions integration missing configuration credentials.")
            return False
            
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/{workflow_id}/dispatches"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {github_token}",
            "User-Agent": "Nomen-Platform"
        }
        
        body = {
            "ref": branch,
            "inputs": {
                "title": payload.get("title", "Nomen Notification"),
                "message": payload.get("message", "")
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                res = await client.post(url, json=body, headers=headers)
                return res.status_code == 204
        except Exception as exc:
            logger.error(f"GitHub Actions dispatch failed: {exc}")
            return False
