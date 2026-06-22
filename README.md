# Add To Vault
The self-hosted backend engine for the ***Add To Vault** ecosystem*. This server handles web scraping, LLM processing, and secure API communication with your Obsidian vault.

**Transparency Notice:** The architecture, backend logic, and frontend codebase were *primarily* written and iterated by Google's Gemini Pro large language model under the direction of a human project manager. The focus is on **function**, **modularity**, and **privacy**.

![alt text](https://raw.githubusercontent.com/epicylon/add-to-vault/refs/heads/demo/scr/atv-screenshot-1.png "Add To Vault Overview")

### Overview
**Add To Vault** is designed to seamlessly integrate the wild web into your Obsidian vault. Instead of relying on expensive third-party SaaS tools, you host this lightweight FastAPI server yourself *(e.g., on a Proxmox node, Raspberry Pi, or VPS)*.

#### How it works:
1. You submit a URL *(via the Web UI or a shortcut)*.

2. The server intelligently scrapes the content (bypassing anti-bot walls using RSS fallbacks and Jina Reader for complex SPAs like Reddit/X).

3. It formats the text using your active **LLM Provider** *(natively supporting Google Gemini, OpenAI, Anthropic, Mistral, Kimi, and local Ollama deployments)* based on your preferred **"Processing Mode"** *(Archivist, Analyst, or Synthesist)*.

4. It cross-references your existing Obsidian tags and file names to generate intelligent ```[[internal links]]```.

5. The companion Obsidian plugin automatically fetches the generated Markdown file and places it securely in your vault.

### Key Features
- **LLM Agnostic:** Bring your own AI. Built-in support for OpenAI, Anthropic, Google Gemini, Mistral, Kimi, and self-hosted privacy-first models via Ollama.

- **Smart Scraping:** Fallback mechanisms for difficult domains.

- **Three Processing Modes:**
  - **Archivist:** *Exact, cleaned-up copy for long-form archiving.*

  - **Analyst:** *Balanced summary with key takeaways.*

  - **Synthesist:** *Ultra-short, extracting only the absolute core concepts.*

- **Multi-Pass Contextual Linking *(Recommended):*** The server analyzes your vault's existing tags and filenames to ensure it only creates valid internal links and tags.

- **Web Dashboard:** A clean, dark-themed UI built with Tailwind CSS for manual link submission and account management.

- **Secure & Private:** JWT Bearer authentication, SQLite database for user settings, and local temporary holding for your notes.

### Getting Started
#### Prerequisites
- Docker and Docker Compose installed on your host machine.

- A free Google Gemini API Key.

#### Installation

1. Clone the repository:

```git clone [https://github.com/epicylon/add-to-vault.git](https://github.com/epicylon/add-to-vault.git)```

```cd add-to-vault```

2. Start the server with Docker Compose:

```docker-compose up -d --build```

*This will build the Python image, install dependencies, and start the Uvicorn server on ```port 8000```.*

#### Configuration & First Run

Open your web browser and navigate to ```http://<your-server-ip>:8000```.

Use the **Web UI** to register a new admin account.

Log in with your new credentials.

Navigate to the **Profile** tab to find your securely generated Bearer Token.

Install the [Add To Vault Obsidian Plugin](https://github.com/epicylon/add-to-vault-plugin) and paste this token, your server IP, and your Gemini API key into the plugin settings.

### Architecture & Volumes

The ```docker-compose.yml``` file utilizes persistent volumes so you never lose your data when updating or restarting the container:

```./backend/data:/app/data``` - Stores the ```add_to_vault.db``` SQLite database *(users, passwords, admin states)*.

```./vault:/app/vault``` - The temporary "Inbox" where generated Markdown files wait to be fetched by your Obsidian plugin.

### Try the Interactive Demo

Curious how the LLM processing looks in practice without setting up a server?
Check out the [100% Static Interactive Demo](https://epicylon.github.io/add-to-vault).

*(Note: The demo is a frontend illusion using pre-generated data to showcase the Archivist, Analyst, and Synthesist modes without consuming live API tokens).*

### Architecture

The project consists of a **FastAPI** backend utilizing **SQLAlchemy** *(SQLite)* for user management, and **Passlib (Bcrypt)** & **python-jose** *(JWT)* for authentication. Web scraping is handled via **BeautifulSoup4**, **Requests** & **XML ElementTree** *(for RSS)*. LLM interactions are orchestrated through **LangChain**. The frontend is a single-page HTML application styled with **Tailwind CSS**, served directly by FastAPI.

<div align="center">
  <a href="https://www.buymeacoffee.com/clinch">
    <img src="https://github.com/epicylon/add-to-vault/blob/demo/scr/blue-button.png?raw=true" alt="Buy Me A Coffee" width="200" />
  </a>
</div>
