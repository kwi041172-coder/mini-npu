"""modes.py - 모드 선택과 모드 1, 모드 2 의 전체 실행 흐름 (요구사항 R10).

지금까지 만든 부품(입력, MAC, 판정, 검증, 성능 측정, 출력)을 순서대로 연결한다.
키보드/화면을 바깥에서 바꿔 끼울 수 있게 input_func, output_func 를 받는다.
"""

from src.analyzer import analyze_all
from src.benchmark import average_time_ms, run_benchmark
from src.compare import judge_ab
from src.data_loader import DEFAULT_DATA_PATH, DataFileError, load_filters, load_json
from src.input_handler import read_user_inputs
from src.mac import mac_score
from src.report import (print_benchmark_table, print_case_result, print_filter_status,
                        print_mode1_result, print_section_header, print_summary, summarize)

MENU_LINES = ("[모드 선택]", "", "1. 사용자 입력 (3x3)", "2. data.json 분석")


def choose_mode(input_func=input, output_func=print):
    """메뉴를 보여 주고 1 또는 2 를 입력받는다. 다른 입력이면 안내 후 다시 묻는다."""
    for line in MENU_LINES:
        output_func(line)
    while True:
        choice = input_func("선택: ").strip()
        if choice in ("1", "2"):
            return int(choice)
        output_func("잘못된 선택입니다. 1 또는 2를 입력하세요.")


def run_user_mode(input_func=input, output_func=print):
    """모드 1: 필터 A, B 입력 -> 저장 확인 -> 패턴 입력 -> MAC 연산 -> 판정 -> 성능 분석(3x3)."""
    filter_a, filter_b, pattern = read_user_inputs(3, input_func, output_func)   # [1], [2]
    output_func("")

    print_section_header("[3] MAC 결과", output_func)
    score_a = mac_score(pattern, filter_a)
    score_b = mac_score(pattern, filter_b)
    # 연산 시간: 이번에 입력한 3x3 패턴과 필터 A 로 MAC 1회를 10번 재서 평균 (입출력 제외)
    avg_ms = average_time_ms(mac_score, (pattern, filter_a))
    print_mode1_result(score_a, score_b, judge_ab(score_a, score_b), avg_ms, output_func)
    output_func("")

    print_section_header("[4] 성능 분석 (평균/10회)", output_func)
    print_benchmark_table(run_benchmark(sizes=(3,)), output_func)


def run_json_mode(output_func=print, data_path=DEFAULT_DATA_PATH):
    """모드 2: 필터 로드 -> 패턴 로드/검증 -> MAC 연산/판정/PASS-FAIL -> 성능 분석 -> 결과 요약.

    파일을 쓸 수 없으면 안내만 출력하고 False 를 돌려준다. 끝까지 진행하면 True.
    """
    try:
        data = load_json(data_path)
    except DataFileError as error:
        output_func(f"data.json 을 사용할 수 없습니다: {error}")
        return False

    filters, filter_errors = load_filters(data)
    print_section_header("[1] 필터 로드", output_func)
    print_filter_status(filters, filter_errors, output_func)
    output_func("")

    print_section_header("[2] 패턴 분석 (라벨 정규화 적용)", output_func)
    results = analyze_all(data["patterns"], filters, filter_errors)
    for result in results:
        print_case_result(result, output_func)
    output_func("")

    print_section_header("[3] 성능 분석 (평균/10회)", output_func)
    print_benchmark_table(run_benchmark(), output_func)      # 3x3, 5x5, 13x13, 25x25
    output_func("")

    print_section_header("[4] 결과 요약", output_func)
    print_summary(summarize(results), output_func)
    return True
