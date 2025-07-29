from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta  

import os
import sqlite3
from pydantic import BaseModel
from fastapi import status

from functions.solved_count import get_today_solved_diff
from functions.top100_db import load_top100_problem, save_top100, get_today_new_problem_score
from functions.user_handle import register_new_user, get_user_list, ensure_directories, check_today_status

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
    return FileResponse("templates/index.html")

class UserRegisterRequest(BaseModel):
    handle: str

# 새로운 유저 추가
@app.post("/api/user/register")
def register_user(req: UserRegisterRequest):
    try:
        result_msg = register_new_user(req.handle)

        if "이미 등록된 유저" in result_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result_msg
            )
        return {"message": result_msg}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 내부 오류: {str(e)}"
        )
    
@app.post("/api/save-yesterday")
def save_yesterday_data():
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    for handle in get_user_list():
        try:
            save_top100(handle, yesterday)
            count = get_solved_count(handle)
            append_today_count(handle, yesterday, count)
        except:
            pass

    return {"message": "OK"}


# 오늘의 스트릭
@app.get("/api/solved-diff/all")
def solved_diff_all():
    today = datetime.now().strftime("%Y-%m-%d")
    ensure_directories()

    results = []

    for handle in get_user_list():
        # 오늘의 로그/DB가 존재하는지 확인
        status = check_today_status(handle)
        if not status["db_exists"]:
            print(f"[INFO] Creating  {handle}'s Today DB...")
            save_top100(handle, today)
        if not status["log_has_today"]:
            print(f"[INFO] Appending {handle}'s Today LOG...")

        diff, today_count = get_today_solved_diff(handle, today)

        results.append({
            "handle": handle,
            "today_count": today_count,
            "diff_from_yesterday": diff
        })
    return results


# 특정 문제 Top100 포함 여부
@app.get("/api/top100/check")
def check_problem_in_top100(problem_id: int):
    today = datetime.now().strftime("%Y-%m-%d")
    found_handles = []

    for handle in get_user_list():
        # 오늘자 top100 DB에서 문제 번호들 불러오기
        problem_ids = load_top100_problem(handle, today)

        if problem_id in problem_ids:
            found_handles.append({"handle": handle})

    return found_handles


# 오늘의 랭킹
@app.get("/api/ranking/today")
def today_tier_ranking():
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    valid_users = set(get_user_list())
    rankings = []

    for handle in valid_users:
        try:
            save_top100(handle, today)
        except Exception as e:
            print(f"{handle} 데이터 저장 실패:", e)
            continue

        score = get_today_new_problem_score(handle, today, yesterday)
        rankings.append({"handle": handle, "tier_score": score})

    rankings.sort(key=lambda x: x["tier_score"], reverse=True)
    return rankings


# uvicorn main:app --reload
# http://127.0.0.1:8000