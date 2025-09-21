import os
from tavily import TavilyClient
from file_tools import read_file, write_file, edit_file

# Initialize Tavily client
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def execute_code(code: str) -> dict:
    try:
        exec_locals = {}
        exec(code, {}, exec_locals)
        # Convert non-serializable objects (like functions, modules) into strings
        safe_locals = {k: str(v) for k, v in exec_locals.items()}
        return {"success": True, "result": safe_locals}
    except Exception as e:
        return {"success": False, "error": str(e)}

def search_internet(query: str):
    resp = tavily_client.search(query, max_results=5)
    results = []
    for r in resp["results"]:
        results.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "snippet": r.get("content", "")
        })
    return results

def web_scrape(url: str):
    return {
        "url": url,
        "content": f"Scraped content from {url} (replace with Firecrawl API)"
    }

TOOLS_REGISTRY = {
    "read_file": read_file,
    "write_file": write_file,
    "edit_file": edit_file,
    "execute_code": execute_code,
    "search_internet": search_internet,
    "web_scrape": web_scrape,
}
