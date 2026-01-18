import urllib.parse
import urllib.request
import feedparser
from datetime import datetime, timedelta
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class ArxivCollector:
    def __init__(self, config: Dict):
        self.config = config
        self.base_url = "http://export.arxiv.org/api/query?"

    def collect(self) -> List[Dict]:
        topics = self.config.get('topics', ['cs.AI'])
        papers = []
        
        # Calculate date range (e.g., last 24 hours)
        # Note: ArXiv API date filtering can be tricky, so we'll fetch recent and filter manually
        
        for topic in topics:
            query = f"all:{topic}"
            encoded_query = urllib.parse.quote(query)
            
            # Fetch more than needed to ensure we cover the time range
            max_results = self.config.get('filters', {}).get('max_papers_per_source', 5) * 2
            
            url = f"{self.base_url}search_query={encoded_query}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
            
            try:
                feed = feedparser.parse(url)
                
                for entry in feed.entries:
                    published = datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%SZ')
                    days_back = self.config.get('filters', {}).get('days_back', 1)
                    
                    if datetime.now() - published <= timedelta(days=days_back + 1): # +1 buffer
                        paper = {
                            'title': entry.title.replace('\n', ' '),
                            'abstract': entry.summary.replace('\n', ' '),
                            'link': entry.link,
                            'source': 'ArXiv',
                            'published': entry.published
                        }
                        papers.append(paper)
                        
            except Exception as e:
                logger.error(f"Error fetching from ArXiv for topic {topic}: {e}")

        # Dedup by link
        seen_links = set()
        unique_papers = []
        for p in papers:
            if p['link'] not in seen_links:
                unique_papers.append(p)
                seen_links.add(p['link'])
                
        # Limit to max per source globally or per topic? Config implies overall or per source.
        # Let's limit total unique papers to a reasonable number to avoid LLM overload
        max_total = self.config.get('filters', {}).get('max_papers_per_source', 5) * len(topics)
        return unique_papers[:max_total]
