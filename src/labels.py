"""labels.py - 표준 라벨과 라벨 정규화 (요구사항 R4).

프로그램 안에서는 아래 '표준 라벨'만 사용한다.
    Cross     : 십자가
    X         : X 모양
    UNDECIDED : 점수가 비슷해서 결정할 수 없음

data.json 은 같은 뜻을 서로 다른 글자로 적어 둔다.
    expected 값 : '+' (십자가), 'x' (X)
    필터 키     : 'cross' (십자가), 'x' (X)
이것을 비교 전에 표준 라벨로 통일하는 일을 '정규화'라고 한다.
"""

CROSS = "Cross"
X = "X"
UNDECIDED = "UNDECIDED"

# 원래 표기(소문자 기준) -> 표준 라벨
_EXPECTED_TABLE = {"+": CROSS, "x": X}
_FILTER_KEY_TABLE = {"cross": CROSS, "x": X}


def _normalize(raw, table, what):
    """문자열을 다듬고(앞뒤 공백 제거, 소문자) 표에서 찾아 표준 라벨로 바꾼다."""
    if not isinstance(raw, str):
        raise ValueError(f"{what}이(가) 글자가 아닙니다: {raw!r}")
    key = raw.strip().lower()
    if key not in table:
        allowed = ", ".join(repr(k) for k in table)
        raise ValueError(f"알 수 없는 {what}: {raw!r} (허용: {allowed})")
    return table[key]


def normalize_expected(raw):
    """expected 값 정규화: '+' -> Cross, 'x' -> X. 모르는 값은 ValueError."""
    return _normalize(raw, _EXPECTED_TABLE, "expected 값")


def normalize_filter_key(raw):
    """필터 키 정규화: 'cross' -> Cross, 'x' -> X. 모르는 값은 ValueError."""
    return _normalize(raw, _FILTER_KEY_TABLE, "필터 키")
