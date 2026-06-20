# add-to-vault
A lightweight and modular service for adding articles, comments & finds to your Obsidian vault.

**Transparency Notice:** *This project is "vibe-coded".* The architecture, backend logic, and frontend codebase were *primarily* written and iterated by Google's Gemini Pro large language model under the direction of a human project manager. The focus is on **function**, **modularity**, and **privacy**.

Overview

Add To Vault is a self-hosted backend and web interface designed to bridge the gap between your web browser and your Obsidian vault. Instead of manually copying text or relying on heavy third-party sync services, you paste a URL into the web dashboard. The server scrapes the content, uses an LLM (Google Gemini) to summarize and format it into Markdown, and holds it in a secure inbox until your Obsidian client pulls it down.

Crucially, it is context-aware. The companion Obsidian plugin sends a list of your existing vault note titles to the server, allowing the LLM to automatically generate internal [[links]] to concepts you already have notes on.

### Features

- **Smart Web Scraping:** Automatically extracts clean, readable text from articles while stripping out ads and navigation.

- **LLM Summarization:** Leverages Google Gemini (flash models recommended) to summarize content, extract key points, and generate tags.

- **Context-Aware Linking:** Knows your existing vault structure (file names only) and weaves relevant internal links into the generated summaries.

- **Customizable Templates:** Write your own prompt template directly inside Obsidian. The server follows your local Markdown structure.

- **Privacy-Focused Sync:** No need to expose your entire vault to Syncthing or cloud providers. The server only sees your file names, and generated files are deleted from the server the moment your local Obsidian client downloads them.

- **Admin Dashboard:** Includes a minimalist web UI with user authentication and the ability to close public registrations.

### Prerequisites

- Docker and Docker Compose installed on your host machine/server.

- A Google Gemini API key (Free tier from Google AI Studio works perfectly).

### Installation

1. Clone this repository to your server:
```
git clone [https://github.com/yourusername/add-to-vault-server.git](https://github.com/yourusername/add-to-vault-server.git)
cd add-to-vault-server
```

2. Start the Docker container:
```
docker-compose up -d --build
```

3. Access the web interface by navigating to ```http://<your-server-ip>:8000``` in your browser.

### Initial Setup

1. **Create the Admin Account:** The very first user to register an account on the web interface is automatically granted Administrator privileges.

2. **Lock Registrations:** Once logged in, go to the "Admin" tab and toggle Open Registration to "CLOSED" to prevent unauthorized users from using your server.

3. **Generate a Token:** You will use the login credentials (specifically the Bearer token managed under the hood) to connect your Obsidian vault.

   (need more on how to obtain bearer token)

### Obsidian Plugin

To complete the setup, you must install the companion Obsidian plugin. This plugin handles the secure push/pull mechanism between your local vault and the server.

[Link to Add To Vault Obsidian Plugin repository] (Update this link when the plugin repository is public)

#### Plugin Configuration

Once the plugin is installed in Obsidian, go to its settings:

1. Enter your Server API URL (e.g., ```http://<your-server-ip>:8000```).

2. Enter your Server API Token (copied from the web dashboard network requests, or managed via the plugin auth flow).

3. Input your Gemini API Key and validate it.

4. Select your preferred LLM model.

5. Point the plugin to a local .md file in your vault to act as the prompt template (Available variables: ```{title}```, ```{url}```, ```{content}```, ```{vault_context}```).

6. Click **"Sync"** to push your preferences and vault context to the server.

### Architecture

The project consists of a **FastAPI** backend utilizing **SQLAlchemy** *(SQLite)* for user management. Web scraping is handled via **BeautifulSoup4**. LLM interactions are orchestrated through **LangChain**. The frontend is a single-page HTML application styled with **Tailwind CSS**, served directly by FastAPI.
