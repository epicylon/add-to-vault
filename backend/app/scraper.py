import requests
from bs4 import BeautifulSoup

def scrape_url(url: str) -> tuple[str, str]:
    """
    Downloads a webpage and extracts the title and main text content.
    """
    # We spoof a standard browser user-agent to avoid being blocked by strict sites (e.g., Reddit)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status() # Raises an error if the page is down (e.g., 404)
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Remove unnecessary elements like menus, footers, ad scripts, etc.
    for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
        element.extract()
        
    # Get the title
    title = soup.title.string.strip() if soup.title else "Untitled"
    
    # Get all visible text
    text = soup.get_text(separator='\n')
    
    # Clean up the text (remove unnecessary blank lines and extra spaces)
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)
    
    # Truncate the text to 15,000 characters to save LLM costs and processing time
    return title, cleaned_text[:15000]
