import time
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.analysis import Analysis, AnalysisStatus
from app.models.repository import Repository
from app.models.settings import SystemSettings
from app.services.code_analyzer import CodeAnalyzer
from app.services.llm_service import LLMService
from app.services.repo_service import RepoService


class AnalysisService:
    """Orchestrates the complete code analysis workflow"""

    def __init__(self, db: Session):
        self.db = db

    async def run_analysis(self, analysis_id: int) -> Analysis:
        """
        Main method to run complete repository analysis
        """
        # Get analysis record
        analysis = self.db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise ValueError(f"Analysis {analysis_id} not found")

        # Update status
        analysis.status = AnalysisStatus.RUNNING
        self.db.commit()

        start_time = time.time()

        try:
            # Get repository
            repository = self.db.query(Repository).filter(
                Repository.id == analysis.repository_id
            ).first()

            if not repository:
                raise ValueError(f"Repository {analysis.repository_id} not found")

            # Get system settings for repo access
            repo_service = self._get_repo_service(repository.source)

            # Clone repository
            repo_path = repo_service.clone_repository(repository.url)

            try:
                # Get LLM service first (needed for both suggestions and AI enhancement)
                llm_service = await self._get_llm_service()

                # Analyze code with AI enhancement (Premium Feature)
                code_analyzer = CodeAnalyzer()
                use_ai_enhancement = True  # Enable AI-enhanced analysis for deeper insights
                analysis_results = code_analyzer.analyze_repository(
                    repo_path,
                    use_ai_enhancement=use_ai_enhancement,
                    llm_service=llm_service
                )

                # Generate AI suggestions
                suggestions = llm_service.generate_analysis_suggestions(analysis_results)

                # Update analysis with results
                scores = analysis_results.get("scores", {})
                analysis.maintainability_score = scores.get("maintainability", 0)
                analysis.reliability_score = scores.get("reliability", 0)
                analysis.scalability_score = scores.get("scalability", 0)
                analysis.security_score = scores.get("security", 0)
                analysis.overall_score = scores.get("overall", 0)

                analysis.code_metrics = analysis_results.get("code_metrics")
                analysis.architecture_patterns = analysis_results.get("architecture")
                analysis.dependencies = analysis_results.get("dependencies")
                analysis.suggestions = suggestions
                analysis.detailed_report = analysis_results

                # Update repository with detected language and framework
                architecture = analysis_results.get("architecture", {})
                if architecture.get("language") and architecture["language"] != "unknown":
                    repository.language = architecture["language"]
                    # Add frameworks to description if detected
                    if architecture.get("frameworks"):
                        frameworks_str = ", ".join(architecture["frameworks"])
                        if repository.description and frameworks_str not in repository.description:
                            repository.description = f"{repository.description} | Frameworks: {frameworks_str}"
                        elif not repository.description:
                            repository.description = f"Frameworks: {frameworks_str}"

                # Extract issues from high complexity functions
                complexity = analysis_results.get("complexity", {})
                issues = []
                for func in complexity.get("high_complexity_functions", []):
                    issues.append({
                        "type": "complexity",
                        "severity": "warning",
                        "message": f"High complexity in function '{func['name']}'",
                        "details": func
                    })
                analysis.issues = issues

                analysis.status = AnalysisStatus.COMPLETED

            finally:
                # Cleanup cloned repository
                repo_service.cleanup_repo(repo_path)

        except Exception as e:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)

        # Calculate duration
        analysis.analysis_duration = time.time() - start_time
        self.db.commit()

        return analysis

    def _get_repo_service(self, source: str) -> RepoService:
        """Get repository service with token from settings"""
        token = None

        if source == "github":
            setting = self.db.query(SystemSettings).filter(
                SystemSettings.key == "github_token"
            ).first()
            if setting:
                token = setting.value

        elif source == "gitlab":
            setting = self.db.query(SystemSettings).filter(
                SystemSettings.key == "gitlab_token"
            ).first()
            if setting:
                token = setting.value

        return RepoService(source=source, token=token)

    async def _get_llm_service(self) -> LLMService:
        """Get LLM service based on system settings"""
        # Get LLM provider settings
        provider_setting = self.db.query(SystemSettings).filter(
            SystemSettings.key == "llm_provider"
        ).first()
        provider = provider_setting.value if provider_setting else "claude"

        # Get API key
        api_key_setting = self.db.query(SystemSettings).filter(
            SystemSettings.key == f"{provider}_api_key"
        ).first()

        if not api_key_setting or not api_key_setting.value:
            raise ValueError(f"API key for {provider} not configured")

        # Get additional settings for Azure
        endpoint = None
        deployment_name = None
        model = None

        if provider == "azure":
            endpoint_setting = self.db.query(SystemSettings).filter(
                SystemSettings.key == "azure_endpoint"
            ).first()
            deployment_setting = self.db.query(SystemSettings).filter(
                SystemSettings.key == "azure_deployment_name"
            ).first()

            endpoint = endpoint_setting.value if endpoint_setting else None
            deployment_name = deployment_setting.value if deployment_setting else None

        return LLMService(
            provider=provider,
            api_key=api_key_setting.value,
            model=model,
            endpoint=endpoint,
            deployment_name=deployment_name
        )
