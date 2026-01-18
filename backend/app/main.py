from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import engine
from .models import Base
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import User
from .auth_utils import hash_password
from .auth_utils import verify_password
from .jwt_utils import create_access_token
from .models import Message
from .deps import get_current_user, get_db
from .ai import chat_with_ai
from .ai import chat_with_ai_history
from fastapi.middleware.cors import CORSMiddleware




app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jalynwu.github.io",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段先全放开，后面上线再收紧
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
def ping():
    return {"msg": "server is alive"}

@app.get("/whoami")
def whoami():
    return {"file": __file__}

@app.get("/countdown")
def countdown():
    target = datetime(2026, 12, 19, 0, 0, 0, tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)

    delta = target - now
    total_seconds = int(delta.total_seconds())

    # 如果已经过期
    if total_seconds <= 0:
        return {
            "expired": True,
            "days": 0,
            "hours": 0,
            "minutes": 0,
            "seconds": 0
        }

    # 拆分时间
    days = total_seconds // 86400
    remaining = total_seconds % 86400

    hours = remaining // 3600
    remaining = remaining % 3600

    minutes = remaining // 60
    seconds = remaining % 60

    return {
        "expired": False,
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds
    }
@app.post("/auth/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    # 1) 用户名是否已存在
    exists = db.query(User).filter(User.username == username).first()
    if exists:
        raise HTTPException(status_code=400, detail="username already exists")

    # 2) 写入数据库（存 hash，不存明文）
    user = User(username=username, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"id": user.id, "username": user.username}
@app.post("/auth/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=400, detail="invalid username or password")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="invalid username or password")

    token = create_access_token({"sub": str(user.id), "username": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/messages")
def post_message(
    content: str,
    user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    msg = Message(user_id=user.id, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {"id": msg.id, "user_id": msg.user_id, "content": msg.content, "created_at": str(msg.created_at)}
@app.get("/messages")
def list_messages(db: Session = Depends(get_db)):
    # 联表：messages + users
    rows = (
        db.query(Message, User)
        .join(User, Message.user_id == User.id)
        .order_by(Message.id.desc())
        .limit(50)
        .all()
    )

    result = []
    for msg, user in rows:
        result.append({
            "id": msg.id,
            "username": user.username,
            "content": msg.content,
            "created_at": str(msg.created_at),
        })
    return {"items": result}

@app.post("/ai/chat")
def ai_chat(
    message: str,
    user = Depends(get_current_user),  # 必须登录才能用
):
    reply = chat_with_ai(message)
    return {"reply": reply}

@app.post("/ai/chat2")
def ai_chat2(
    history: str,  # 先用最简单方式：前端把 JSON 字符串传过来
    user = Depends(get_current_user),
):
    import json
    hist = json.loads(history)
    reply = chat_with_ai_history(hist)
    return {"reply": reply}

