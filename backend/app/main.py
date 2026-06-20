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
from .llm import process_text_with_llm

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Add To Vault API", version="0.3.0")

VAULT_DIR = "/app/vault"
DATA_DIR = "/app/data"
STATIC_DIR = "/app/app/static"

os.makedirs(VAULT_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

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
    # Check if this is the very first user in the system
    user_count = db.query(models.User).count()
    is_first_user = user_count == 0

    # If not the first user, check if registrations are open
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
        is_admin=is_first_user # The first person to register becomes an admin
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
@app.post("/validate-gemini", tags=["Plugin Sync"])
async def validate_gemini(request: schemas.ValidateGeminiRequest):
    try:
        genai.configure(api_key=request.api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return {"supported_models": available_models}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/update-index", tags=["Plugin Sync"])
async def update_vault_index(request: schemas.IndexRequest, current_user: models.User = Depends(auth.get_current_user)):
    index_file = os.path.join(DATA_DIR, f"vault_index_{current_user.username}.json")
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(request.notes, f, ensure_ascii=False)
    return {"status": "ok"}

@app.post("/update-prefs", tags=["Plugin Sync"])
async def update_user_prefs(request: schemas.UserPrefsRequest, current_user: models.User = Depends(auth.get_current_user)):
    prefs_file = os.path.join(DATA_DIR, f"prefs_{current_user.username}.json")
    with open(prefs_file, "w", encoding="utf-8") as f:
        json.dump(request.dict(), f, ensure_ascii=False)
    return {"status": "ok"}

# --- CORE FUNCTIONALITY (INBOX) ---
@app.post("/process-link", response_model=schemas.ProcessResponse, tags=["Inbox"])
async def process_link(request: schemas.LinkRequest, current_user: models.User = Depends(auth.get_current_user)):
    try:
        prefs_file = os.path.join(DATA_DIR, f"prefs_{current_user.username}.json")
        if not os.path.exists(prefs_file):
            raise HTTPException(status_code=400, detail="Missing settings. Please sync from the Obsidian plugin first!")

        with open(prefs_file, "r", encoding="utf-8") as f:
            prefs = json.load(f)

        vault_context_list = []
        index_file = os.path.join(DATA_DIR, f"vault_index_{current_user.username}.json")
        if os.path.exists(index_file):
            with open(index_file, "r", encoding="utf-8") as f:
                vault_context_list = json.load(f)
        context_string = ", ".join(vault_context_list) if vault_context_list else "No notes found."

        title, content = await run_in_threadpool(scrape_url, request.url)
        if not content:
            raise HTTPException(status_code=400, detail="Could not find content at the provided link.")

        markdown_result = await process_text_with_llm(
            url=request.url,
            title=title,
            content=content,
            api_key=prefs.get("api_key"),
            model_name=prefs.get("model", "gemini-2.5-flash"),
            prompt_template=prefs.get("prompt_template"),
            vault_context=context_string
        )

        title_with_dash = title.replace("|", "-")
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title_with_dash)
        filename = f"{safe_title}.md"
        
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
