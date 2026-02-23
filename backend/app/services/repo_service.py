import os
import tempfile
import shutil
from typing import Dict, Any, Optional
from git import Repo, GitCommandError
import httpx
from pathlib import Path
from app.core.constants import GITHUB_API_BASE_URL, GITLAB_API_BASE_URL


class RepoService:
    """Service for interacting with GitHub/GitLab repositories"""

    def __init__(self, source: str = "github", token: Optional[str] = None):
        self.source = source.lower()
        self.token = token
        self.base_url = self._get_base_url()

    def _get_base_url(self) -> str:
        """Get the API base URL for the repository source"""
        if self.source == "github":
            return GITHUB_API_BASE_URL
        elif self.source == "gitlab":
            return GITLAB_API_BASE_URL
        else:
            raise ValueError(f"Unsupported source: {self.source}")

    async def get_repo_info(self, repo_url: str) -> Dict[str, Any]:
        """
        Fetch repository information from GitHub/GitLab API
        """
        owner, repo_name = self._parse_repo_url(repo_url)

        headers = {}
        if self.token:
            if self.source == "github":
                headers["Authorization"] = f"Bearer {self.token}"
            elif self.source == "gitlab":
                headers["PRIVATE-TOKEN"] = self.token

        try:
            async with httpx.AsyncClient() as client:
                if self.source == "github":
                    url = f"{self.base_url}/repos/{owner}/{repo_name}"
                    response = await client.get(url, headers=headers)
                    response.raise_for_status()
                    data = response.json()

                    return {
                        "name": data.get("name"),
                        "description": data.get("description"),
                        "language": data.get("language"),
                        "stars": data.get("stargazers_count", 0),
                        "forks": data.get("forks_count", 0),
                        "url": data.get("html_url"),
                    }

                elif self.source == "gitlab":
                    project_path = f"{owner}/{repo_name}"
                    url = f"{self.base_url}/projects/{project_path.replace('/', '%2F')}"
                    response = await client.get(url, headers=headers)
                    response.raise_for_status()
                    data = response.json()

                    return {
                        "name": data.get("name"),
                        "description": data.get("description"),
                        "language": None,  # GitLab doesn't provide primary language directly
                        "stars": data.get("star_count", 0),
                        "forks": data.get("forks_count", 0),
                        "url": data.get("web_url"),
                    }

        except httpx.HTTPError as e:
            raise Exception(f"Failed to fetch repository info: {str(e)}")

    def clone_repository(self, repo_url: str, destination: Optional[str] = None) -> str:
        """
        Clone a repository to a local directory
        Returns the path to the cloned repository
        """
        if destination is None:
            destination = tempfile.mkdtemp(prefix="archify_repo_")

        try:
            # Add authentication token to URL if provided
            if self.token:
                auth_url = self._add_token_to_url(repo_url)
            else:
                auth_url = repo_url

            print(f"Cloning repository to {destination}")
            Repo.clone_from(auth_url, destination, depth=1)  # Shallow clone
            return destination

        except GitCommandError as e:
            if destination and os.path.exists(destination):
                shutil.rmtree(destination)
            raise Exception(f"Failed to clone repository: {str(e)}")

    def cleanup_repo(self, repo_path: str):
        """Delete cloned repository"""
        if repo_path and os.path.exists(repo_path):
            try:
                shutil.rmtree(repo_path)
            except Exception as e:
                print(f"Error cleaning up repository: {e}")

    def _parse_repo_url(self, repo_url: str) -> tuple:
        """
        Parse repository URL to extract owner and repo name
        Returns (owner, repo_name)
        """
        # Remove .git suffix if present
        repo_url = repo_url.rstrip(".git")

        # Handle different URL formats
        if "github.com" in repo_url or "gitlab.com" in repo_url:
            parts = repo_url.rstrip("/").split("/")
            repo_name = parts[-1]
            owner = parts[-2]
            return owner, repo_name

        raise ValueError(f"Invalid repository URL: {repo_url}")

    def _add_token_to_url(self, repo_url: str) -> str:
        """Add authentication token to repository URL"""
        if not self.token:
            return repo_url

        if self.source == "github":
            # Format: https://oauth2:TOKEN@github.com/owner/repo.git
            if "https://github.com" in repo_url:
                return repo_url.replace("https://github.com", f"https://oauth2:{self.token}@github.com")

        elif self.source == "gitlab":
            # Format: https://oauth2:TOKEN@gitlab.com/owner/repo.git
            if "https://gitlab.com" in repo_url:
                return repo_url.replace("https://gitlab.com", f"https://oauth2:{self.token}@gitlab.com")

        return repo_url
