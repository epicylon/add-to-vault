import requests
from bs4 import BeautifulSoup

def scrape_url(url: str):
    # A standard User-Agent is critical; many sites block default Python requests.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Define domains that are notoriously difficult to scrape (SPAs, aggressive anti-bot)
    difficult_domains = ["reddit.com", "redd.it", "twitter.com", "x.com", "instagram.com"]
    is_difficult = any(domain in url for domain in difficult_domains)

    # --- JINA READER HANDLER (For complex sites) ---
    if is_difficult:
        jina_url = f"https://r.jina.ai/{url}"
        try:
            # Jina returns pre-formatted markdown optimized for LLMs
            response = requests.get(jina_url, headers=headers, timeout=20)
            response.raise_for_status()
            
            text = response.text
            title = "Scraped via Jina (Title missing)"
            
            # Jina often places the title at the very top as "Title: [Title]"
            lines = text.split("\n")
            if lines and len(lines[0]) > 0 and "Title:" in lines[0]:
                title = lines[0].replace("Title:", "").strip()
            
            return title, text
            
        except Exception as e:
            return "Jina scraping failed", f"Could not fetch content via Jina: {str(e)}"

    # --- STANDARD WEBPAGE HANDLER (For everything else) ---
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        title = soup.title.string.strip() if soup.title else "Untitled"
        
        # Remove noise like menus, footers, and scripts
        for element in soup(["script", "style", "nav", "footer", "aside"]):
            element.decompose()
            
        text = soup.get_text(separator="\n", strip=True)
        return title, text
        
    except Exception as e:
        return "Scraping failed", f"Could not scrape the webpage: {str(e)}"
