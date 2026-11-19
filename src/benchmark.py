"""benchmark.py - 크기별 MAC 연산 시간 측정 (요구사항 R8).

측정 규칙
  - 시간은 ms(밀리초) 단위로 구한다.
  - 크기마다 10회 반복 측정해서 평균을 낸다.
  - 입력/출력(키보드, 화면, 파일) 시간은 넣지 않고 '연산 함수를 부르는 구간'만 잰다.
"""

import time

from src.mac import mac_score
from src.pattern_generator import make_cross, make_x

BENCHMARK_SIZES = (3, 5, 13, 25)   # 문서에서 요구하는 크기들
DEFAULT_REPEAT = 10                # 문서의 최소 반복 횟수


def average_time_ms(func, args, repeat=DEFAULT_REPEAT, warmup=1):
    """func(*args) 를 repeat 번 실행하면서 한 번 걸린 시간의 평균을 ms 로 돌려준다.

    warmup: 시간에 넣지 않고 먼저 한두 번 실행해 보는 '몸풀기' 횟수.
            (처음 실행은 준비 작업 때문에 유난히 느릴 수 있어서 결과를 왜곡한다)
    """
    if repeat < 1:
        raise ValueError("반복 횟수 repeat 는 1 이상이어야 합니다.")

    for _ in range(warmup):
        func(*args)                        # 시간을 재지 않는 몸풀기 실행

    total_seconds = 0.0
    for _ in range(repeat):
        start = time.perf_counter()        # 초 단위, 짧은 시간을 재는 데 가장 정밀한 시계
        func(*args)                        # <- 오직 이 구간만 잰다 (입출력 없음)
        end = time.perf_counter()
        total_seconds += end - start
    return total_seconds / repeat * 1000.0   # 평균(초) -> ms


def measure(n, repeat=DEFAULT_REPEAT, mac_func=mac_score):
    """N x N 크기에서 MAC 연산 1회의 평균 시간(ms)을 돌려준다."""
    pattern = make_cross(n)
    filt = make_x(n)
    return average_time_ms(mac_func, (pattern, filt), repeat)


def run_benchmark(sizes=BENCHMARK_SIZES, repeat=DEFAULT_REPEAT, mac_func=mac_score):
    """크기별로 측정해서 표 데이터(목록)를 돌려준다.

    각 항목: {"size": N, "avg_ms": 평균 시간(ms), "ops": 연산 횟수 N*N}
    """
    rows = []
    for n in sizes:
        rows.append({"size": n, "avg_ms": measure(n, repeat, mac_func), "ops": n * n})
    return rows
