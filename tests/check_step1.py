"""1단계(R1, R5) 확인용 스크립트. 프로젝트 폴더에서 `python tests/check_step1.py` 로 실행."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.matrix import create_matrix, is_square_matrix, get_size, get_value, set_value
from src.mac import mac_score

CROSS_3 = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
X_3 = [[1, 0, 1], [0, 1, 0], [1, 0, 1]]


def check(name, condition):
    print(("[통과] " if condition else "[실패] ") + name)
    if not condition:
        sys.exit(1)


print("=== R1: 데이터 구조 ===")
m = create_matrix(3)
check("3x3 영행렬 생성", m == [[0.0] * 3 for _ in range(3)])
set_value(m, 1, 2, 7.5)
check("값 저장/읽기 (1,2)", get_value(m, 1, 2) == 7.5)
check("줄 간 공유 없음(다른 줄은 그대로 0.0)", m[0][2] == 0.0 and m[2][2] == 0.0)
for n in (3, 5, 13, 25):
    check(f"{n}x{n} 생성/크기", get_size(create_matrix(n)) == n)
check("정사각형 검사: 3x2 는 거부", not is_square_matrix([[1, 2, 3], [4, 5, 6]]))
check("정사각형 검사: 문자 포함은 거부", not is_square_matrix([[1, "a"], [2, 3]]))
check("정사각형 검사: 빈 리스트는 거부", not is_square_matrix([]))

print("\n=== R5: MAC 연산 (문서 예시) ===")
check("십자가 패턴 x 십자가 필터 = 5", mac_score(CROSS_3, CROSS_3) == 5.0)
check("십자가 패턴 x X 필터 = 1", mac_score(CROSS_3, X_3) == 1.0)
check("X 패턴 x 십자가 필터 = 1", mac_score(X_3, CROSS_3) == 1.0)
check("X 패턴 x X 필터 = 5", mac_score(X_3, X_3) == 5.0)
check("반환 타입은 float", isinstance(mac_score(CROSS_3, CROSS_3), float))

print("\n=== R5: 오류 처리 ===")
try:
    mac_score(CROSS_3, create_matrix(5))
    check("크기 불일치는 ValueError", False)
except ValueError as e:
    check(f"크기 불일치는 ValueError -> {e}", True)

print("\n=== 실제 data.json 으로 점수 계산 (판정은 2단계에서) ===")
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(here, "data.json"), encoding="utf-8") as f:
    data = json.load(f)
for key, case in data["patterns"].items():
    n = int(key.split("_")[1])
    flt = data["filters"][f"size_{n}"]
    s_cross = mac_score(case["input"], flt["cross"])
    s_x = mac_score(case["input"], flt["x"])
    print(f"{key:10s} expected={case['expected']!r:4s} cross={s_cross!r:22s} x={s_x!r}")

print("\n모든 확인 통과")