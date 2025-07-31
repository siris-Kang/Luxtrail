import requests
from datetime import datetime


# 지금까지 푼 문제 수 가져오기
def get_solved_count(handle):
    url = f"https://solved.ac/api/v3/user/show?handle={handle}"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json().get("solvedCount", 0)
    return 0


# 어제 날짜 기준으로 마지막 푼 문제 수를 return
def read_yesterday_count(handle, today):
    file_path = f"logs/solved_count_log_{handle}.txt"
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
            yesterday_count = None

            for line in lines:
                date_str, count_str = line.strip().split(": ")
                if date_str < today:
                    yesterday_count = int(count_str)

            return yesterday_count
    except FileNotFoundError:
        return None


# 오늘 기준으로 푼 문제 수 업데이트
def append_today_count(handle, date, count):
    file_path = f"logs/solved_count_log_{handle}.txt"
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()

        if lines and lines[-1].startswith(f"{date}:"):
            lines[-1] = f"{date}: {count}\n"
        else:
            lines.append(f"{date}: {count}\n")
            
        with open(file_path, "w") as f:
            f.writelines(lines)

    except FileNotFoundError:
        with open(file_path, "w") as f:
            f.write(f"{date}: {count}\n")


def append_yesterday_count(handle, target_date_str, count):
    file_path = f"logs/solved_count_log_{handle}.txt"
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()

        found = False
        for i, line in enumerate(lines):
            if line.startswith(f"{target_date_str}:"):
                lines[i] = f"{target_date_str}: {count}\n"
                found = True
                break

        if not found:
            # 해당 날짜가 없으면 맨 끝에 추가
            lines.append(f"{target_date_str}: {count}\n")

        with open(file_path, "w") as f:
            f.writelines(lines)

    except FileNotFoundError:
        with open(file_path, "w") as f:
            f.write(f"{target_date_str}: {count}\n")



# 어제와 오늘 푼 문제 수 차이를 return
def get_today_solved_diff(handle, today):
    today_count = get_solved_count(handle)
    prev_count = read_yesterday_count(handle, today)
    append_today_count(handle, today, today_count)
    
    if prev_count is not None:
        return today_count - prev_count, today_count
    return 0, today_count