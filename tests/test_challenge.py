from __future__ import annotations

import hashlib

import pytest

from htbapi.challenge import ChallengeList
from htbapi.exception.errors import RequestException


def make_challenge(client, challenge_id: int = 10, name: str = "Web 101") -> ChallengeList:
    data = {
        "id": challenge_id,
        "name": name,
        "retired": False,
        "difficulty": "Easy",
        "solves": 1,
        "release_date": "2024-01-01",
        "challenge_category_id": 1,
        "rating": 4.0,
        "avg_difficulty": 2,
        "authUserSolve": False,
        "isTodo": False,
    }
    return ChallengeList(_client=client, data=data)


def test_challenge_download_writes_zip(client, stub_http, tmp_path) -> None:
    challenge = make_challenge(client, name="My Challenge")
    stub_http.add_get(f"challenge/download/{challenge.id}", b"ZIPDATA")

    target_dir = tmp_path / "dl"
    output_path = challenge.download(path=str(target_dir))

    assert output_path.endswith("My_Challenge.zip")
    assert (target_dir / "My_Challenge.zip").read_bytes() == b"ZIPDATA"


@pytest.mark.parametrize(
    "message, expected",
    [
        ("unauthorized", "not authorized"),
        ("Not Found", "Certificate not found"),
    ],
)
def test_challenge_download_maps_errors(client, stub_http, message, expected) -> None:
    challenge = make_challenge(client)
    stub_http.add_get(
        f"challenge/download/{challenge.id}",
        RequestException({"message": message}),
    )

    with pytest.raises(RequestException) as exc:
        challenge.download(path="/tmp")

    assert expected in str(exc.value)


def test_challenge_download_writeup_success_and_hash_validation(client, stub_http, tmp_path) -> None:
    challenge = make_challenge(client, name="Forensics 1")
    file_bytes = b"WRITEUP"
    sha256 = hashlib.sha256(file_bytes).hexdigest()

    stub_http.add_get(
        f"challenge/{challenge.id}/writeup",
        {
            "data": {
                "official": {
                    "url": "https://example.invalid/writeup",
                    "filename": "writeup.pdf",
                    "sha256": sha256,
                }
            }
        },
    )
    stub_http.add_get("https://example.invalid/writeup", file_bytes)

    output_path = challenge.download_writeup(path=str(tmp_path / "reports"))

    assert output_path.endswith("writeup.pdf")
    assert (tmp_path / "reports" / "writeup.pdf").read_bytes() == file_bytes


def test_challenge_download_writeup_missing_official_raises(client, stub_http) -> None:
    challenge = make_challenge(client)
    stub_http.add_get(f"challenge/{challenge.id}/writeup", {"data": {}})

    with pytest.raises(RequestException):
        challenge.download_writeup(path="/tmp")


def test_challenge_download_writeup_hash_mismatch_raises(client, stub_http) -> None:
    challenge = make_challenge(client)
    stub_http.add_get(
        f"challenge/{challenge.id}/writeup",
        {
            "data": {
                "official": {
                    "url": "https://example.invalid/writeup",
                    "filename": "writeup.pdf",
                    "sha256": "deadbeef",
                }
            }
        },
    )
    stub_http.add_get("https://example.invalid/writeup", b"BAD")

    with pytest.raises(RequestException) as exc:
        challenge.download_writeup(path="/tmp")

    assert "Hash mismatch" in str(exc.value)


def test_challenge_download_writeup_maps_unauthorized(client, stub_http) -> None:
    challenge = make_challenge(client)
    stub_http.add_get(
        f"challenge/{challenge.id}/writeup",
        {
            "data": {
                "official": {
                    "url": "https://example.invalid/writeup",
                    "filename": "writeup.pdf",
                    "sha256": "deadbeef",
                }
            }
        },
    )
    stub_http.add_get(
        "https://example.invalid/writeup",
        RequestException({"message": "unauthorized"}),
    )

    with pytest.raises(RequestException) as exc:
        challenge.download_writeup(path="/tmp")

    assert "not authorized" in str(exc.value)
