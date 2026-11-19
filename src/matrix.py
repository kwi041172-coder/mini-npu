"""matrix.py - N x N 행렬(2차원 배열)을 다루는 기본 도구 모음 (요구사항 R1).

행렬은 파이썬의 '리스트의 리스트'로 표현한다.
    [[0, 1, 0],
     [1, 1, 1],
     [0, 1, 0]]
m[행][열] 로 특정 위치의 값을 읽고 쓸 수 있다. (예: m[1][2] -> 2번째 줄의 3번째 값)
"""


def create_matrix(n, fill=0.0):
    """n x n 크기의 행렬을 만들고 모든 칸을 fill 값으로 채운다."""
    if n <= 0:
        raise ValueError("크기 n은 1 이상이어야 합니다.")
    matrix = []
    for _ in range(n):
        row = []
        for _ in range(n):
            row.append(fill)
        matrix.append(row)  # 줄마다 새 리스트를 만든다(같은 줄 공유 방지)
    return matrix


def is_number(value):
    """int 또는 float 이면 True. (True/False 같은 bool 은 숫자로 보지 않는다)"""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_square_matrix(matrix):
    """정사각형(N x N) 이고 모든 값이 숫자인지 검사한다."""
    if not isinstance(matrix, list) or len(matrix) == 0:
        return False
    n = len(matrix)
    for row in matrix:
        if not isinstance(row, list) or len(row) != n:
            return False
        for value in row:
            if not is_number(value):
                return False
    return True


def get_size(matrix):
    """정사각형 행렬의 크기 N을 돌려준다."""
    if not is_square_matrix(matrix):
        raise ValueError("정사각형(N x N) 숫자 행렬이 아닙니다.")
    return len(matrix)


def get_value(matrix, row, col):
    """(row, col) 위치의 값을 읽는다. 0부터 시작."""
    return matrix[row][col]


def set_value(matrix, row, col, value):
    """(row, col) 위치에 값을 저장한다. 0부터 시작."""
    matrix[row][col] = value