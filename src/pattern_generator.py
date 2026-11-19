"""pattern_generator.py - N x N 십자가(Cross)와 X 패턴 자동 생성 (보너스 과제의 기본 형태).

성능 측정(benchmark.py)에서 3x3 ~ 25x25 크기의 시험용 데이터를 만들 때 쓴다.
3x3 일 때 문서의 예시와 같은 모양이 나온다.

    make_cross(3)      make_x(3)
    0 1 0              1 0 1
    1 1 1              0 1 0
    0 1 0              1 0 1
"""

from src.matrix import create_matrix, set_value


def make_cross(n):
    """가운데 줄과 가운데 칸을 1.0 으로 채운 십자가 패턴 (N 이 홀수일 때 정확히 가운데)."""
    if n < 1:
        raise ValueError("크기 n은 1 이상이어야 합니다.")
    matrix = create_matrix(n, 0.0)
    mid = n // 2
    for i in range(n):
        set_value(matrix, mid, i, 1.0)   # 가운데 가로줄
        set_value(matrix, i, mid, 1.0)   # 가운데 세로줄
    return matrix


def make_x(n):
    """두 대각선을 1.0 으로 채운 X 패턴."""
    if n < 1:
        raise ValueError("크기 n은 1 이상이어야 합니다.")
    matrix = create_matrix(n, 0.0)
    for i in range(n):
        set_value(matrix, i, i, 1.0)             # 왼쪽 위 -> 오른쪽 아래
        set_value(matrix, i, n - 1 - i, 1.0)     # 오른쪽 위 -> 왼쪽 아래
    return matrix
