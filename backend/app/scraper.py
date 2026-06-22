import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


def _resolve_url(url: str, headers: dict, timeout: int = 10) -> str:
    """
    Follows redirects to resolve short/share/mobile links to their canonical URL.
    Uses a HEAD request for speed (no body download).
    """
    try:
        resp = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
        return resp.url
    except Exception:
        return url  # Fallback: return original if resolution fails


def scrape_url(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # --- STEP 1: AUTO-RESOLVE REDIRECTS ---
    # Handles Reddit /s/ share links, mobile links (i.reddit.com, old.reddit.com),
    # URL shorteners (bit.ly, t.co), and any other redirects — all transparently.
    resolved_url = _resolve_url(url, headers)
    
    # Normalize: strip query params, fragments, and trailing slash
    clean_url = resolved_url.split("?")[0].split("#")[0].rstrip("/")

    # --- REDDIT RSS HANDLER ---
    # Strictly match canonical post URLs: /r/{sub}/comments/{id}/...
    if "/r/" in clean_url and "/comments/" in clean_url:
        rss_url = f"{clean_url}/.rss"
        
        try:
            resp = requests.get(rss_url, headers=headers, timeout=15)
            resp.raise_for_status()
            
            root = ET.fromstring(resp.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            
            entries = []
            for entry in root.findall(".//atom:entry", ns):
                title = entry.find("atom:title", ns).text or "No title"
                content_elem = entry.find("atom:content", ns)
                
                content_text = ""
                if content_elem is not None and content_elem.text:
                    soup = BeautifulSoup(content_elem.text, "html.parser")
                    content_text = soup.get_text(separator="\n", strip=True)
                
                entries.append(f"**{title}**\n{content_text}\n")
            
            feed_title_elem = root.find(".//atom:title", ns)
            feed_title = feed_title_elem.text if feed_title_elem is not None else "Reddit Thread"
            
            return feed_title, "\n---\n".join(entries)
            
        except Exception as e:
            return "Reddit RSS Scraping Failed", f"Could not fetch Reddit via RSS: {str(e)}"

    # --- JINA READER HANDLER ---
    difficult_domains = ["twitter.com", "x.com", "instagram.com"]
    is_difficult = any(domain in clean_url for domain in difficult_domains)

    if is_difficult:
        jina_url = f"https://r.jina.ai/{clean_url}"
        try:
            response = requests.get(jina_url, headers=headers, timeout=20)
            response.raise_for_status()
            
            text = response.text
            title = "Scraped via Jina (Title missing)"
            
            lines = text.split("\n")
            if lines and len(lines[0]) > 0 and "Title:" in lines[0]:
                title = lines[0].replace("Title:", "").strip()
            
            return title, text
            
        except Exception as e:
            return "Jina scraping failed", f"Could not fetch content via Jina: {str(e)}"

    # --- STANDARD WEBPAGE HANDLER ---
    try:
        response = requests.get(clean_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        title = soup.title.string.strip() if soup.title else "Untitled"
        
        for element in soup(["script", "style", "nav", "footer", "aside"]):
            element.decompose()
            
        text = soup.get_text(separator="\n", strip=True)
        return title, text
        
    except Exception as e:
        return "Scraping failed", f"Could not scrape the webpage: {str(e)}"
