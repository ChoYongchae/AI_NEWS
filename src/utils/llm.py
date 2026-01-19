import os
import logging
from typing import List, Dict
import openai
from tenacity import retry, stop_after_attempt, wait_exponential

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

logger = logging.getLogger(__name__)

class LLMUtil:
    def __init__(self, config: Dict):
        self.config = config
        self.provider = os.getenv("LLM_PROVIDER", "openai")
        self.api_key = os.getenv("LLM_API_KEY")
        self.model = os.getenv("LLM_MODEL", "gpt-4o")

        if self.api_key:
            if self.provider == "openai":
                openai.api_key = self.api_key
            elif self.provider == "gemini":
                if not genai:
                    logger.error("google-genai package not found. Please install it.")
                else:
                    self.gemini_client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("LLM API Key not found. LLM features may not work.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_digest(self, papers: List[Dict]) -> str:
        if not papers:
            return "No papers to summarize."

        if not self.api_key:
            logger.warning("No API Key. Returning raw list.")
            return self._fallback_format(papers)

        language = self.config.get('agent', {}).get('language', 'Korean')
        tone = self.config.get('agent', {}).get('tone', 'Professional yet engaging')
        
        # Prepare context
        papers_text = ""
        for i, p in enumerate(papers, 1):
            papers_text += f"{i}. Title: {p['title']}\n   Source: {p['source']}\n   Abstract: {p['abstract'][:500]}...\n   Link: {p['link']}\n\n"

        focus_instruction = ""
        if self.config.get('agent', {}).get('focus_on_topics', False):
            topics = self.config.get('topics', [])
            if topics:
                focus_instruction = f"""
        Important: The user is specifically interested in: {', '.join(topics)}.
        
        Please prioritize papers related to these topics in your summary. You may group them together or highlight them to ensure they are noticed first.
        """

        prompt = f"""
        You are a research assistant writing a "Morning News" style daily digest of AI papers.
        The audience consists of AI researchers and engineers.
        
        Language: {language}
        Tone: {tone}{focus_instruction}
        
        Task:
        1. Select the most impactful/interesting papers from the list below.
        2. Group them by theme if possible.
        3. Write a concise summary for each selected paper.
        4. Provide the title and link for each.
        5. Add a brief "Why it matters" or "Takeaway" for key papers.
        6. Start with a friendly morning greeting.

        Papers List:
        {papers_text}
        
        Output Format:
        Markdown (HTML compatible).
        """

        try:
            if self.provider == "openai":
                response = openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful AI research assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content
            
            elif self.provider == "gemini" and genai:
                response = self.gemini_client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
                return response.text

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._fallback_format(papers)

    def _fallback_format(self, papers: List[Dict]) -> str:
        """Fallback if LLM fails or no key."""
        output = "# Daily AI Papers (Raw List)\n\n"
        for p in papers:
            output += f"## [{p['title']}]({p['link']})\n"
            output += f"**Source:** {p['source']}\n\n"
            output += f"{p['abstract'][:300]}...\n\n"
        return output
