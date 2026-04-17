import logging
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

async def get_sector_news(sector: str) -> str:
    """
    Searches for current news and data regarding trade opportunities
    in India for the given sector.
    """
    query = f"{sector} trade opportunities India"
    logger.info(f"Searching web for: {query}")
        
    try:
        # Use DDGS context manager as recommended by duckduckgo-search
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=10))
            
            if not results:
                # Fallback to general search if news returns empty
                results = list(ddgs.text(query, max_results=10))
                
        if not results:
            return "No recent news or data found for this sector."
            
        # Extract title and body snippets to build a comprehensive context
        context_snippets = []
        for index, item in enumerate(results):
            title = item.get("title", "")
            snippet = item.get("body", "")
            date = item.get("date", "")
            source = item.get("source", "")
            
            context_str = f"Result {index+1}:\n"
            if title:
                context_str += f"Title: {title}\n"
            if date:
                context_str += f"Date: {date}\n"
            if source:
                context_str += f"Source: {source}\n"
            if snippet:
                context_str += f"Summary/Snippet: {snippet}\n"
            
            context_snippets.append(context_str)
            
        return "\n".join(context_snippets)
    except Exception as e:
        logger.error(f"Error during duckduckgo search: {e}")
        return f"Error retrieving data: {e}"
