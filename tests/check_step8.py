"""8단계(R9 결과 요약, 모드 1 결과 출력) 확인. 프로젝트 폴더에서 `python tests/check_step8.py` 로 실행."""
import copy
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from src.analyzer import KIND_MISMATCH, KIND_TIE, analyze_all
from src.data_loader import KIND_SCHEMA, KIND_SIZE_MISMATCH, load_filters, load_json
from src.report import print_mode1_result, print_summary, summarize


def check(name, condition):
    print(("[통과] " if condition else "[실패] ") + name)
    if not condition:
        sys.exit(1)


data = load_json()
filters, filter_errors = load_filters(data)
results = analyze_all(data["patterns"], filters, filter_errors)

print("=== summarize: 실제 data.json 6건 ===")
s = summarize(results)
check("총 6 / 통과 3 / 실패 3", (s["total"], s["passed"], s["failed"]) == (6, 3, 3))
check("통과 + 실패 = 총", s["passed"] + s["failed"] == s["total"])
check("실패 목록 = size_5_1, size_13_2, size_25_1",
      [r["case_id"] for r in s["failures"]] == ["size_5_1", "size_13_2", "size_25_1"])
check("실패 종류별: 동점(TIE) 3건", s["kind_counts"] == {KIND_TIE: 3})

print("\n=== print_summary: 실제 data.json ===")
screen = []
print_summary(s, screen.append)
for line in screen:
    print("    " + line)
check("'총 테스트: 6개' 출력", "총 테스트: 6개" in screen)
check("'통과: 3개' 출력", "통과: 3개" in screen)
check("'실패: 3개' 출력", "실패: 3개" in screen)
check("실패 케이스 식별자와 사유 출력", any(l.startswith("- size_5_1: 동점(UNDECIDED)") for l in screen))
check("실패 종류별 줄 출력", "실패 종류별: 동점 규칙 3건" in screen)
check("README 안내 문구 출력", any("README.md" in l and "결과 리포트" in l for l in screen))

print("\n=== 실패가 하나도 없을 때 ===")
only_pass = [r for r in results if r["passed"]]
s0 = summarize(only_pass)
screen0 = []
print_summary(s0, screen0.append)
check("총 3 / 통과 3 / 실패 0", (s0["total"], s0["passed"], s0["failed"]) == (3, 3, 0))
check("'실패 케이스: 없음' 출력", "실패 케이스: 없음" in screen0)
check("실패 종류별 줄은 없음", not any("실패 종류별" in l for l in screen0))

print("\n=== 결과가 하나도 없을 때(빈 목록)도 멈추지 않는다 ===")
s_empty = summarize([])
check("총 0 / 통과 0 / 실패 0", (s_empty["total"], s_empty["passed"], s_empty["failed"]) == (0, 0, 0))
print_summary(s_empty, lambda text: None)
check("빈 목록 출력도 오류 없음", True)

print("\n=== 여러 종류의 실패가 섞였을 때 ===")
mixed = copy.deepcopy(data["patterns"])
mixed["size_5_9"] = {"input": [[1, 0, 1], [0, 1, 0], [1, 0, 1]], "expected": "x"}      # 크기 불일치
mixed["size_13_9"] = {"input": data["patterns"]["size_13_1"]["input"]}                 # expected 없음
mixed["size_5_77"] = {"input": data["patterns"]["size_5_2"]["input"], "expected": "x"}  # 판정 불일치
s2 = summarize(analyze_all(mixed, filters, filter_errors))
check("총 9 / 통과 3 / 실패 6", (s2["total"], s2["passed"], s2["failed"]) == (9, 3, 6))
check("종류별 개수 TIE 3, SIZE_MISMATCH 1, SCHEMA 1, MISMATCH 1",
      s2["kind_counts"] == {KIND_TIE: 3, KIND_SIZE_MISMATCH: 1, KIND_SCHEMA: 1, KIND_MISMATCH: 1})
screen2 = []
print_summary(s2, screen2.append)
for line in screen2:
    print("    " + line)

print("\n=== print_mode1_result (모드 1 결과 출력) ===")
screen = []
print_mode1_result(1.0, 5.0, "B", 0.0123, screen.append)
check("A 점수 줄", "A 점수: 1.0" in screen)
check("B 점수 줄", "B 점수: 5.0" in screen)
check("연산 시간 줄", "연산 시간(평균/10회): 0.0123 ms" in screen)
check("판정 B", "판정: B" in screen)
screen = []
print_mode1_result(0.9, 0.8999999999999999, "판정 불가", 0.01, screen.append)
check("동점이면 문서 예시처럼 '판정 불가 (|A-B| < 1e-9)'", "판정: 판정 불가 (|A-B| < 1e-9)" in screen)
for line in screen:
    print("    " + line)
screen = []
print_mode1_result(5.0, 1.0, "A", 0.02, screen.append)
check("판정 A", "판정: A" in screen)

print("\n모든 확인 통과")
