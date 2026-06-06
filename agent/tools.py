from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
from langchain_core.tools import Tool
from ddgs import DDGS

def search_web(query: str) -> str:
    """Search the web using DuckDuckGo and return top results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        
        if not results:
            return "No results found."
        
        formatted = []
        for r in results:
            formatted.append(f"Title: {r['title']}\nURL: {r['href']}\nSummary: {r['body']}\n")
        
        return "\n---\n".join(formatted)
    
    except Exception as e:
        return f"Search failed: {e}"


def scrape_webpage(url: str) -> str:
    """Scrape and return the main text content of a webpage."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove scripts and styles
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        
        text = soup.get_text(separator="\n", strip=True)
        
        # Return first 3000 chars to avoid token limits
        return text[:3000] if len(text) > 3000 else text
    
    except Exception as e:
        return f"Scraping failed: {e}"


# LangChain Tool wrappers
search_tool = Tool(
    name="web_search",
    func=search_web,
    description="Search the web for current information. Input should be a search query string."
)

scrape_tool = Tool(
    name="scrape_webpage",
    func=scrape_webpage,
    description="Scrape the full content of a webpage. Input should be a URL string."
)

tools = [search_tool, scrape_tool]


if __name__ == "__main__":
    # Test search
    print("Testing search tool...")
    result = search_web("LangChain ReAct agent 2024")
    print(result[:500])
    
    print("\nTesting scrape tool...")
    result = scrape_webpage("https://python.langchain.com")
    print(result[:500])