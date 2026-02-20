"""AI analysis using Gemini API - Pure API client, no output logic"""
import logging
from typing import Optional, Dict, Any
from google import genai
from google.genai.types import GenerateContentResponse
from .config import config

logger = logging.getLogger(__name__)


class GeminiAPIError(Exception):
    """Custom exception for Gemini API errors"""
    pass


class AIAnalyzer:
    """Pure API client for Gemini - returns data, doesn't print"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.settings.gemini_api_key
        self.client = None
        
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.debug("Gemini client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                raise GeminiAPIError(f"Gemini initialization failed: {e}")
        else:
            logger.debug("GEMINI_API_KEY not set - AI features disabled")
    
    def is_available(self) -> bool:
        """Check if AI analysis is available"""
        return self.client is not None
    
    def analyze_pod_issue(self, pod_data: Dict[str, Any]) -> str:
        """
        Analyze pod issues with AI
        
        Args:
            pod_data: Dictionary containing pod information
            
        Returns:
            str: Analysis result
            
        Raises:
            GeminiAPIError: If API call fails
        """
        if not self.is_available():
            raise GeminiAPIError("AI analysis unavailable - GEMINI_API_KEY not set")
        
        try:
            prompt = self._build_pod_analysis_prompt(pod_data)
            response = self._call_api(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Pod analysis failed: {e}")
            raise GeminiAPIError(f"Analysis failed: {str(e)}")
    
    def analyze_cluster_health(self, cluster_data: Dict[str, Any]) -> str:
        """
        Analyze overall cluster health
        
        Args:
            cluster_data: Dictionary containing cluster metrics
            
        Returns:
            str: Health analysis result
            
        Raises:
            GeminiAPIError: If API call fails
        """
        if not self.is_available():
            raise GeminiAPIError("AI analysis unavailable")
        
        try:
            prompt = self._build_cluster_analysis_prompt(cluster_data)
            response = self._call_api(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Cluster analysis failed: {e}")
            raise GeminiAPIError(f"Analysis failed: {str(e)}")
    
    def _call_api(self, prompt: str) -> GenerateContentResponse:
        """
        Make API call to Gemini
        
        Args:
            prompt: The prompt to send
            
        Returns:
            GenerateContentResponse: API response
            
        Raises:
            GeminiAPIError: If API call fails
        """
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            return response
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise GeminiAPIError(f"API call failed: {str(e)}")
    
    def _build_pod_analysis_prompt(self, pod_data: Dict[str, Any]) -> str:
        """Build prompt for pod analysis"""
        return f"""Analyze this Kubernetes pod issue and provide:
1. Root cause (1 sentence)
2. Impact assessment (1 sentence)
3. Recommended fix (1-2 sentences)

Pod Data:
Name: {pod_data.get('name')}
Status: {pod_data.get('status')}
Containers: {pod_data.get('containers', [])}

Be concise and actionable. Max 100 words."""
    
    def _build_cluster_analysis_prompt(self, cluster_data: Dict[str, Any]) -> str:
        """Build prompt for cluster analysis"""
        return f"""Analyze this Kubernetes cluster health:

Nodes: {cluster_data.get('nodes', {})}
Pods: {cluster_data.get('pods', {})}

Provide:
1. Overall health score (0-100%)
2. Top 2 issues (if any)
3. One recommendation

Be brief. Max 80 words."""


# Global analyzer instance
analyzer = AIAnalyzer()
