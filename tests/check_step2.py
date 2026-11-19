"""2단계(R6, R7 일부) 확인용 스크립트. 프로젝트 폴더에서 `python tests/check_step2.py` 로 실행."""
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from src.compare import EPSILON, is_tie, judge, judge_ab
from src.labels import CROSS, X, UNDECIDED
from src.mac import mac_score


def check(name, condition):
    print(("[통과] " if condition else "[실패] ") + name)
    if not condition:
        sys.exit(1)


print("=== 컴퓨터는 0.1 + 0.2 를 정확히 0.3 으로 저장하지 못한다 ===")
print("0.1 + 0.2 =", repr(0.1 + 0.2), "/ 0.1 + 0.2 == 0.3 ->", 0.1 + 0.2 == 0.3)
check("그래서 '==' 비교는 믿을 수 없다", (0.1 + 0.2 == 0.3) is False)
check("epsilon 비교로는 같다고 판단", is_tie(0.1 + 0.2, 0.3))

print("\n=== is_tie ===")
check("문서 예시: 0.9 vs 0.8999999999999999 는 동점", is_tie(0.9, 0.8999999999999999))
check("차이 1e-10 (epsilon 보다 작음) -> 동점", is_tie(1.0, 1.0 + 1e-10))
check("차이 1e-8 (epsilon 보다 큼) -> 동점 아님", not is_tie(1.0, 1.0 + 1e-8))
check("차이 0.5 -> 동점 아님", not is_tie(5.0, 4.5))
check("순서를 바꿔도 결과 같음(대칭)", is_tie(0.8999999999999999, 0.9))
check(f"EPSILON 값은 {EPSILON}", EPSILON == 1e-9)

print("\n=== judge (Cross/X/UNDECIDED) ===")
check("Cross 점수가 더 크면 Cross", judge(5.0, 1.0) == CROSS)
check("X 점수가 더 크면 X", judge(1.0, 5.0) == X)
check("동점이면 UNDECIDED", judge(0.9, 0.8999999999999999) == UNDECIDED)
check("표준 라벨 글자 확인", (CROSS, X, UNDECIDED) == ("Cross", "X", "UNDECIDED"))

print("\n=== judge_ab (A/B/판정 불가) ===")
check("A가 크면 A", judge_ab(5.0, 1.0) == "A")
check("B가 크면 B (문서 예시 1.0 vs 5.0)", judge_ab(1.0, 5.0) == "B")
check("동점이면 판정 불가", judge_ab(0.9, 0.8999999999999999) == "판정 불가")

print("\n=== 실제 data.json: 단순 비교(>) vs epsilon 비교 ===")
# 아래 expected 변환은 이 확인용 스크립트에서만 쓰는 임시 방법이다.
# 실제 프로그램의 정규화는 3단계(labels.py)에서 제대로 만든다.
temp_map = {"+": CROSS, "x": X}
with open(os.path.join(HERE, "data.json"), encoding="utf-8") as f:
    data = json.load(f)

print(f"{'케이스':10s} {'점수 차이':>12s}  {'단순 >':8s} {'epsilon':10s} {'expected':8s} 결과")
for key, case in data["patterns"].items():
    n = int(key.split("_")[1])
    flt = data["filters"][f"size_{n}"]
    s_cross = mac_score(case["input"], flt["cross"])
    s_x = mac_score(case["input"], flt["x"])
    naive = CROSS if s_cross > s_x else X
    fair = judge(s_cross, s_x)
    expected = temp_map[case["expected"]]
    result = "PASS" if fair == expected else "FAIL"
    print(f"{key:10s} {abs(s_cross - s_x):12.2e}  {naive:8s} {fair:10s} {expected:8s} {result}")

print("\n모든 확인 통과")
