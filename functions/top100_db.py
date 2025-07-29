import os
import sqlite3
import requests


# 오늘을 기준으로 Top 100의 전체 문제 가져오기
def get_today_problems(handle):
    url = f"https://solved.ac/api/v3/user/top_100?handle={handle}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        problem_ids = [item["problemId"] for item in data["items"]]
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


# DB 초기화
def init_db(handle, date):
    base_path = os.path.dirname(__file__)
    db_path = os.path.join(base_path, '..', 'DBs', f'top100_{handle}_{date}.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS top100_problems")

    cursor.execute("""
        CREATE TABLE top100_problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            handle TEXT NOT NULL,
            problem_id INTEGER NOT NULL,
            fetched_date TEXT NOT NULL,
            UNIQUE(handle, problem_id)
        )
    """)

    cursor.execute("DELETE FROM sqlite_sequence WHERE name='top100_problems'")

    conn.commit()
    conn.close()


# DB에 저장
def save_top100(handle, date):
    init_db(handle, date)
    problem_ids = get_today_problems(handle)

    base_path = os.path.dirname(__file__)
    db_path = os.path.join(base_path, '..', 'DBs', f'top100_{handle}_{date}.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    values = [(handle, pid, date) for pid in problem_ids]
    cursor.executemany("""
        INSERT OR IGNORE INTO top100_problems (handle, problem_id, fetched_date)
        VALUES (?, ?, ?)
    """, values)  # 중복되면 INSERT 안함

    conn.commit()
    conn.close()
    print(f"[OK] {handle}의 Top 100 저장 완료")



# DB에 저장된 Top 100의 문제 번호 읽어오기
def load_top100_problem(handle, date):
    base_path = os.path.dirname(__file__)
    db_path = os.path.join(base_path, '..', 'DBs', f'top100_{handle}_{date}.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT problem_id FROM top100_problems")
    problems = [row[0] for row in cursor.fetchall()]
    conn.close()
    return set(problems)


# 오늘 새로 추가된 문제들의 티어 합 반환하기
def get_today_new_problem_score(handle, today_str, yesterday_str):
    today_ids = load_top100_problem(handle, today_str)
    yesterday_ids = load_top100_problem(handle, yesterday_str)

    if not yesterday_ids:
        return 0

    new_problem_ids = today_ids - yesterday_ids

    total_score = 0
    for pid in new_problem_ids:
        tier = get_problem_tier(pid) 
        total_score += tier if tier else 0

    return total_score
