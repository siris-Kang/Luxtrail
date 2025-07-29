import os
from datetime import date, datetime
from .top100_db import save_top100

USER_LIST_PATH = "user_list.txt"
LOG_DIR = "logs"
DB_DIR = "DBs"


def ensure_directories():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    else:
        print(f"[SKIP] 로그 디렉토리 이미 존재: {LOG_DIR}")

    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    else:
        print(f"[SKIP] DB 디렉토리 이미 존재: {DB_DIR}")



def is_new_user(handle):
    if not os.path.exists(USER_LIST_PATH):
        return True
    with open(USER_LIST_PATH, "r") as f:
        return handle not in [line.strip() for line in f.readlines()]


def register_new_user(handle: str) -> str:
    user_list_path = "user_list.txt"
    dbs_dir = "DBs"
    logs_dir = "logs"
    today_str = date.today().strftime("%Y-%m-%d")

    os.makedirs(dbs_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    # 유저 리스트 불러오기
    if os.path.exists(user_list_path):
        with open(user_list_path, 'r', encoding='utf-8') as f:
            existing_users = [line.strip() for line in f.readlines()]
    else:
        existing_users = []

    if handle in existing_users:
        return "이미 등록된 유저입니다."

    # 유저리스트에 추가
    with open(user_list_path, 'a', encoding='utf-8') as f:
        f.write(handle + "\n")

    # 로그파일 생성
    log_path = f"{logs_dir}/solved_count_log_{handle}.txt"
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"{today_str}: 0\n")

    # Top100 DB 생성
    save_top100(handle, today_str)

    return f"{handle} 계정이 등록되었습니다."



def get_user_list():
    if not os.path.exists(USER_LIST_PATH):
        return []
    with open(USER_LIST_PATH, "r") as f:
        return [line.strip() for line in f.readlines()]

# 로그 파일 안에 오늘 날짜가 존재하는지 확인
def check_today_status(handle: str) -> dict:
    today = date.today().strftime("%Y-%m-%d")
    db_path = os.path.join(DB_DIR, f"top100_{handle}_{today}.db")
    log_path = os.path.join(LOG_DIR, f"solved_count_log_{handle}.txt")

    db_exists = os.path.exists(db_path)

    log_has_today = False
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(f"{today}:"):
                    log_has_today = True
                    break

    return {
        "db_exists": db_exists,
        "log_has_today": log_has_today
    }
