"""9단계(R10 실행 흐름, main.py) 확인. 프로젝트 폴더에서 `python tests/check_step9.py` 로 실행."""
import copy
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from main import main
from src.data_loader import load_json
from src.modes import choose_mode, run_json_mode, run_user_mode


def check(name, condition):
    print(("[통과] " if condition else "[실패] ") + name)
    if not condition:
        sys.exit(1)


def fake_keyboard(lines):
    """미리 준비한 줄을 차례로 '타이핑'해 주는 가짜 입력 장치."""
    iterator = iter(lines)

    def keyboard(prompt=""):
        try:
            return next(iterator)
        except StopIteration:
            raise AssertionError("준비한 입력이 부족합니다") from None
    return keyboard


def interrupting_keyboard(lines, error):
    """준비한 줄을 다 입력한 뒤 Ctrl+C(또는 입력 끊김)가 일어나는 가짜 입력 장치."""
    iterator = iter(lines)

    def keyboard(prompt=""):
        try:
            return next(iterator)
        except StopIteration:
            raise error from None
    return keyboard


def index_of(screen, text):
    return screen.index(text)


CROSS_A = ["0 1 0", "1 1 1", "0 1 0"]
X_B = ["1 0 1", "0 1 0", "1 0 1"]

print("=== 모드 선택 ===")
screen = []
mode = choose_mode(fake_keyboard(["3", "abc", "", "2"]), screen.append)
check("엉뚱한 입력 3번 뒤 '2' 를 고르면 2", mode == 2)
check("안내 문구가 3번 출력됨", screen.count("잘못된 선택입니다. 1 또는 2를 입력하세요.") == 3)
check("메뉴 문구 출력", "1. 사용자 입력 (3x3)" in screen and "2. data.json 분석" in screen)
check("앞뒤 공백 ' 1 ' 도 1 로 인식", choose_mode(fake_keyboard([" 1 "]), lambda s: None) == 1)

print("\n=== 모드 1: 문서 예시 (오류 입력 1번 섞음) ===")
screen = []
run_user_mode(fake_keyboard(["0 1"] + CROSS_A + X_B + X_B), screen.append)
check("형식 오류 안내가 1번 출력됨",
      screen.count("입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요.") == 1)
check("A 점수 1.0 / B 점수 5.0 / 판정 B",
      "A 점수: 1.0" in screen and "B 점수: 5.0" in screen and "판정: B" in screen)
check("연산 시간 줄 출력", any(l.startswith("연산 시간(평균/10회): ") and l.endswith(" ms") for l in screen))
order = [index_of(screen, h) for h in ("# [1] 필터 입력", "# [2] 패턴 입력", "# [3] MAC 결과",
                                       "# [4] 성능 분석 (평균/10회)")]
check("구역 순서 [1] -> [2] -> [3] -> [4]", order == sorted(order))
check("성능 분석에 3×3 한 줄", any(l.startswith("3×3") and l.rstrip().endswith("9") for l in screen))
check("성능 분석에 다른 크기는 없음(모드 1 은 3x3 만)", not any(l.startswith("5×5") for l in screen))

print("\n=== 모드 1: 동점이면 '판정 불가' (문서의 0.9 vs 0.8999999999999999 예시) ===")
screen = []
tie_a = ["0.1 0.1 0.1"] * 3                   # 0.1 을 아홉 번 더하면 0.8999999999999999
tie_b = ["0.9 0 0", "0 0 0", "0 0 0"]         # 0.9
run_user_mode(fake_keyboard(tie_a + tie_b + ["1 1 1"] * 3), screen.append)
check("A 점수 0.8999999999999999, B 점수 0.9", "A 점수: 0.8999999999999999" in screen and "B 점수: 0.9" in screen)
check("판정 불가 (|A-B| < 1e-9)", "판정: 판정 불가 (|A-B| < 1e-9)" in screen)

print("\n=== 모드 2: 실제 data.json ===")
screen = []
ok = run_json_mode(screen.append)
check("끝까지 진행하면 True", ok is True)
order = [index_of(screen, h) for h in ("# [1] 필터 로드", "# [2] 패턴 분석 (라벨 정규화 적용)",
                                       "# [3] 성능 분석 (평균/10회)", "# [4] 결과 요약")]
check("구역 순서 [1] -> [2] -> [3] -> [4]", order == sorted(order))
check("총 6 / 통과 3 / 실패 3", "총 테스트: 6개" in screen and "통과: 3개" in screen and "실패: 3개" in screen)
check("성능 분석에 3×3, 5×5, 13×13, 25×25 모두 포함",
      all(any(l.startswith(name) for l in screen) for name in ("3×3", "5×5", "13×13", "25×25")))

print("\n=== 모드 2: data.json 에 문제가 있어도 프로그램이 멈추지 않는다 ===")
with tempfile.TemporaryDirectory() as tmp:
    def write(name, text):
        path = os.path.join(tmp, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    for label, path in [("파일 없음", os.path.join(tmp, "없음.json")),
                        ("빈 파일", write("empty.json", "")),
                        ("깨진 JSON", write("broken.json", '{"filters": {'))]:
        screen = []
        ok = run_json_mode(screen.append, path)
        check(f"{label}: 안내 출력 후 False", ok is False and "사용할 수 없습니다" in screen[0])
        print("        " + screen[0])

    data = load_json()
    data["patterns"]["size_5_9"] = {"input": [[1, 0, 1], [0, 1, 0], [1, 0, 1]], "expected": "x"}
    data["patterns"]["size_13_9"] = {"input": data["patterns"]["size_13_1"]["input"]}
    path = write("mixed.json", json.dumps(data))
    screen = []
    ok = run_json_mode(screen.append, path)
    check("이상한 케이스 2건이 섞여도 끝까지 진행(True)", ok is True)
    check("총 8 / 통과 3 / 실패 5", "총 테스트: 8개" in screen and "통과: 3개" in screen and "실패: 5개" in screen)
    check("크기 불일치 사유가 요약에 보임", any(l.startswith("- size_5_9:") and "3×3" in l for l in screen))

print("\n=== main(): 전체 흐름 ===")
screen = []
code = main(fake_keyboard(["1"] + CROSS_A + X_B + X_B), screen.append)
check("모드 1 종료 코드 0", code == 0)
check("제목 문구 출력", screen[0] == "=== Mini NPU Simulator ===")
check("모드 1 결과 판정 B", "판정: B" in screen)

screen = []
code = main(fake_keyboard(["x", "2"]), screen.append)
check("엉뚱한 선택 뒤 2 -> 모드 2 실행, 종료 코드 0", code == 0 and "총 테스트: 6개" in screen)

screen = []
code = main(fake_keyboard(["2"]), screen.append, os.path.join(HERE, "없는파일.json"))
check("data.json 사용 불가면 종료 코드 1", code == 1 and any("사용할 수 없습니다" in l for l in screen))

for label, error in [("Ctrl+C", KeyboardInterrupt()), ("입력 끊김(EOF)", EOFError())]:
    screen = []
    code = main(interrupting_keyboard(["1", "0 1 0"], error), screen.append)
    check(f"모드 1 입력 도중 {label}: 안내 후 종료 코드 0", code == 0
          and "입력이 중단되어 프로그램을 종료합니다." in screen)
    screen = []
    code = main(interrupting_keyboard([], error), screen.append)
    check(f"모드 선택 중 {label}: 안내 후 종료 코드 0", code == 0
          and "입력이 중단되어 프로그램을 종료합니다." in screen)

print("\n=== 진짜 프로그램 실행 (python main.py, 다른 폴더에서 실행해도 되는지까지) ===")
main_path = os.path.join(HERE, "main.py")


def run_program(stdin_text):
    with tempfile.TemporaryDirectory() as other_folder:
        return subprocess.run([sys.executable, main_path], input=stdin_text, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", cwd=other_folder, timeout=60)

done = run_program("2\n")
check("모드 2: 종료 코드 0, 총 6 / 통과 3 / 실패 3",
      done.returncode == 0 and "총 테스트: 6개" in done.stdout and "통과: 3개" in done.stdout)
done = run_program("1\n" + "\n".join(CROSS_A + X_B + X_B) + "\n")
check("모드 1: 종료 코드 0, 판정 B", done.returncode == 0 and "판정: B" in done.stdout)
done = run_program("")
check("입력이 하나도 없으면(EOF) 안내 후 정상 종료", done.returncode == 0 and "입력이 중단" in done.stdout)

print("\n모든 확인 통과")
