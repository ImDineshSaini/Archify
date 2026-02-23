import time
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.analysis import Analysis, AnalysisStatus
from app.models.repository import Repository
from app.repositories.settings_repository import SettingsRepository
from app.repositories.repository_repository import RepositoryRepository
from app.services.code_analyzer import CodeAnalyzer
from app.services.llm_service import LLMService
from app.services.repo_service import RepoService


class AnalysisService:
    """Orchestrates the complete code analysis workflow"""

    def __init__(self, db: Session):
        self.db = db
        self.settings_repo = SettingsRepository(db)
        self.repo_repo = RepositoryRepository(db)

    async def run_analysis(self, analysis_id: int) -> Analysis:
        """Main method to run complete repository analysis"""
        analysis = self.db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise ValueError(f"Analysis {analysis_id} not found")

        analysis.status = AnalysisStatus.RUNNING
        self.db.commit()

        start_time = time.time()

        try:
            repository = self.repo_repo.find_by_id(analysis.repository_id)
            if not repository:
                raise ValueError(f"Repository {analysis.repository_id} not found")

            repo_service = self._get_repo_service(repository.source)
            repo_path = repo_service.clone_repository(repository.url)

            try:
                llm_service = self._get_llm_service()

                code_analyzer = CodeAnalyzer()
                analysis_results = code_analyzer.analyze_repository(
                    repo_path,
                    use_ai_enhancement=True,
                    llm_service=llm_service,
                )

                if analysis_results.get("directory_tree"):
                    deep_analysis = self._run_deep_analysis(
                        llm_service=llm_service,
                        directory_tree=analysis_results["directory_tree"],
                        basic_analysis=analysis_results,
                    )
                    analysis_results["deep_analysis"] = deep_analysis

                suggestions = llm_service.generate_analysis_suggestions(analysis_results)

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

                architecture = analysis_results.get("architecture", {})
                if architecture.get("language") and architecture["language"] != "unknown":
                    repository.language = architecture["language"]
                    if architecture.get("frameworks"):
                        frameworks_str = ", ".join(architecture["frameworks"])
                        if repository.description and frameworks_str not in repository.description:
                            repository.description = f"{repository.description} | Frameworks: {frameworks_str}"
                        elif not repository.description:
                            repository.description = f"Frameworks: {frameworks_str}"

                complexity = analysis_results.get("complexity", {})
                issues = []
                for func in complexity.get("high_complexity_functions", []):
                    issues.append({
                        "type": "complexity",
                        "severity": "warning",
                        "message": f"High complexity in function '{func['name']}'",
                        "details": func,
                    })
                analysis.issues = issues

                analysis.status = AnalysisStatus.COMPLETED

            finally:
                repo_service.cleanup_repo(repo_path)

        except Exception as e:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)

        analysis.analysis_duration = time.time() - start_time
        self.db.commit()

        return analysis

    def _get_repo_service(self, source: str) -> RepoService:
        """Get repository service with token from settings"""
        token = None
        token_key = f"{source}_token"
        setting = self.settings_repo.get_by_key(token_key)
        if setting:
            token = setting.value

        return RepoService(source=source, token=token)

    def _get_llm_service(self) -> LLMService:
        """Get LLM service based on system settings"""
        provider_setting = self.settings_repo.get_by_key("llm_provider")
        provider = provider_setting.value if provider_setting else "claude"

        api_key_setting = self.settings_repo.get_by_key(f"{provider}_api_key")
        if not api_key_setting or not api_key_setting.value:
            raise ValueError(f"API key for {provider} not configured")

        endpoint = None
        deployment_name = None
        model = None

        if provider == "azure":
            endpoint_setting = self.settings_repo.get_by_key("azure_endpoint")
            deployment_setting = self.settings_repo.get_by_key("azure_deployment_name")
            endpoint = endpoint_setting.value if endpoint_setting else None
            deployment_name = deployment_setting.value if deployment_setting else None

        return LLMService(
            provider=provider,
            api_key=api_key_setting.value,
            model=model,
            endpoint=endpoint,
            deployment_name=deployment_name,
        )

    def _run_deep_analysis(
        self,
        llm_service: LLMService,
        directory_tree: str,
        basic_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run multi-stage deep analysis with layer-by-layer examination."""
        deep_analysis = {
            "layers": {},
            "synthesis": {},
            "analysis_completed": False,
            "errors": [],
        }

        layer_methods = [
            ("security", llm_service.analyze_security_layer),
            ("performance", llm_service.analyze_performance_layer),
            ("testing", llm_service.analyze_testing_layer),
            ("devops", llm_service.analyze_devops_layer),
            ("code_quality", llm_service.analyze_code_quality_layer),
        ]

        try:
            for layer_name, method in layer_methods:
                try:
                    deep_analysis["layers"][layer_name] = method(directory_tree, basic_analysis)
                except Exception as e:
                    deep_analysis["errors"].append(f"{layer_name} analysis failed: {str(e)}")
                    deep_analysis["layers"][layer_name] = {"error": str(e)}

            try:
                synthesis = llm_service.synthesize_deep_analysis(
                    security_analysis=deep_analysis["layers"].get("security", {}),
                    performance_analysis=deep_analysis["layers"].get("performance", {}),
                    testing_analysis=deep_analysis["layers"].get("testing", {}),
                    devops_analysis=deep_analysis["layers"].get("devops", {}),
                    code_quality_analysis=deep_analysis["layers"].get("code_quality", {}),
                    basic_analysis=basic_analysis,
                )
                deep_analysis["synthesis"] = synthesis
                deep_analysis["analysis_completed"] = True
            except Exception as e:
                deep_analysis["errors"].append(f"Synthesis failed: {str(e)}")
                deep_analysis["synthesis"] = {"error": str(e)}

        except Exception as e:
            deep_analysis["errors"].append(f"Deep analysis failed: {str(e)}")
            deep_analysis["analysis_completed"] = False

        return deep_analysis
