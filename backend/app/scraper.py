import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

def scrape_url(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # --- REDDIT RSS HANDLER ---
    if "reddit.com" in url or "redd.it" in url:
        # Clean URL and append .rss
        clean_url = url.split("?")[0].rstrip("/")
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
                    # Reddit embeds HTML inside the XML content. Clean it with BeautifulSoup.
                    soup = BeautifulSoup(content_elem.text, "html.parser")
                    content_text = soup.get_text(separator="\n", strip=True)
                
                entries.append(f"**{title}**\n{content_text}\n")
            
            feed_title_elem = root.find(".//atom:title", ns)
            feed_title = feed_title_elem.text if feed_title_elem is not None else "Reddit Thread"
            
            return feed_title, "\n---\n".join(entries)
            
        except Exception as e:
            return "Reddit RSS Scraping Failed", f"Could not fetch Reddit via RSS: {str(e)}"

    # --- JINA READER HANDLER (For other complex SPAs like X/Twitter) ---
    difficult_domains = ["twitter.com", "x.com", "instagram.com"]
    is_difficult = any(domain in url for domain in difficult_domains)

    if is_difficult:
        jina_url = f"https://r.jina.ai/{url}"
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

    # --- STANDARD WEBPAGE HANDLER (For Substack, blogs, articles) ---
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
        return "Scraping failed", f"Could not scrape the webpage: {str(e)}"import requests
from bs4 import BeautifulSoup

def scrape_url(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    difficult_domains = ["reddit.com", "redd.it", "twitter.com", "x.com", "instagram.com"]
    is_difficult = any(domain in url for domain in difficult_domains)

    # --- JINA READER HANDLER ---
    if is_difficult:
        # Tweak for Reddit: Forsøk å bruke old.reddit.com for å omgå moderne Cloudflare-sjekker
        if "reddit.com" in url:
            url = url.replace("www.reddit.com", "old.reddit.com")

        jina_url = f"https://r.jina.ai/{url}"
        try:
            response = requests.get(jina_url, headers=headers, timeout=20)
            response.raise_for_status()
            
            text = response.text

            # Sjekk om Jina returnerte en "soft error" (vellykket forespørsel, men blokkert av målet)
            if "Target URL returned error" in text or "You've been blocked by network security" in text:
                return "Scraping Blocked", f"The target website actively blocked the scraping attempt. \n\n**Raw output:**\n{text[:300]}"
            
            title = "Scraped via Jina (Title missing)"
            lines = text.split("\n")
            if lines and len(lines[0]) > 0 and "Title:" in lines[0]:
                title = lines[0].replace("Title:", "").strip()
            
            return title, text
            
        except Exception as e:
            return "Jina scraping failed", f"Could not fetch content via Jina: {str(e)}"

    # --- STANDARD WEBPAGE HANDLER ---
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        title = soup.title.string.strip() if soup.title else "Untitled"
        
        for element in soup(["script", "style", "nav", "footer", "aside"]):
            element.decompose()
            
        text = soup.get_text(separator="\n", strip=True)
        return title, text
        
    except Exception as e:
        return "Scraping failed", f"Could not scrape the webpage: {str(e)}"
