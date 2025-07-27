from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from functions.solved_count import get_today_solved_diff
from functions.top100 import load_top100_set, get_tier_from_db
from datetime import datetime
import os
import sqlite3

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML 서빙
@app.get("/")
def serve_index():
    return FileResponse("templates/luxtrail_index.html")

# 오늘 푼 문제 수 API
@app.get("/api/solved-diff/{handle}")
def solved_diff(handle: str):
    today = datetime.now().strftime("%Y-%m-%d")
    diff, today_count = get_today_solved_diff(handle, today)
    return {"today_count": today_count, "diff_from_yesterday": diff}

# 특정 문제 Top100 포함 여부
@app.get("/api/top100/check")
def check_problem_in_top100(problem_id: int):
    today = datetime.now().strftime("%Y-%m-%d")
    found_handles = []

    for filename in os.listdir():
        if filename.startswith("top100_") and filename.endswith(f"{today}.db"):
            parts = filename.split("_")
            if len(parts) >= 2:
                handle = parts[1]
                problem_set = load_top100_set(handle, today)
                if problem_id in problem_set:
                    found_handles.append({"handle": handle})

    return found_handles

# 오늘의 랭킹
@app.get("/api/ranking/today")
def today_tier_ranking():
    today = datetime.now().strftime("%Y-%m-%d")
    rankings = []

    for filename in os.listdir():
        if filename.startswith("top100_") and filename.endswith(f"{today}.db"):
            handle = filename.split("_")[1]
            db_path = filename
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT problem_id FROM top100_problems")
            problems = [row[0] for row in cursor.fetchall()]
            conn.close()

            total_score = 0
            for pid in problems:
                tier = get_tier_from_db(db_path, pid)
                total_score += tier if tier else 0

            rankings.append({"handle": handle, "tier_score": total_score})

    rankings.sort(key=lambda x: x["tier_score"], reverse=True)
    return rankings