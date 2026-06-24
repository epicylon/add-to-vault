import os
import re
import json
import google.generativeai as genai
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.concurrency import run_in_threadpool
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import timedelta

from . import models, schemas, auth
from .database import engine, get_db
from .scraper import scrape_url
from .llm import process_text_with_llm, _validate_links

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Add To Vault API", version="0.3.0")

VAULT_DIR = "/app/vault"
DATA_DIR = "/app/data"
STATIC_DIR = "/app/app/static"

os.makedirs(VAULT_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# ── STATIC FILE SERVING ───────────────────────────────────────────────────
# Mount Vite production assets FIRST (hashed JS/CSS bundles)
assets_dir = os.path.join(STATIC_DIR, "assets")
if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# Keep /static mount for any manually placed files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", tags=["UI"])
async def serve_frontend():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(index_path):
        return {"message": "Frontend not found."}
    return FileResponse(index_path)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok"}

# --- ADMIN HELPER FUNCTION ---
def get_current_admin(current_user: models.User = Depends(auth.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Requires administrator privileges.")
    return current_user

# --- USER AND AUTHENTICATION ---
@app.post("/register", response_model=schemas.UserResponse, tags=["Auth"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user_count = db.query(models.User).count()
    is_first_user = user_count == 0

    if not is_first_user:
        setting = db.query(models.SystemSetting).filter_by(key="allow_signups").first()
        allow_signups = setting.value == "true" if setting else True
        if not allow_signups:
            raise HTTPException(status_code=403, detail="Registration is currently closed by the administrator.")

    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username is already in use")

    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        sync_strategy=user.sync_strategy,
        is_admin=is_first_user
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=schemas.Token, tags=["Auth"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials", headers={"WWW-Authenticate": "Bearer"})

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse, tags=["Users"])
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.post("/users/me/password", tags=["Users"])
def change_password(passwords: schemas.PasswordChange, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if not auth.verify_password(passwords.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password.")
    current_user.hashed_password = auth.get_password_hash(passwords.new_password)
    db.commit()
    return {"status": "ok", "message": "Password successfully changed."}

# --- ADMINISTRATOR ENDPOINTS ---
@app.get("/admin/settings", tags=["Admin"])
def get_admin_settings(db: Session = Depends(get_db)):
    setting = db.query(models.SystemSetting).filter_by(key="allow_signups").first()
    allow = setting.value == "true" if setting else True
    return {"allow_signups": allow}

@app.post("/admin/toggle-signups", tags=["Admin"])
def toggle_signups(current_admin: models.User = Depends(get_current_admin), db: Session = Depends(get_db)):
    setting = db.query(models.SystemSetting).filter_by(key="allow_signups").first()
    if not setting:
        setting = models.SystemSetting(key="allow_signups", value="false")
        db.add(setting)
    else:
        setting.value = "false" if setting.value == "true" else "true"
    db.commit()
    return {"status": "ok", "allow_signups": setting.value == "true"}

@app.get("/admin/users", tags=["Admin"])
def list_users(current_admin: models.User = Depends(get_current_admin), db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return [{"id": u.id, "username": u.username, "is_admin": u.is_admin, "is_active": u.is_active} for u in users]

# --- PLUGIN: CONTEXT AND SETTINGS ---
@app.post("/validate-provider", tags=["Plugin Sync"])
async def validate_provider(request: schemas.ValidateProviderRequest):
    try:
        provider = request.provider
        api_key = request.api_key

        if provider == "gemini":
            genai.configure(api_key=api_key)
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            return {"supported_models": available_models}
        elif provider == "openai":
            return {"supported_models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]}
        elif provider == "anthropic":
            return {"supported_models": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"]}
        elif provider == "mistral":
            return {"supported_models": ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest"]}
        elif provider == "kimi":
            return {"supported_models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]}
        elif provider == "ollama":
            return {"supported_models": ["llama3", "mistral", "gemma2", "phi3"]}
        else:
            return {"supported_models": []}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/update-index", tags=["Plugin Sync"])
async def update_vault_index(request: schemas.IndexRequest, current_user: models.User = Depends(auth.get_current_user)):
    index_file = os.path.join(DATA_DIR, f"vault_index_{current_user.username}.json")
    # Convert Pydantic objects to dicts
    notes_data = [note.dict() for note in request.notes]
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(notes_data, f, ensure_ascii=False)
    return {"status": "ok"}

@app.post("/update-prefs", tags=["Settings"])
async def update_prefs(request: schemas.UserPrefsRequest, current_user: models.User = Depends(auth.get_current_user)):
    prefs_file = os.path.join(DATA_DIR, f"prefs_{current_user.username}.json")
    prefs_data = {
        "api_key": request.api_key,
        "provider": request.provider,
        "model": request.model,
        "prompt_template": request.prompt_template,
        "template_archivist": request.template_archivist,
        "template_analyst": request.template_analyst,
        "template_synthesist": request.template_synthesist,
        "use_multipass": request.use_multipass
    }
    with open(prefs_file, "w", encoding="utf-8") as f:
        json.dump(prefs_data, f, ensure_ascii=False)
    return {"status": "success", "message": "Preferences updated"}

# --- CORE FUNCTIONALITY (INBOX) ---
@app.post("/process-link", response_model=schemas.ProcessResponse, tags=["Inbox"])
async def process_link(request: schemas.LinkRequest, current_user: models.User = Depends(auth.get_current_user)):
    try:
        prefs_file = os.path.join(DATA_DIR, f"prefs_{current_user.username}.json")
        if not os.path.exists(prefs_file):
            raise HTTPException(status_code=400, detail="Preferences not configured. Please sync from Obsidian first.")

        with open(prefs_file, "r", encoding="utf-8") as f:
            prefs = json.load(f)

        # Hent hvelvkontekst (filnavn og tags)
        vault_context_list = []
        index_file = os.path.join(DATA_DIR, f"vault_index_{current_user.username}.json")
        if os.path.exists(index_file):
            with open(index_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                # Fallback to handle old string-based indexes smoothly
                for item in raw_data:
                    if isinstance(item, str):
                        vault_context_list.append({"path": item, "tags": []})
                    else:
                        vault_context_list.append(item)

        # Skrap innholdet fra URL
        title, content = await run_in_threadpool(scrape_url, request.url)
        if not content:
            raise HTTPException(status_code=400, detail="Could not find content at the provided link.")

        mode = request.mode or "analyst"
        template_key = f"template_{mode}"
        prompt_template = prefs.get(template_key, prefs.get("prompt_template"))

        if not prompt_template:
            raise HTTPException(status_code=400, detail=f"Missing template for mode: {mode}. Please configure it in Obsidian and sync.")

        # Generer notat ved hjelp av det oppdaterte LLM-maskineriet
        markdown_result = await process_text_with_llm(
            url=request.url,
            title=title,
            content=content,
            api_key=prefs.get("api_key"),
            provider=prefs.get("provider", "gemini"),  # Fallback til gemini hvis feltet mangler
            model_name=prefs.get("model", "gemini-2.5-flash"),
            prompt_template=prompt_template,
            vault_context_data=vault_context_list,
            use_multipass=prefs.get("use_multipass", False)
        )

        # Strip hallucinated [[links]] against the synced vault index
        markdown_result = _validate_links(markdown_result, vault_context_list)

        title_with_dash = title.replace("|", "-")
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title_with_dash)
        filename = f"{safe_title}.md"

        filepath = os.path.join(VAULT_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_result)

        return schemas.ProcessResponse(title=title, markdown=markdown_result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")

# --- INBOX (PULL) ---
@app.get("/inbox", tags=["Plugin Sync"])
async def get_inbox_items(current_user: models.User = Depends(auth.get_current_user)):
    items = []
    if os.path.exists(VAULT_DIR):
        for filename in os.listdir(VAULT_DIR):
            if filename.endswith(".md"):
                filepath = os.path.join(VAULT_DIR, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                items.append({"filename": filename, "content": content})
    return {"items": items}

@app.delete("/inbox/{filename}", tags=["Plugin Sync"])
async def delete_inbox_item(filename: str, current_user: models.User = Depends(auth.get_current_user)):
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(VAULT_DIR, safe_filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return {"status": "ok"}
    raise HTTPException(status_code=404, detail="File not found.")
