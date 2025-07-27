async function checkStreak() {
    const handle = document.getElementById('handleInput').value;
    const res = await fetch(`/api/solved-diff/${handle}`);
    const data = await res.json();
    document.getElementById('streakResult').innerText = 
  `오늘 ${data.diff_from_yesterday}문제 풀었고, 총 ${data.today_count}문제를 풀었습니다.`;
}

async function checkProblemInTop100() {
    const problemId = document.getElementById('problemIdInput').value;
    const res = await fetch(`/api/top100/check?problem_id=${problemId}`);
    const data = await res.json();
    const resultDiv = document.getElementById('top100Result');

    if (data.length === 0) {
    resultDiv.innerText = '아무도 이 문제를 Top100에서 풀지 않았습니다';
    return;
    }

    resultDiv.innerHTML = '<b>Top100 문제로 푼 사람:</b><ul>' + 
    data.map(user => `<li>${user.handle}</li>`).join('') + '</ul>';
}

async function loadRanking() {
    const res = await fetch('/api/ranking/today');
    const data = await res.json();
    const ul = document.getElementById('rankingList');
    ul.innerHTML = '';
    data.forEach((entry, idx) => {
    const li = document.createElement('li');
    li.innerText = `#${idx + 1} ${entry.handle} - ${entry.tier_score} 티어점수`;
    ul.appendChild(li);
    });
}