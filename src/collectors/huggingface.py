import requests
from bs4 import BeautifulSoup
import re
import feedparser
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class HuggingFaceCollector:
    def __init__(self, config: Dict):
        self.config = config
        self.url = "https://huggingface.co/papers"
        self.arxiv_api_url = "http://export.arxiv.org/api/query?id_list="

    def collect(self) -> List[Dict]:
        logger.info(f"Fetching trending papers from {self.url}...")
        try:
            response = requests.get(self.url)
            if response.status_code != 200:
                logger.error(f"Failed to fetch HF papers page: {response.status_code}")
                return []

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links matching /papers/(\d+\.\d+)
            # Note: The page structure might change, but links to papers usually follow this pattern
            paper_links = soup.find_all('a', href=re.compile(r"/papers/\d+\.\d+"))
            
            arxiv_ids = set()
            for link in paper_links:
                match = re.search(r"(\d+\.\d+)", link['href'])
                if match:
                    arxiv_ids.add(match.group(1))
            
            if not arxiv_ids:
                logger.info("No paper IDs found on HF page.")
                return []
            
            # Limit number of papers if needed, though usually daily list is small (~10-20)
            # Let's take top N
            max_papers = self.config.get('filters', {}).get('max_papers_per_source', 10)
            target_ids = list(arxiv_ids)[:max_papers]
            
            return self._fetch_arxiv_details(target_ids)

        except Exception as e:
            logger.error(f"Error collecting from HF: {e}")
            return []

    def _fetch_arxiv_details(self, ids: List[str]) -> List[Dict]:
        if not ids:
            return []
            
        id_list = ",".join(ids)
        url = f"{self.arxiv_api_url}{id_list}"
        papers = []
        
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                paper = {
                    'title': entry.title.replace('\n', ' '),
                    'abstract': entry.summary.replace('\n', ' '),
                    'link': entry.link,
                    'source': 'Hugging Face (Trending)',
                    'published': entry.published
                }
                papers.append(paper)
        except Exception as e:
            logger.error(f"Error fetching details from ArXiv for IDs {ids}: {e}")
            
        return papers
