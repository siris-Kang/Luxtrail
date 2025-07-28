const BACKEND_URL = "http://127.0.0.1:8000";

async function pushNewUser() {
    const handle = document.querySelector(".handleInput").value.trim();
    if (!handle) {
        alert("백준 ID를 입력해주세요.");
        return;
    }

    try {
    const res = await axios.post(`${BACKEND_URL}/api/user/register`, 
        { handle: handle },
        { headers: { "Content-Type": "application/json" } }
    );
    } catch (err) {
    alert("[Error]: " + (err.response?.data?.detail || err.message));
    }
}


async function getStreak() {
    const res = await axios.get(`/api/solved-diff/all`);
    const data = res.data;

    const resultDiv = document.querySelector('.streakResult');
    resultDiv.innerHTML = "";

    data.forEach(entry => {
        const p = document.createElement("p");
        p.innerText = `${entry.handle}: 오늘 ${entry.diff_from_yesterday}문제를 풀었습니다!`;
        resultDiv.appendChild(p);
    });
}


async function checkProblemInTop100() {
    const problemId = document.querySelector('.problemIdInput').value;
    const res = await axios.get(`/api/top100/check?problem_id=${problemId}`);
    const data = res.data;
    const resultDiv = document.querySelector('.top100Result');

    if (data.length === 0) {
    resultDiv.innerText = '아무도 이 문제를 Top100에서 풀지 않았습니다';
    return;
    }

    resultDiv.innerHTML = '<b>Top100 문제로 푼 사람:</b><ul>' + 
    data.map(user => `<li>${user.handle}</li>`).join('') + '</ul>';
}


async function loadRanking() {
    const res = await axios.get(`${BACKEND_URL}/api/ranking/today`);
    const data = res.data;

    const ul = document.querySelector('.rankingList');
    if (!ul) {
        console.error("❌ .rankingList 요소 없음!");
        return;
    }

    ul.innerHTML = '';
    console.log(data);
    data.forEach((entry, idx) => {
        const li = document.createElement('li');
        li.innerText = `#${idx + 1} ${entry.handle} - ${entry.tier_score} 티어점수`;
        ul.appendChild(li);
    });
}
