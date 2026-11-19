"""input_handler.py - 모드 1(사용자 입력 3x3)의 입력 처리 (요구사항 R2).

규칙: 한 줄에 공백으로 구분해서 숫자를 입력받는다.
      형식이 틀리면 안내 문구를 출력하고 그 줄을 다시 입력받는다.

테스트하기 쉽도록 '입력 장치(input_func)'와 '출력 장치(output_func)'를
바깥에서 바꿔 끼울 수 있게 만들었다. 평소에는 키보드(input)와 화면(print)을 쓰고,
테스트할 때는 미리 준비한 입력을 흘려 넣는다.
"""

import math

from src.report import print_section_header


def format_error_message(n):
    """형식 오류 안내 문구."""
    return f"입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요."


def parse_row(line, n):
    """글자 한 줄을 숫자 n개의 리스트로 바꾼다. 형식이 틀리면 ValueError.

    틀린 경우: 숫자가 n개가 아님(열 수 불일치), 숫자가 아닌 글자 포함(파싱 실패),
               nan/inf 같은 비정상 값
    """
    parts = line.split()            # 공백(여러 칸, 탭 포함) 기준으로 자른다
    if len(parts) != n:
        raise ValueError(format_error_message(n))

    row = []
    for part in parts:
        try:
            value = float(part)     # '1' -> 1.0, '0.5' -> 0.5, 'a' -> 오류
        except ValueError:
            raise ValueError(format_error_message(n)) from None
        if not math.isfinite(value):   # 'nan', 'inf' 거부
            raise ValueError(format_error_message(n))
        row.append(value)
    return row


def read_matrix(title, n=3, input_func=input, output_func=print):
    """n줄을 입력받아 n x n 행렬을 돌려준다. 잘못 입력한 줄은 다시 입력받는다."""
    output_func(f"{title} ({n}줄 입력, 공백 구분)")
    matrix = []
    while len(matrix) < n:
        line = input_func("")
        try:
            row = parse_row(line, n)
        except ValueError as error:
            output_func(str(error))
            output_func(f"  → {len(matrix) + 1}번째 줄을 다시 입력하세요.")
            continue                # 저장하지 않고 같은 줄을 다시 입력받는다
        matrix.append(row)
    return matrix


def read_user_inputs(n=3, input_func=input, output_func=print):
    """필터 A, 필터 B, 패턴을 차례로 입력받아 (A, B, 패턴)을 돌려준다."""
    print_section_header("[1] 필터 입력", output_func)
    filter_a = read_matrix("필터 A", n, input_func, output_func)
    output_func("")
    filter_b = read_matrix("필터 B", n, input_func, output_func)
    output_func("✓ 필터 A, B 저장 완료")
    output_func("")

    print_section_header("[2] 패턴 입력", output_func)
    pattern = read_matrix("패턴", n, input_func, output_func)
    output_func("✓ 패턴 저장 완료")
    return filter_a, filter_b, pattern
