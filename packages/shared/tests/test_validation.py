from __future__ import annotations

import pytest

from jejueo_shared import ApiError, parse_request_json, validate_translation_request


def test_parse_request_json_rejects_non_object() -> None:
    with pytest.raises(ApiError) as excinfo:
        parse_request_json(b'["not-an-object"]')

    assert excinfo.value.status_code == 400
    assert excinfo.value.error == "invalid_input"


def test_validate_translation_request_accepts_bidirectional_pairs() -> None:
    request = validate_translation_request(
        {
            "sourceText": "대한민국은 사계절이 뚜렷합니다.",
            "sourceLang": "ko",
            "targetLang": "ko-jeju",
        }
    )

    assert request.sourceLang == "ko"
    assert request.targetLang == "ko-jeju"


def test_validate_translation_request_rejects_same_language_pair() -> None:
    with pytest.raises(ApiError) as excinfo:
        validate_translation_request(
            {
                "sourceText": "안녕하세요",
                "sourceLang": "ko",
                "targetLang": "ko",
            }
        )

    assert excinfo.value.status_code == 400
    assert excinfo.value.error == "invalid_input"


def test_validate_translation_request_rejects_whitespace_input() -> None:
    with pytest.raises(ApiError) as excinfo:
        validate_translation_request(
            {
                "sourceText": "   \n  ",
                "sourceLang": "ko",
                "targetLang": "ko-jeju",
            }
        )

    assert excinfo.value.status_code == 400
    assert excinfo.value.error == "invalid_input"


def test_validate_translation_request_rejects_oversized_input() -> None:
    with pytest.raises(ApiError) as excinfo:
        validate_translation_request(
            {
                "sourceText": "가" * 501,
                "sourceLang": "ko",
                "targetLang": "ko-jeju",
            }
        )

    assert excinfo.value.status_code == 413
    assert excinfo.value.error == "input_too_long"
