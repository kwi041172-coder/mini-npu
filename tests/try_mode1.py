"""4단계 직접 해 보기: 키보드로 필터 A, B, 패턴을 입력하고 점수와 판정을 본다.
프로젝트 폴더에서 `python tests/try_mode1.py` 로 실행. (연산 시간 측정은 7단계에서 추가)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.compare import judge_ab
from src.input_handler import read_user_inputs
from src.mac import mac_score
from src.report import print_section_header

filter_a, filter_b, pattern = read_user_inputs()
score_a = mac_score(pattern, filter_a)
score_b = mac_score(pattern, filter_b)

print()
print_section_header("[3] MAC 결과")
print(f"A 점수: {score_a}")
print(f"B 점수: {score_b}")
print(f"판정: {judge_ab(score_a, score_b)}")
