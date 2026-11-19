"""main.py - Mini NPU 시뮬레이터 실행 파일.

실행 방법:  python main.py
"""

import sys

from src.data_loader import DEFAULT_DATA_PATH
from src.modes import choose_mode, run_json_mode, run_user_mode


def configure_console():
    """화면 출력 글자를 UTF-8 로 맞춘다. (✓, × 같은 글자가 일부 환경에서 오류를 내는 것을 막는다)"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def main(input_func=input, output_func=print, data_path=DEFAULT_DATA_PATH):
    """프로그램 전체 흐름. 종료 코드(0: 정상, 1: data.json 사용 불가)를 돌려준다."""
    output_func("=== Mini NPU Simulator ===")
    output_func("")
    try:
        mode = choose_mode(input_func, output_func)
        output_func("")
        if mode == 1:
            run_user_mode(input_func, output_func)
            return 0
        return 0 if run_json_mode(output_func, data_path) else 1
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C 를 누르거나 입력이 끊긴 경우: 어려운 오류 화면 대신 안내만 하고 끝낸다
        output_func("")
        output_func("입력이 중단되어 프로그램을 종료합니다.")
        return 0


if __name__ == "__main__":
    configure_console()
    sys.exit(main())
