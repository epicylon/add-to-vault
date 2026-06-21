# Add To Vault
A lightweight and modular service for adding articles, comments & finds to your Obsidian vault.

**Transparency Notice:** *This project is "vibe-coded".* The architecture, backend logic, and frontend codebase were *primarily* written and iterated by Google's Gemini Pro large language model under the direction of a human project manager. The focus is on **function**, **modularity**, and **privacy**.

![alt text](https://raw.githubusercontent.com/epicylon/add-to-vault/refs/heads/demo/scr/atv-screenshot-1.png "Add To Vault Overview")

### Overview
**Add To Vault** is a two-part system designed to capture, summarize, and link web content securely. While the backend server handles the heavy lifting (web scraping and LLM processing), this plugin sits quietly in your Obsidian vault and acts as the secure courier.

It performs two main tasks:

1. **Pushing Context:** It reads the filenames in your vault and securely pushes this index to your server. This allows the server's LLM to generate intelligent [[internal links]] to concepts you already know.

2. **Pulling Notes:** It periodically polls your server's secure inbox for newly generated markdown files, downloads them directly into your vault, and deletes them from the server.

<div align="center">
  <h3><a href="https://epicylon.github.io/add-to-vault/">Try out a demo simulation here</a></h3>
</div>

### Prerequisites
- An active, self-hosted instance of the Add To Vault Server. (Update link when ready)

- A generated Bearer Token (found in your server's web dashboard under the "Profile" tab).

- A Google Gemini API Key.

### Manual Installation

Until this plugin is available in the official Obsidian Community Plugins directory, you can install it manually:

1. Download the latest ```main.js``` and ```manifest.json``` files from the Releases tab *(or build them from source)*.

2. Open your Obsidian vault folder.

3. Navigate to ```.obsidian/plugins/```.

4. Create a new folder named ```add-to-vault```.

5. Place ```main.js``` and ```manifest.json``` inside this new folder.

6. Restart Obsidian, go to Settings -> Community Plugins, disable Safe Mode, and enable "Add To Vault".

### Configuration & Authentication
Navigate to the Add To Vault settings tab inside Obsidian to configure the connection:

1. **Create an Account:** Visit your self-hosted server's web dashboard and register for an account.

2. **Get Your Token:** Once logged in, navigate to the Profile tab in the dashboard and click "Show / Hide Token". Copy this Bearer Token.

3. **Obsidian Setup:** Paste the token into the "Server API Token" field in the plugin settings. Set your API URL (e.g., http://192.168.1.100:8000).

#### Other Settings:

- **Gemini API Key:** Your Google AI Studio key. (Note: This is securely transmitted and stored on your own server).

- **LLM Model:** Select your preferred model (e.g., gemini-2.5-flash).

- **Inbox Folder:** The local folder where new notes should be saved.

- **LLM Prompt Templates:** Point to local .md files for Archivist, Analyst, and Synthesist modes. Variables supported: {title}, {url}, {content}, {vault_context}.

### Development

To build this plugin from source:

1. Clone this repository.

2. Run ```npm install``` to install dependencies.

3. Run ```npm run build``` to compile the TypeScript source code into the final ```main.js``` file.

### Architecture

The project consists of a **FastAPI** backend utilizing **SQLAlchemy** *(SQLite)* for user management. Web scraping is handled via **BeautifulSoup4**. LLM interactions are orchestrated through **LangChain**. The frontend is a single-page HTML application styled with **Tailwind CSS**, served directly by FastAPI.

<div align="center">
  <a href="https://www.buymeacoffee.com/clinch">
    <img src="https://github.com/epicylon/add-to-vault/blob/demo/scr/blue-button.png?raw=true" alt="Buy Me A Coffee" width="200" />
  </a>
</div>
