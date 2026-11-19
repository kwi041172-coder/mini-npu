"""7단계(R8 성능 분석) 확인. 프로젝트 폴더에서 `python tests/check_step7.py` 로 실행."""
import os
import sys
import time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from src.benchmark import BENCHMARK_SIZES, DEFAULT_REPEAT, average_time_ms, measure, run_benchmark
from src.mac import mac_score
from src.matrix import create_matrix
from src.pattern_generator import make_cross, make_x
from src.report import print_benchmark_table


def check(name, condition):
    print(("[통과] " if condition else "[실패] ") + name)
    if not condition:
        sys.exit(1)


def count_ones(matrix):
    total = 0
    for row in matrix:
        for value in row:
            total += value
    return total


print("=== 패턴 생성기 ===")
check("3x3 십자가가 문서 예시와 같음", make_cross(3) == [[0, 1, 0], [1, 1, 1], [0, 1, 0]])
check("3x3 X 가 문서 예시와 같음", make_x(3) == [[1, 0, 1], [0, 1, 0], [1, 0, 1]])
check("5x5 십자가: 가운데 줄/칸", make_cross(5)[2] == [1.0] * 5 and [r[2] for r in make_cross(5)] == [1.0] * 5)
for n in BENCHMARK_SIZES:
    check(f"{n}x{n}: 십자가와 X 의 1 개수는 각각 2N-1 = {2 * n - 1}",
          count_ones(make_cross(n)) == 2 * n - 1 and count_ones(make_x(n)) == 2 * n - 1)
check("생성한 3x3 로 MAC: 십자가 x 십자가 = 5, 십자가 x X = 1",
      mac_score(make_cross(3), make_cross(3)) == 5.0 and mac_score(make_cross(3), make_x(3)) == 1.0)

print("\n=== 연산 횟수가 정말 N*N 인가? (모든 칸이 1 이면 점수 = 곱셈·덧셈 횟수) ===")
for n in BENCHMARK_SIZES:
    ones = create_matrix(n, 1.0)
    check(f"{n}x{n}: 점수 {mac_score(ones, ones)} == {n * n}", mac_score(ones, ones) == n * n)

print("\n=== average_time_ms: 반복 횟수와 단위 ===")
calls = []
average_time_ms(lambda: calls.append(1), (), repeat=10, warmup=1)
check("repeat=10, warmup=1 이면 함수가 11번 불림 (그중 10번만 시간에 반영)", len(calls) == 11)
calls.clear()
average_time_ms(lambda: calls.append(1), (), repeat=10, warmup=0)
check("warmup=0 이면 정확히 10번", len(calls) == 10)
try:
    average_time_ms(lambda: None, (), repeat=0)
    check("repeat=0 은 ValueError", False)
except ValueError:
    check("repeat=0 은 ValueError", True)
avg = average_time_ms(time.sleep, (0.005,), repeat=3, warmup=0)
check(f"5ms 쉬는 함수를 재면 약 5 (ms 단위 확인): {avg:.2f} ms", 3 < avg < 100)

print("\n=== run_benchmark ===")
rows = run_benchmark()
check("기본 크기 3, 5, 13, 25", [r["size"] for r in rows] == [3, 5, 13, 25])
check("연산 횟수 N*N = 9, 25, 169, 625", [r["ops"] for r in rows] == [9, 25, 169, 625])
check("평균 시간이 모두 0 보다 큼", all(r["avg_ms"] > 0 for r in rows))
by = {r["size"]: r["avg_ms"] for r in rows}
check("큰 크기일수록 오래 걸림 (3<13, 5<25)", by[3] < by[13] and by[5] < by[25])
check("기본 반복 횟수는 10", DEFAULT_REPEAT == 10)

counter = []
def counting_mac(pattern, filt):
    counter.append(len(pattern))
    return 0.0
run_benchmark(sizes=(3, 5), repeat=10, mac_func=counting_mac)
check("연산 함수를 바꿔 끼울 수 있음 (3, 5 각각 10회 + 몸풀기 1회 = 22번 호출)", len(counter) == 22)

print("\n=== 성능 표 (이 컴퓨터에서 측정한 값) ===")
screen = []
print_benchmark_table(rows, screen.append)
check("표 머리 + 구분선 + 4줄", len(screen) == 6)
check("'3×3' 과 연산 횟수 625 가 표에 있음", "3×3" in screen[2] and "625" in screen[5])
for line in screen:
    print("    " + line)

print("\n=== O(N²) 근거: 연산 횟수가 늘어난 배율과 시간이 늘어난 배율 비교 (5×5 기준) ===")
print(f"    {'크기':<8}{'연산횟수 배율':>14}{'시간 배율':>12}{'1회당 시간(ns)':>18}")
base = rows[1]
for r in rows:
    per_op_ns = r["avg_ms"] * 1_000_000 / r["ops"]
    print(f"    {str(r['size']) + '×' + str(r['size']):<8}{r['ops'] / base['ops']:>14.1f}"
          f"{r['avg_ms'] / base['avg_ms']:>12.1f}{per_op_ns:>18.1f}")

print("\n모든 확인 통과")
