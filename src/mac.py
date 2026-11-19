"""mac.py - MAC(Multiply-Accumulate, 곱하고 누적해서 더하기) 연산 (요구사항 R5).

규칙: NumPy 같은 외부 라이브러리 금지, sum() 같은 묶음 함수에 맡기지 않고
      반복문으로 직접 곱하고 직접 더한다.
"""

from src.matrix import get_size


def mac_score(pattern, filt):
    """패턴과 필터를 같은 위치끼리 곱해서 모두 더한 점수(float)를 돌려준다.

    점수가 클수록 패턴이 필터와 비슷하다.
    두 행렬의 크기가 다르거나 정사각형이 아니면 ValueError 를 일으킨다.
    """
    n_pattern = get_size(pattern)   # 정사각형 숫자 행렬이 아니면 여기서 ValueError
    n_filter = get_size(filt)
    if n_pattern != n_filter:
        raise ValueError(
            f"크기 불일치: 패턴 {n_pattern}x{n_pattern}, 필터 {n_filter}x{n_filter}"
        )

    total = 0.0                          # 누적 합(Accumulate)을 담는 바구니
    for row in range(n_pattern):         # 바깥 반복문: 줄(행)
        for col in range(n_pattern):     # 안쪽 반복문: 칸(열)
            total += pattern[row][col] * filt[row][col]   # 곱하고(Multiply) 더한다
    return float(total)