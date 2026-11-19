"""5단계(R3 JSON 로드와 스키마 검증) 확인. 프로젝트 폴더에서 `python tests/check_step5.py` 로 실행."""
import copy
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from src.data_loader import (CaseError, DataFileError, DEFAULT_DATA_PATH, KIND_SCHEMA,
                             KIND_SIZE_MISMATCH, extract_filter_size, extract_size,
                             load_filters, load_json, validate_case)
from src.labels import CROSS, X


def check(name, condition):
    print(("[통과] " if condition else "[실패] ") + name)
    if not condition:
        sys.exit(1)


def message_of(func, *args):
    """함수를 실행해서 DataFileError/ValueError/CaseError 의 메시지를 돌려준다. 오류가 없으면 None."""
    try:
        func(*args)
    except (DataFileError, ValueError, CaseError) as e:
        return str(e)
    return None


def case_error(key, case, filters, errors):
    try:
        validate_case(key, case, filters, errors)
    except CaseError as e:
        return e
    return None


print("=== extract_size: 키에서 크기 뽑기 ===")
check("'size_5_1' -> 5", extract_size("size_5_1") == 5)
check("'size_13_2' -> 13", extract_size("size_13_2") == 13)
check("'size_25_10' -> 25", extract_size("size_25_10") == 25)
for bad in ["size_5", "size__1", "sizeX_1", "size_a_1", "size_0_1", "size_05_1", "", "5_1"]:
    check(f"잘못된 키 {bad!r} 는 ValueError", message_of(extract_size, bad) is not None)
check("필터 키 'size_13' -> 13", extract_filter_size("size_13") == 13)
check("필터 키 'size_13_1' 은 거부", message_of(extract_filter_size, "size_13_1") is not None)

print("\n=== load_json: 파일 문제는 친절한 안내 + DataFileError ===")
with tempfile.TemporaryDirectory() as tmp:
    def write(name, text, encoding="utf-8"):
        path = os.path.join(tmp, name)
        with open(path, "w", encoding=encoding) as f:
            f.write(text)
        return path

    msg = message_of(load_json, os.path.join(tmp, "없는파일.json"))
    check("파일 없음 -> 안내", msg is not None and "찾을 수 없습니다" in msg)
    print("        메시지:", msg)

    msg = message_of(load_json, write("empty.json", ""))
    check("빈 파일 -> 안내 (지난번에 겪은 오류가 이제 친절한 메시지가 됨)", msg is not None and "비어" in msg)
    print("        메시지:", msg)

    msg = message_of(load_json, write("broken.json", '{"filters": {'))
    check("깨진 JSON -> 안내", msg is not None and "JSON 형식 오류" in msg)

    msg = message_of(load_json, write("list.json", "[1, 2, 3]"))
    check("최상위가 목록이면 안내", msg is not None and "객체" in msg)

    msg = message_of(load_json, write("nopat.json", '{"filters": {}}'))
    check("patterns 항목이 없으면 안내", msg is not None and "'patterns'" in msg)

    bom = write("bom.json", '{"filters": {}, "patterns": {}}', encoding="utf-8-sig")
    check("메모장 BOM 이 붙은 파일도 읽힘", load_json(bom) == {"filters": {}, "patterns": {}})

print("\n=== 실제 data.json ===")
print("        위치:", DEFAULT_DATA_PATH)
data = load_json()
check("filters/patterns 읽기 성공", set(data) >= {"filters", "patterns"})
filters, filter_errors = load_filters(data)
check("필터 크기 5, 13, 25 로드", sorted(filters) == [5, 13, 25])
check("필터 라벨이 모두 Cross/X 로 정규화됨", all(set(v) == {CROSS, X} for v in filters.values()))
check("필터 오류 없음", filter_errors == {})
for key, case in data["patterns"].items():
    pattern, pair, expected = validate_case(key, case, filters, filter_errors)
    check(f"{key}: 검사 통과 (크기 {len(pattern)}, expected {expected})",
          len(pattern) == len(pair[CROSS]) and expected in (CROSS, X))

print("\n=== 망가뜨린 필터: 그 크기만 오류가 되고 나머지는 계속 ===")
broken = copy.deepcopy(data)
broken["filters"]["size_5"]["cross"] = [[1, 0, 1], [0, 1, 0], [1, 0, 1]]      # 3x3 을 5 자리에
del broken["filters"]["size_13"]["x"]                                        # X 필터 삭제
broken["filters"]["size_25"]["plus"] = broken["filters"]["size_25"].pop("cross")  # 모르는 키
broken["filters"]["size_abc"] = {}                                           # 키 형식 오류
f2, e2 = load_filters(broken)
check("정상 필터는 하나도 안 남음(위에서 3개 모두 망가뜨림)", f2 == {})
check("오류 4건이 기록됨", sorted(e2) == ["size_13", "size_25", "size_5", "size_abc"])
for k, v in sorted(e2.items()):
    print(f"        {k}: {v}")

broken2 = copy.deepcopy(data)
broken2["filters"]["size_13"]["X"] = broken2["filters"]["size_13"]["x"]      # 'x' 와 'X' 중복
f3, e3 = load_filters(broken2)
check("정상 필터(5, 25)는 살아남음", sorted(f3) == [5, 25])
check("라벨 중복은 오류로 기록", "size_13" in e3 and "두 번" in e3["size_13"])

print("\n=== 망가뜨린 케이스: 종류와 사유가 정확해야 한다 ===")
good = data["patterns"]["size_5_1"]
three = [[1, 0, 1], [0, 1, 0], [1, 0, 1]]
scenarios = [
    ("크기 불일치 (키 size_5, 패턴 3x3)", "size_5_9", {"input": three, "expected": "x"}, KIND_SIZE_MISMATCH),
    ("expected 항목 없음", "size_5_9", {"input": good["input"]}, KIND_SCHEMA),
    ("input 항목 없음", "size_5_9", {"expected": "x"}, KIND_SCHEMA),
    ("모르는 expected 'O'", "size_5_9", {"input": good["input"], "expected": "O"}, KIND_SCHEMA),
    ("키 형식 오류", "pattern_1", good, KIND_SCHEMA),
    ("input 이 정사각형 아님", "size_5_9", {"input": [[1, 2], [3]], "expected": "x"}, KIND_SCHEMA),
    ("input 에 글자 포함", "size_5_9", {"input": [["a"]], "expected": "x"}, KIND_SCHEMA),
    ("해당 크기 필터 없음 (size_7)", "size_7_1", {"input": [[0] * 7] * 7, "expected": "x"}, KIND_SCHEMA),
    ("케이스가 객체가 아님", "size_5_9", "hello", KIND_SCHEMA),
]
for label, key, case, kind in scenarios:
    err = case_error(key, case, filters, filter_errors)
    check(f"{label} -> {kind}", err is not None and err.kind == kind)
    print(f"        사유: {err.message}")
err = case_error("size_5_1", good, f2, e2)
check("망가진 필터를 쓰는 케이스 -> SCHEMA 와 필터 오류 사유", err is not None
      and err.kind == KIND_SCHEMA and "필터 size_5 오류" in err.message)
print(f"        사유: {err.message}")

print("\n=== 전체 흐름: 이상한 케이스가 섞여도 끝까지 간다 ===")
mixed = dict(data["patterns"])
mixed["size_5_9"] = {"input": three, "expected": "x"}
mixed["size_13_9"] = {"input": mixed["size_13_1"]["input"]}
ok = bad = 0
for key, case in mixed.items():
    try:
        validate_case(key, case, filters, filter_errors)
        ok += 1
        print(f"        {key:10s} 검사 통과")
    except CaseError as e:
        bad += 1
        print(f"        {key:10s} FAIL ({e.kind}) {e.message}")
check(f"정상 {ok}건 + 오류 {bad}건 모두 처리 (프로그램 중단 없음)", (ok, bad) == (6, 2))

print("\n모든 확인 통과")
