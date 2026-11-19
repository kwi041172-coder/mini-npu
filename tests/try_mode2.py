"""모드 2 화면 미리보기: data.json 을 읽어 필터 로드, 케이스 판정, 성능 분석, 결과 요약을 출력한다.
프로젝트 폴더에서 `python tests/try_mode2.py` 로 실행. (최종 main.py 는 9단계에서 만든다)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analyzer import analyze_all
from src.benchmark import run_benchmark
from src.data_loader import DataFileError, load_filters, load_json
from src.report import (print_benchmark_table, print_case_result, print_filter_status,
                        print_section_header, print_summary, summarize)

try:
    data = load_json()
except DataFileError as error:
    print(f"data.json 을 사용할 수 없습니다: {error}")
    sys.exit(1)

filters, filter_errors = load_filters(data)

print_section_header("[1] 필터 로드")
print_filter_status(filters, filter_errors)
print()
print_section_header("[2] 패턴 분석 (라벨 정규화 적용)")
results = analyze_all(data["patterns"], filters, filter_errors)
for result in results:
    print_case_result(result)

print()
print_section_header("[3] 성능 분석 (평균/10회)")
print_benchmark_table(run_benchmark())

print()
print_section_header("[4] 결과 요약")
print_summary(summarize(results))
