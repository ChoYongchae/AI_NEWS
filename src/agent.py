import logging
import yaml
import os
from datetime import datetime
from typing import List, Dict

from .collectors.arxiv import ArxivCollector
from .collectors.huggingface import HuggingFaceCollector
from .utils.llm import LLMUtil
from .utils.email import EmailUtil

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DailyPaperAgent:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.arxiv_collector = ArxivCollector(self.config)
        self.hf_collector = HuggingFaceCollector(self.config)
        self.llm = LLMUtil(self.config)
        self.email_util = EmailUtil(self.config)

    def _load_config(self, path: str) -> Dict:
        if not os.path.exists(path):
            logger.warning(f"Config file {path} not found. Using defaults.")
            return {}
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def wake_up(self):
        """
        Main entry point for the agent to start its daily routine.
        """
        logger.info("Agent Waking Up...")
        
        # 1. Collect Papers
        papers = self.collect_papers()
        
        if not papers:
            logger.info("No new interesting papers found today.")
            return

        # 2. Digest/Summarize Papers
        digest = self.digest_papers(papers)

        # 3. Send Notification
        self.send_notification(digest)
        
        logger.info("Daily routine completed. Going back to sleep.")

    def collect_papers(self) -> List[Dict]:
        logger.info("Collecting papers...")
        arxiv_papers = self.arxiv_collector.collect()
        hf_papers = self.hf_collector.collect()
        
        # Merge and deduplicate (simple dedup by title)
        all_papers = arxiv_papers + hf_papers
        unique_papers = {p['title']: p for p in all_papers}.values()
        
        logger.info(f"Collected {len(unique_papers)} unique papers.")
        return list(unique_papers)

    def digest_papers(self, papers: List[Dict]) -> str:
        logger.info("Summarizing papers...")
        return self.llm.generate_digest(papers)

    def send_notification(self, digest_content: str):
        logger.info("Sending notification...")
        self.email_util.send_email(digest_content)
