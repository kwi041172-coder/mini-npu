"""6단계(R3, R7 모드 2 케이스 처리) 확인. 프로젝트 폴더에서 `python tests/check_step6.py` 로 실행."""
import copy
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from src.analyzer import KIND_MISMATCH, KIND_TIE, analyze_all, analyze_case
from src.data_loader import KIND_SCHEMA, KIND_SIZE_MISMATCH, load_filters, load_json
from src.labels import CROSS, UNDECIDED, X
from src.mac import mac_score
from src.report import print_case_result, print_filter_status, print_section_header


def check(name, condition):
    print(("[통과] " if condition else "[실패] ") + name)
    if not condition:
        sys.exit(1)


data = load_json()
filters, filter_errors = load_filters(data)

print("=== 실제 data.json 6건 처리 ===")
results = analyze_all(data["patterns"], filters, filter_errors)
check("결과 6건", len(results) == 6)
check("결과 항목이 모두 같은 모양", all(set(r) == {"case_id", "cross_score", "x_score", "decision",
      "expected", "passed", "fail_kind", "fail_reason"} for r in results))
by_id = {r["case_id"]: r for r in results}

# 점수가 1단계 MAC 과 같은지
r = by_id["size_5_2"]
check("size_5_2 점수가 mac_score 와 같음",
      r["cross_score"] == mac_score(data["patterns"]["size_5_2"]["input"], filters[5][CROSS]))
check("size_5_2: Cross 판정, PASS", r["decision"] == CROSS and r["expected"] == CROSS and r["passed"])
check("size_13_1: X 판정, PASS", by_id["size_13_1"]["decision"] == X and by_id["size_13_1"]["passed"])
check("size_25_2: Cross 판정, PASS", by_id["size_25_2"]["decision"] == CROSS and by_id["size_25_2"]["passed"])
for cid in ("size_5_1", "size_13_2", "size_25_1"):
    r = by_id[cid]
    check(f"{cid}: 동점 -> UNDECIDED, FAIL, 종류 TIE",
          r["decision"] == UNDECIDED and not r["passed"] and r["fail_kind"] == KIND_TIE)
    check(f"{cid}: 사유에 '동점' 포함", "동점" in r["fail_reason"])
passed = sum(1 for r in results if r["passed"])
check(f"총 6 / 통과 {passed} / 실패 {6 - passed}  (예상: 통과 3, 실패 3)", passed == 3)

print("\n=== 로직 문제(MISMATCH) 만들어 보기: Cross 모양인데 expected 를 'x' 로 ===")
case = {"input": data["patterns"]["size_5_2"]["input"], "expected": "x"}
r = analyze_case("size_5_77", case, filters, filter_errors)
check("점수 차이는 분명 -> 동점 아님, 판정 Cross", r["decision"] == CROSS)
check("expected X 와 달라서 FAIL, 종류 MISMATCH", not r["passed"] and r["fail_kind"] == KIND_MISMATCH)

print("\n=== 이상한 케이스가 섞여도 끝까지 간다 ===")
mixed = copy.deepcopy(data["patterns"])
mixed["size_5_9"] = {"input": [[1, 0, 1], [0, 1, 0], [1, 0, 1]], "expected": "x"}   # 크기 불일치
mixed["size_13_9"] = {"input": data["patterns"]["size_13_1"]["input"]}              # expected 없음
mixed["bad_key"] = data["patterns"]["size_5_1"]                                     # 키 형식 오류
results2 = analyze_all(mixed, filters, filter_errors)
check("결과 9건 (프로그램 중단 없음)", len(results2) == 9)
by2 = {r["case_id"]: r for r in results2}
check("size_5_9: SIZE_MISMATCH", by2["size_5_9"]["fail_kind"] == KIND_SIZE_MISMATCH)
check("size_13_9: SCHEMA", by2["size_13_9"]["fail_kind"] == KIND_SCHEMA)
check("bad_key: SCHEMA", by2["bad_key"]["fail_kind"] == KIND_SCHEMA)
check("오류 케이스는 점수 None, passed False",
      all(by2[k]["cross_score"] is None and by2[k]["passed"] is False
          for k in ("size_5_9", "size_13_9", "bad_key")))
check("통과 3건은 그대로", sum(1 for r in results2 if r["passed"]) == 3)

print("\n=== 망가진 필터 ===")
broken = copy.deepcopy(data)
del broken["filters"]["size_13"]["x"]
f2, e2 = load_filters(broken)
results3 = analyze_all(data["patterns"], f2, e2)
by3 = {r["case_id"]: r for r in results3}
check("size_13 케이스 2건만 SCHEMA 로 FAIL", by3["size_13_1"]["fail_kind"] == KIND_SCHEMA
      and by3["size_13_2"]["fail_kind"] == KIND_SCHEMA)
check("size_5, size_25 케이스는 정상 처리", by3["size_5_2"]["passed"] and by3["size_25_2"]["passed"])

print("\n=== 화면 출력 모양 확인 ===")
screen = []
print_section_header("[1] 필터 로드", screen.append)
print_filter_status(filters, filter_errors, screen.append)
print_section_header("[2] 패턴 분석 (라벨 정규화 적용)", screen.append)
for r in results2:
    print_case_result(r, screen.append)
check("필터 로드 줄 출력", "✓ size_5  필터 로드 완료 (Cross, X)" in screen
      and "✓ size_13 필터 로드 완료 (Cross, X)" in screen)
check("PASS 줄 출력", "판정: Cross | expected: Cross | PASS" in screen)
check("동점 FAIL 줄 출력", "판정: UNDECIDED | expected: X | FAIL (동점 규칙)" in screen)
for line in screen:
    print("        " + line)

print("\n모든 확인 통과")
