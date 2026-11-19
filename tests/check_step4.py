"""4단계(R2 모드 1 입력 처리) 자동 확인. 프로젝트 폴더에서 `python tests/check_step4.py` 로 실행."""
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from src.compare import judge_ab
from src.input_handler import parse_row, read_matrix, read_user_inputs
from src.mac import mac_score

MSG3 = "입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요."


def check(name, condition):
    print(("[통과] " if condition else "[실패] ") + name)
    if not condition:
        sys.exit(1)


def error_text(line, n=3):
    try:
        parse_row(line, n)
    except ValueError as e:
        return str(e)
    return None


def fake_keyboard(lines):
    """미리 준비한 줄을 차례로 '타이핑'해 주는 가짜 입력 장치."""
    iterator = iter(lines)
    return lambda prompt="": next(iterator)


print("=== parse_row: 올바른 입력 ===")
check("'0 1 0' -> [0.0, 1.0, 0.0]", parse_row("0 1 0", 3) == [0.0, 1.0, 0.0])
check("여러 칸 공백/앞뒤 공백 허용", parse_row("  1   0\t1  ", 3) == [1.0, 0.0, 1.0])
check("소수 허용 '0.5 1 0.25'", parse_row("0.5 1 0.25", 3) == [0.5, 1.0, 0.25])
check("음수 허용 '-1 0 1'", parse_row("-1 0 1", 3) == [-1.0, 0.0, 1.0])

print("\n=== parse_row: 잘못된 입력은 안내 문구와 함께 거부 ===")
for label, bad in [("숫자 2개(열 부족)", "0 1"), ("숫자 4개(열 초과)", "0 1 0 1"),
                   ("글자 포함", "0 a 1"), ("빈 줄", ""), ("쉼표 구분", "1,0,1"),
                   ("nan", "nan 1 0"), ("inf", "inf 0 0")]:
    check(f"{label}: {bad!r}", error_text(bad) == MSG3)
check("5x5 일 때는 문구가 '5개'로 바뀜", "5개의 숫자" in (error_text("1 2 3", 5) or ""))

print("\n=== read_matrix: 잘못 입력하면 그 줄만 다시 입력받는다 ===")
screen = []
keyboard = fake_keyboard(["0 1", "0 1 0",      # 1번째 줄: 한 번 틀리고 다시
                          "1 1 1",              # 2번째 줄: 한 번에 성공
                          "0 x 0", "0 1 0"])    # 3번째 줄: 한 번 틀리고 다시
matrix = read_matrix("필터 A", 3, keyboard, screen.append)
check("최종 행렬이 올바름", matrix == [[0.0, 1.0, 0.0], [1.0, 1.0, 1.0], [0.0, 1.0, 0.0]])
check("오류 안내가 정확히 2번 출력됨", screen.count(MSG3) == 2)
check("제목 줄 출력", screen[0] == "필터 A (3줄 입력, 공백 구분)")
print("        --- 가짜 화면 출력 ---")
for s in screen:
    print("        " + s)

print("\n=== read_user_inputs: 문서의 모드 1 예시 흐름 ===")
screen = []
keyboard = fake_keyboard(["0 1 0", "1 1 1", "0 1 0",      # 필터 A (십자가)
                          "1 0 1", "0 1 0", "1 0 1",      # 필터 B (X)
                          "1 0 1", "0 1 0", "1 0 1"])     # 패턴 (X)
a, b, p = read_user_inputs(3, keyboard, screen.append)
check("필터 A/B/패턴이 올바르게 저장됨",
      a == [[0, 1, 0], [1, 1, 1], [0, 1, 0]] and b == [[1, 0, 1], [0, 1, 0], [1, 0, 1]]
      and p == b)
check("구역 제목 '[1] 필터 입력' 출력", "# [1] 필터 입력" in screen)
check("구역 제목 '[2] 패턴 입력' 출력", "# [2] 패턴 입력" in screen)
check("저장 확인 문구 출력", "✓ 필터 A, B 저장 완료" in screen and "✓ 패턴 저장 완료" in screen)
score_a, score_b = mac_score(p, a), mac_score(p, b)
check(f"문서 예시: A 점수 {score_a}, B 점수 {score_b}", (score_a, score_b) == (1.0, 5.0))
check("문서 예시: 판정은 B", judge_ab(score_a, score_b) == "B")

print("\n=== 5x5 도 같은 코드로 입력 가능 ===")
rows = ["1 0 0 0 1", "0 1 0 1 0", "0 0 1 0 0", "0 1 0 1 0", "1 0 0 0 1"]
check("5x5 입력", read_matrix("패턴", 5, fake_keyboard(rows), lambda s: None)[2][2] == 1.0)

print("\n모든 확인 통과")
