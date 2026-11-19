"""3단계(R4 라벨 정규화) 확인용 스크립트. 프로젝트 폴더에서 `python tests/check_step3.py` 로 실행."""
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from src.compare import judge
from src.labels import CROSS, X, normalize_expected, normalize_filter_key
from src.mac import mac_score


def check(name, condition):
    print(("[통과] " if condition else "[실패] ") + name)
    if not condition:
        sys.exit(1)


def raises_value_error(func, arg):
    try:
        func(arg)
    except ValueError as e:
        print("        오류 메시지:", e)
        return True
    return False


print("=== 정규화를 안 하면 생기는 문제 ===")
check("'x' == 'X' 는 False (글자가 다르다)", ("x" == "X") is False)
check("'+' == 'Cross' 는 False (표기가 다르다)", ("+" == "Cross") is False)

print("\n=== normalize_expected ===")
check("'+' -> Cross", normalize_expected("+") == CROSS)
check("'x' -> X", normalize_expected("x") == X)
check("대문자 'X' -> X", normalize_expected("X") == X)
check("앞뒤 공백 ' + ' -> Cross", normalize_expected(" + ") == CROSS)
check("모르는 값 'O' 는 ValueError", raises_value_error(normalize_expected, "O"))
check("숫자 1 은 ValueError", raises_value_error(normalize_expected, 1))
check("None 은 ValueError", raises_value_error(normalize_expected, None))

print("\n=== normalize_filter_key ===")
check("'cross' -> Cross", normalize_filter_key("cross") == CROSS)
check("'x' -> X", normalize_filter_key("x") == X)
check("'Cross' (대소문자 달라도) -> Cross", normalize_filter_key("Cross") == CROSS)
check("모르는 키 'plus' 는 ValueError", raises_value_error(normalize_filter_key, "plus"))

print("\n=== 실제 data.json: 정규화 + MAC + 판정 (R7 미리보기) ===")
with open(os.path.join(HERE, "data.json"), encoding="utf-8") as f:
    data = json.load(f)

# 필터: 키를 표준 라벨로 바꿔서 {크기: {Cross: 행렬, X: 행렬}} 모양으로 정리
filters = {}
for size_key, pair in data["filters"].items():
    n = int(size_key.split("_")[1])
    filters[n] = {normalize_filter_key(k): matrix for k, matrix in pair.items()}
check("필터 3종 모두 Cross/X 로 정규화", all(set(v) == {CROSS, X} for v in filters.values()))

passed = 0
print(f"{'케이스':10s} {'원래 expected':12s} {'표준 expected':12s} {'판정':10s} 결과")
for key, case in data["patterns"].items():
    n = int(key.split("_")[1])
    s_cross = mac_score(case["input"], filters[n][CROSS])
    s_x = mac_score(case["input"], filters[n][X])
    decision = judge(s_cross, s_x)
    expected = normalize_expected(case["expected"])
    ok = decision == expected
    passed += ok
    print(f"{key:10s} {case['expected']!r:12s} {expected:12s} {decision:10s} {'PASS' if ok else 'FAIL'}")
print(f"\n총 {len(data['patterns'])}개 / 통과 {passed}개 / 실패 {len(data['patterns']) - passed}개")

print("\n모든 확인 통과")