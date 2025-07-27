from functions.solved_count import get_today_solved_diff
from functions.top100 import load_top100_set, get_tier_from_db
from datetime import datetime
import os
import sqlite3

def clean_handle(raw_input):
    return raw_input.replace("solved_count_log_", "").replace(".txt", "").strip()

def print_newly_solved_top100(handle, today):
    db_path = f"top100_{handle}_{today}.db"
    if not os.path.exists(db_path):
        print(f"[⚠️] 오늘자 Top100 DB가 존재하지 않습니다: {db_path}")
        return

    solved_log_path = f"solved_count_log_{handle}.txt"
    if not os.path.exists(solved_log_path):
        print(f"[⚠️] 로그 파일이 없습니다: {solved_log_path}")
        return

    # 오늘 푼 문제 목록이 로그에 없으므로, top100 DB 전체에서 오늘 푼 것으로 추정되는 문제를 비교
    top100_set = load_top100_set(handle, today)

    # 이전 날짜 top100 로드 (어제 날짜 기준)
    from datetime import timedelta
    yest = (datetime.strptime(today, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    prev_db_path = f"top100_{handle}_{yest}.db"
    prev_set = set()
    if os.path.exists(prev_db_path):
        prev_set = load_top100_set(handle, yest)

    newly_solved = top100_set - prev_set
    if not newly_solved:
        print("오늘 새롭게 푼 Top100 문제는 없습니다.")
        return

    print("오늘 새롭게 푼 Top100 문제 목록:")
    for pid in sorted(newly_solved):
        tier = get_tier_from_db(db_path, pid)
        print(f" - 문제 번호 {pid}, 티어: {tier}")

def main():
    print("=== 백준 스트릭 기록기 + Top100 비교 ===")
    raw = input("백준 ID를 입력하세요: ")
    handle = clean_handle(raw)
    today = datetime.now().strftime("%Y-%m-%d")
    
    log_path = f"solved_count_log_{handle}.txt"
    
    if not os.path.exists(log_path):
        print(f"로그 파일이 존재하지 않아 새로 만듭니다: {log_path}")
    
    try:
        diff, today_count = get_today_solved_diff(handle, today)
        print(f"\n[{handle}] 오늘 푼 문제 수: {today_count}개")
        if diff > 0:
            print(f"{diff}문제 풀었다!")
        else:
            print("얼른 문제 푸세요!")

        print_newly_solved_top100(handle, today)

    except Exception as e:
        print(f"[ERROR] 처리 중 문제가 발생했습니다: {e}")

if __name__ == "__main__":
    main()