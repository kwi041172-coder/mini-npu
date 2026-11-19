"""compare.py - 점수 비교와 판정 (요구사항 R6, R7).

핵심 규칙: 소수(float)는 '==' 나 '>' 로 직접 비교하지 않고,
           '허용오차(epsilon)'보다 작게 차이 나면 같은 점수(동점)로 본다.
"""

from src.labels import CROSS, X, UNDECIDED

# 이 값보다 작은 차이는 '같은 점수'로 간주한다. (문서 권장값)
EPSILON = 1e-9


def is_tie(score_a, score_b, eps=EPSILON):
    """두 점수가 허용오차 안에서 같으면 True (동점)."""
    return abs(score_a - score_b) < eps


def judge(cross_score, x_score):
    """모드 2용 판정. 'Cross' / 'X' / 'UNDECIDED' 중 하나를 돌려준다."""
    if is_tie(cross_score, x_score):
        return UNDECIDED
    if cross_score > x_score:
        return CROSS
    return X


def judge_ab(score_a, score_b):
    """모드 1용 판정. 'A' / 'B' / '판정 불가' 중 하나를 돌려준다."""
    if is_tie(score_a, score_b):
        return "판정 불가"
    if score_a > score_b:
        return "A"
    return "B"
