"""analyzer.py - 모드 2의 케이스 처리 (요구사항 R3, R7).

패턴 케이스 하나를 '검사 -> MAC 점수 -> 판정 -> expected 와 비교' 순서로 처리하고,
결과를 사전(dict) 하나로 정리해 돌려준다. 어떤 케이스가 이상해도 예외를 밖으로 던지지 않고
그 케이스를 FAIL 로 기록한 뒤 다음 케이스로 넘어간다.
"""

from src.compare import EPSILON, judge
from src.data_loader import CaseError, KIND_SCHEMA, validate_case
from src.labels import CROSS, UNDECIDED, X
from src.mac import mac_score

# 실패 종류 (data_loader 의 SCHEMA, SIZE_MISMATCH 에 이어서)
KIND_TIE = "TIE"            # 수치 비교 문제: 점수 차이가 epsilon 보다 작아 동점 -> UNDECIDED
KIND_MISMATCH = "MISMATCH"  # 로직 문제: 점수 차이는 분명한데 판정이 expected 와 다름


def _make_result(case_id, cross_score=None, x_score=None, decision=None,
                 expected=None, passed=False, fail_kind=None, fail_reason=None):
    """케이스 결과를 항상 같은 모양의 사전으로 만든다. (해당 없는 값은 None)"""
    return {
        "case_id": case_id,
        "cross_score": cross_score,
        "x_score": x_score,
        "decision": decision,
        "expected": expected,
        "passed": passed,
        "fail_kind": fail_kind,
        "fail_reason": fail_reason,
    }


def analyze_case(case_id, case, filters, filter_errors):
    """패턴 케이스 하나를 처리해서 결과 사전을 돌려준다. 이 함수는 예외를 밖으로 던지지 않는다."""
    # 1) 검사: 키에서 크기 추출, 크기 일치, expected 정규화 (실패하면 그 케이스만 FAIL)
    try:
        pattern, pair, expected = validate_case(case_id, case, filters, filter_errors)
    except CaseError as error:
        return _make_result(case_id, fail_kind=error.kind, fail_reason=error.message)

    # 2) MAC 점수 (검사를 통과했으므로 보통 오류가 없지만, 만약을 위한 안전장치)
    try:
        cross_score = mac_score(pattern, pair[CROSS])
        x_score = mac_score(pattern, pair[X])
    except ValueError as error:
        return _make_result(case_id, expected=expected,
                            fail_kind=KIND_SCHEMA, fail_reason=str(error))

    # 3) 판정 (epsilon 동점 규칙 적용) 과 expected 비교
    decision = judge(cross_score, x_score)
    passed = decision == expected

    fail_kind = None
    fail_reason = None
    if not passed:
        if decision == UNDECIDED:
            fail_kind = KIND_TIE
            fail_reason = (f"동점(UNDECIDED) 처리 규칙에 따라 FAIL "
                           f"(|Cross-X| = {abs(cross_score - x_score):.1e} < {EPSILON})")
        else:
            fail_kind = KIND_MISMATCH
            fail_reason = f"판정 {decision} 이(가) expected {expected} 와 다름"

    return _make_result(case_id, cross_score, x_score, decision, expected,
                        passed, fail_kind, fail_reason)


def analyze_all(patterns, filters, filter_errors):
    """patterns(data.json 의 patterns 사전)의 모든 케이스를 처리해 결과 목록을 돌려준다."""
    results = []
    for case_id, case in patterns.items():
        results.append(analyze_case(case_id, case, filters, filter_errors))
    return results
