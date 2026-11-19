"""data_loader.py - data.json 읽기와 검증 (요구사항 R3).

이 파일이 하는 일
  1) 파일을 읽는다 (없거나 비었거나 깨졌으면 친절한 안내와 함께 DataFileError)
  2) 필터(size_5, size_13, size_25)를 읽고 라벨을 표준화한다
  3) 패턴 한 개(케이스)를 검사한다 (키에서 크기 추출, 크기 일치, expected 정규화)

중요 원칙: '파일 전체' 문제는 DataFileError 로 알리고,
          '케이스 하나' 문제는 CaseError 로 알려서 그 케이스만 FAIL 처리한다.
          (케이스 하나가 이상하다고 프로그램 전체가 멈추면 안 된다)
"""

import json
import os
import re

from src.labels import CROSS, X, normalize_expected, normalize_filter_key
from src.matrix import is_square_matrix

# data.json 의 기본 위치: 프로젝트 폴더(= src 폴더의 바로 윗 폴더) 안
DEFAULT_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data.json"
)

# 케이스 실패 종류 (README 실패 원인 분석에서 쓸 분류)
KIND_SCHEMA = "SCHEMA"                # 데이터/스키마 문제 (항목 없음, 형식 오류, 모르는 라벨 등)
KIND_SIZE_MISMATCH = "SIZE_MISMATCH"  # 필터와 패턴의 크기 불일치

# 숫자 앞에 0이 오는 'size_05' 같은 키는 인정하지 않는다
_PATTERN_KEY = re.compile(r"^size_([1-9]\d*)_(\d+)$")
_FILTER_KEY = re.compile(r"^size_([1-9]\d*)$")


class DataFileError(Exception):
    """data.json 파일 전체를 쓸 수 없을 때."""


class CaseError(Exception):
    """패턴 케이스 하나가 이상할 때. kind(실패 종류)와 message(사유)를 가진다."""

    def __init__(self, kind, message):
        super().__init__(message)
        self.kind = kind
        self.message = message


# ---------------------------------------------------------------- 파일 읽기
def load_json(path=DEFAULT_DATA_PATH):
    """data.json 을 읽어 dict 로 돌려준다. 문제가 있으면 DataFileError."""
    try:
        # utf-8-sig: 윈도우 메모장이 붙이는 BOM(눈에 안 보이는 표식)이 있어도 읽힌다
        with open(path, encoding="utf-8-sig") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise DataFileError(f"파일을 찾을 수 없습니다: {path}") from None
    except json.JSONDecodeError as e:
        raise DataFileError(
            f"JSON 형식 오류 ({e.lineno}줄 {e.colno}열, {e.msg}): "
            "파일이 비어 있거나 내용이 깨지지 않았는지 확인하세요."
        ) from None
    except UnicodeDecodeError:
        raise DataFileError("파일 글자 인코딩을 읽을 수 없습니다. UTF-8 로 저장했는지 확인하세요.") from None
    except OSError as e:
        raise DataFileError(f"파일을 읽을 수 없습니다: {e}") from None

    if not isinstance(data, dict):
        raise DataFileError("data.json 의 최상위가 객체({ ... })가 아닙니다.")
    for part in ("filters", "patterns"):
        if not isinstance(data.get(part), dict):
            raise DataFileError(f"data.json 에 '{part}' 항목(객체)이 없습니다.")
    return data


# ---------------------------------------------------------------- 키에서 크기 뽑기
def extract_size(key):
    """패턴 키 'size_13_2' 에서 크기 13 을 뽑는다. 형식이 틀리면 ValueError."""
    match = _PATTERN_KEY.match(key) if isinstance(key, str) else None
    if match is None:
        raise ValueError(f"패턴 키 형식 오류: {key!r} (예: size_5_1)")
    return int(match.group(1))


def extract_filter_size(key):
    """필터 키 'size_13' 에서 크기 13 을 뽑는다. 형식이 틀리면 ValueError."""
    match = _FILTER_KEY.match(key) if isinstance(key, str) else None
    if match is None:
        raise ValueError(f"필터 키 형식 오류: {key!r} (예: size_5)")
    return int(match.group(1))


# ---------------------------------------------------------------- 필터 읽기
def _parse_filter_pair(n, pair):
    """size_n 필터 묶음 하나를 검사해서 {Cross: 행렬, X: 행렬} 로 돌려준다."""
    if not isinstance(pair, dict):
        raise ValueError("필터 묶음이 객체({ ... })가 아닙니다.")

    built = {}
    for raw_key, matrix in pair.items():
        label = normalize_filter_key(raw_key)          # 모르는 키면 ValueError
        if label in built:
            raise ValueError(f"같은 라벨({label})의 필터가 두 번 들어 있습니다.")
        if not is_square_matrix(matrix):
            raise ValueError(f"'{raw_key}' 필터가 N×N 숫자 배열이 아닙니다.")
        if len(matrix) != n:
            raise ValueError(
                f"'{raw_key}' 필터 크기가 {len(matrix)}×{len(matrix)} 입니다 (기대: {n}×{n})."
            )
        built[label] = matrix

    missing = [label for label in (CROSS, X) if label not in built]
    if missing:
        raise ValueError(f"필터가 없습니다: {', '.join(missing)}")
    return built


def load_filters(data):
    """모든 필터를 읽는다.

    돌려주는 값: (filters, filter_errors)
      filters       : {5: {"Cross": 행렬, "X": 행렬}, 13: {...}, ...}   (정상인 것만)
      filter_errors : {"size_13": "사유", ...}                            (문제 있는 것)
    문제 있는 필터가 있어도 멈추지 않는다. 그 크기의 패턴만 나중에 FAIL 처리된다.
    """
    filters = {}
    filter_errors = {}
    for size_key, pair in data["filters"].items():
        try:
            n = extract_filter_size(size_key)
            filters[n] = _parse_filter_pair(n, pair)
        except ValueError as error:
            filter_errors[size_key] = str(error)
    return filters, filter_errors


# ---------------------------------------------------------------- 케이스 검사
def validate_case(key, case, filters, filter_errors):
    """패턴 케이스 하나를 검사한다.

    정상이면 (패턴, 필터묶음, 표준 expected) 를 돌려준다.
    문제가 있으면 CaseError(kind, message) 를 일으킨다.
    """
    try:
        n = extract_size(key)
    except ValueError as error:
        raise CaseError(KIND_SCHEMA, str(error)) from None

    if not isinstance(case, dict) or "input" not in case or "expected" not in case:
        raise CaseError(KIND_SCHEMA, "'input' 또는 'expected' 항목이 없습니다.")

    pattern = case["input"]
    if not is_square_matrix(pattern):
        raise CaseError(KIND_SCHEMA, "'input' 이 N×N 숫자 배열이 아닙니다.")

    try:
        expected = normalize_expected(case["expected"])
    except ValueError as error:
        raise CaseError(KIND_SCHEMA, str(error)) from None

    filter_key = f"size_{n}"
    if filter_key in filter_errors:
        raise CaseError(KIND_SCHEMA, f"필터 {filter_key} 오류: {filter_errors[filter_key]}")
    if n not in filters:
        raise CaseError(KIND_SCHEMA, f"data.json 에 {filter_key} 필터가 없습니다.")

    size = len(pattern)
    if size != n:
        raise CaseError(
            KIND_SIZE_MISMATCH,
            f"키는 {filter_key} 이므로 {n}×{n} 이어야 하는데 패턴은 {size}×{size} 입니다.",
        )
    return pattern, filters[n], expected
