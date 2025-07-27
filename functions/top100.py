import sqlite3
import requests

# DB 초기화
def init_db(handle, date):
    conn = sqlite3.connect(f"top100_{handle}_{date}.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS top100_problems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        handle TEXT NOT NULL,
        problem_id INTEGER NOT NULL,
        fetched_date TEXT NOT NULL,
        tier INTEGER
    )
    """)
    conn.commit()
    conn.close()
    print("DB 초기화 완료")

# 오늘을 기준으로 Top 100의 전체 문제 가져오기
def get_today_problems(handle):
    url = f"https://solved.ac/api/v3/user/top_100?handle={handle}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        problem_ids = [item["problemId"] for item in data["items"]]
        print("Top 100 문제:")
        print(problem_ids)
    else:
        print(f"[ERROR] {handle}의 Top 100 가져오기 실패")
    return problem_ids

# 문제별 티어 점수 가져오기
def get_problem_tier(problem_id):
    url = f"https://solved.ac/api/v3/problem/show?problemId={problem_id}"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json().get("level", 0)
    return 0

# DB에 저장
def save_top100(handle, date):
    init_db(date)
    problem_ids = get_today_problems(handle)

    conn = sqlite3.connect(f"top100_{handle}_{date}.db")
    cursor = conn.cursor()

    for pid in problem_ids:
        tier = get_problem_tier(pid)
        cursor.execute("""
            INSERT INTO top100_problems (handle, problem_id, fetched_date, tier)
            VALUES (?, ?, ?, ?)
        """, (handle, pid, date, tier))
    conn.commit()
    conn.close()
    print(f"[OK] {handle}의 Top 100 저장 완료")

# DB에 저장된 Top 100 읽어오는 함수
def load_top100_set(handle, date):
    db_path = f"top100_{handle}_{date}.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT problem_id FROM top100_problems")
    problems = [row[0] for row in cursor.fetchall()]
    conn.close()
    return set(problems)

# DB에 저장된 Top 100에서 특정 문제 tier만 읽어오기
def get_tier_from_db(db_path, problem_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT tier FROM top100_problems WHERE problem_id = ?", (problem_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None