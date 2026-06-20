import requests
from bs4 import BeautifulSoup

def scrape_url(url: str):
    # En standard User-Agent er helt kritisk; Reddit blokkerer alle forespørsler som identifiserer seg som Python.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # --- REDDIT NATIVE JSON HANDLER ---
    if "reddit.com" in url or "redd.it" in url:
        # Fjern query parameters (som ?utm_source=share)
        clean_url = url.split("?")[0]
        if clean_url.endswith("/"):
            clean_url = clean_url[:-1]
        
        json_url = f"{clean_url}.json"
        
        try:
            response = requests.get(json_url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Reddit JSON struktur: data[0] er selve posten, data[1] er kommentarene
            post_data = data[0]["data"]["children"][0]["data"]
            title = post_data.get("title", "Reddit Post")
            author = post_data.get("author", "Unknown")
            selftext = post_data.get("selftext", "")
            
            content_parts = [f"**Post av u/{author}**:\n{selftext}\n\n### Toppkommentarer:\n"]
            
            # Hent toppkommentarer, filtrer ut AutoModerator
            if len(data) > 1:
                comments = data[1]["data"]["children"]
                for comment in comments[:15]:
                    c_data = comment.get("data", {})
                    body = c_data.get("body")
                    c_author = c_data.get("author")
                    if body and c_author and c_author != "AutoModerator":
                        content_parts.append(f"- **u/{c_author}**: {body}\n")
                        
            return title, "\n".join(content_parts)
            
        except Exception as e:
            return "Reddit-skraping feilet", f"Klarte ikke å hente Reddit-data via JSON: {str(e)}"

    # --- STANDARD WEBPAGE HANDLER ---
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        title = soup.title.string.strip() if soup.title else "Uten tittel"
        
        # Fjern støy som menyer, bunntekst og scripts
        for element in soup(["script", "style", "nav", "footer", "aside"]):
            element.decompose()
            
        text = soup.get_text(separator="\n", strip=True)
        return title, text
        
    except Exception as e:
        return "Skraping feilet", f"Klarte ikke å skrape nettsiden: {str(e)}"import requests
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
