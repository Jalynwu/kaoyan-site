from datetime import datetime, timezone
from fastapi import FastAPI

app = FastAPI()


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
