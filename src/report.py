"""report.py - 콘솔 출력 모음 (요구사항 R9).

들어 있는 것: 구역 제목, 필터 로드 현황, 케이스 결과, 성능 표,
              모드 1 결과(점수/시간/판정), 모드 2 결과 요약(총/통과/실패).
"""

import unicodedata

from src.analyzer import KIND_MISMATCH, KIND_TIE
from src.compare import EPSILON
from src.data_loader import KIND_SCHEMA, KIND_SIZE_MISMATCH
from src.labels import CROSS, X

# 실패 종류를 화면에 보여 줄 한글 이름
KIND_NAMES = {
    KIND_SCHEMA: "스키마 오류",
    KIND_SIZE_MISMATCH: "크기 불일치",
    KIND_TIE: "동점 규칙",
    KIND_MISMATCH: "판정 불일치",
}


def print_section_header(title, output_func=print):
    """문서 예시처럼 구역 제목을 세 줄로 출력한다.

    #----------------------------------------
    # [1] 필터 입력
    #----------------------------------------
    """
    line = "#" + "-" * 39
    output_func(line)
    output_func("# " + title)
    output_func(line)


def print_filter_status(filters, filter_errors, output_func=print):
    """필터 로드 결과를 한 줄씩 출력한다. (정상은 ✓, 문제는 ✗ 와 사유)"""
    for n in filters:
        name = f"size_{n}"
        output_func(f"✓ {name:<7} 필터 로드 완료 ({CROSS}, {X})")
    for key, message in filter_errors.items():
        output_func(f"✗ {key:<7} 필터 오류: {message}")


def print_case_result(result, output_func=print):
    """케이스 결과 하나를 문서 예시 모양으로 출력한다."""
    output_func(f"--- {result['case_id']} ---")
    kind_name = KIND_NAMES.get(result["fail_kind"], result["fail_kind"])

    if result["cross_score"] is None:
        # 검사 단계에서 막혀 점수를 계산하지 못한 케이스
        output_func(f"검사 실패: {result['fail_reason']}")
        output_func(f"판정: - | expected: {result['expected'] or '-'} | FAIL ({kind_name})")
        return

    output_func(f"Cross 점수: {result['cross_score']}")
    output_func(f"X 점수: {result['x_score']}")
    status = "PASS" if result["passed"] else f"FAIL ({kind_name})"
    output_func(f"판정: {result['decision']} | expected: {result['expected']} | {status}")
    if not result["passed"]:
        output_func(f"  사유: {result['fail_reason']}")


# ---------------------------------------------------------------- 성능 표
def _display_width(text):
    """화면에서 차지하는 칸 수. 한글은 한 글자가 두 칸이라서 따로 센다."""
    width = 0
    for ch in text:
        width += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return width


def _pad_right(text, width):
    """왼쪽 정렬: 글자 뒤에 공백을 채워 width 칸으로 맞춘다."""
    return text + " " * (width - _display_width(text))


def _pad_left(text, width):
    """오른쪽 정렬: 글자 앞에 공백을 채워 width 칸으로 맞춘다."""
    return " " * (width - _display_width(text)) + text


def print_benchmark_table(rows, output_func=print):
    """크기 / 평균 시간(ms) / 연산 횟수 표를 출력한다. rows 는 run_benchmark 의 결과."""
    output_func(_pad_right("크기", 10) + _pad_left("평균 시간(ms)", 16) + _pad_left("연산 횟수", 12))
    output_func("-" * 38)
    for row in rows:
        label = f"{row['size']}×{row['size']}"
        output_func(_pad_right(label, 10)
                    + _pad_left(f"{row['avg_ms']:.4f}", 16)
                    + _pad_left(str(row["ops"]), 12))


# ---------------------------------------------------------------- 모드 1 결과
def _epsilon_text():
    """EPSILON 을 문서 예시처럼 '1e-9' 모양의 글자로 만든다."""
    return f"{EPSILON:.0e}".replace("e-0", "e-")


def print_mode1_result(score_a, score_b, judgement, avg_ms, output_func=print):
    """모드 1 결과: A/B 점수, 연산 시간, 판정. judgement 는 judge_ab 의 결과('A'/'B'/'판정 불가')."""
    output_func(f"A 점수: {score_a}")
    output_func(f"B 점수: {score_b}")
    output_func(f"연산 시간(평균/10회): {avg_ms:.4f} ms")
    if judgement == "판정 불가":
        output_func(f"판정: 판정 불가 (|A-B| < {_epsilon_text()})")
    else:
        output_func(f"판정: {judgement}")


# ---------------------------------------------------------------- 모드 2 결과 요약
def summarize(results):
    """analyze_all 의 결과 목록을 세어서 요약 사전으로 돌려준다.

    돌려주는 값: total(총), passed(통과), failed(실패),
                failures(실패한 결과들), kind_counts(실패 종류별 개수)
    """
    passed = 0
    failures = []
    kind_counts = {}
    for result in results:
        if result["passed"]:
            passed += 1
        else:
            failures.append(result)
            kind = result["fail_kind"]
            kind_counts[kind] = kind_counts.get(kind, 0) + 1
    return {
        "total": len(results),
        "passed": passed,
        "failed": len(failures),
        "failures": failures,
        "kind_counts": kind_counts,
    }


def print_summary(summary, output_func=print):
    """총 테스트/통과/실패 개수와 실패 케이스 목록(식별자 + 사유)을 출력한다."""
    output_func(f"총 테스트: {summary['total']}개")
    output_func(f"통과: {summary['passed']}개")
    output_func(f"실패: {summary['failed']}개")
    output_func("")

    if summary["failed"] == 0:
        output_func("실패 케이스: 없음")
    else:
        output_func("실패 케이스:")
        for result in summary["failures"]:
            output_func(f"- {result['case_id']}: {result['fail_reason']}")
        output_func("")
        counts = ", ".join(f"{KIND_NAMES.get(kind, kind)} {count}건"
                           for kind, count in summary["kind_counts"].items())
        output_func(f"실패 종류별: {counts}")

    output_func("")
    output_func('(상세 원인 분석 및 복잡도 설명은 README.md의 "결과 리포트" 섹션에 작성)')
