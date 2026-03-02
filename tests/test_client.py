from __future__ import annotations

from typing import Dict, List

import pytest

from htbapi.exception.errors import RequestException, NoPwnBoxActiveException
from htbapi.sherlock import SherlockCategory



def sample_user_profile(user_id: int = 1, name: str = "alice") -> Dict:
    return {
        "id": user_id,
        "name": name,
        "points": 1337,
        "rank": "Hacker",
        "rank_id": 5,
        "rank_requirement": 0,
        "public": True,
    }


def sample_ranking_bracket() -> Dict:
    return {
        "rank": 123,
        "points": 9000,
        "current_bracket": "Hacker",
        "next_bracket": "Pro Hacker",
    }


def sample_badges() -> List[Dict]:
    return [{"id": 7, "pivot": {"created_at": "2024-01-02T03:04:05Z"}}]


def challenge_search_data() -> List[Dict]:
    return [
        {
            "id": 1,
            "name": "Alpha",
            "state": "active",
            "difficulty": "Easy",
            "solves": 10,
            "release_date": "2024-01-01",
            "category_id": 1,
            "rating": 4.0,
            "user_difficulty": 2,
            "is_owned": True,
            "isTodo": False,
        },
        {
            "id": 2,
            "name": "Bravo",
            "state": "retired",
            "difficulty": "Hard",
            "solves": 20,
            "release_date": "2024-02-01",
            "category_id": 2,
            "rating": 3.5,
            "user_difficulty": 3,
            "is_owned": False,
            "isTodo": True,
        },
        {
            "id": 3,
            "name": "Charlie",
            "state": "active",
            "difficulty": "Hard",
            "solves": 5,
            "release_date": "2024-03-01",
            "category_id": 2,
            "rating": 4.5,
            "user_difficulty": 4,
            "is_owned": False,
            "isTodo": False,
        },
    ]


def challenge_list_data() -> List[Dict]:
    return [
        {
            "id": 1,
            "name": "A",
            "retired": False,
            "difficulty": "Easy",
            "solves": 10,
            "release_date": "2024-01-01",
            "challenge_category_id": 1,
            "rating": 4.0,
            "avg_difficulty": 2,
            "authUserSolve": True,
            "isTodo": False,
        },
        {
            "id": 2,
            "name": "B",
            "retired": False,
            "difficulty": "Hard",
            "solves": 5,
            "release_date": "2024-01-02",
            "category_id": 2,
            "rating": 3.0,
            "avg_difficulty": 3,
            "authUserSolve": False,
            "isTodo": True,
        },
    ]


def challenge_unreleased_data() -> List[Dict]:
    return [
        {
            "id": 3,
            "name": "C",
            "retired": False,
            "difficulty": "Hard",
            "solves": 0,
            "release_date": "2024-01-03",
            "category_id": 2,
            "rating": 3.2,
            "avg_difficulty": 3,
            "isTodo": False,
        }
    ]


def pwnbox_data() -> Dict:
    return {
        "id": 1,
        "flock_id": 2,
        "hostname": "pwnbox-1",
        "username": "user",
        "vnc_password": "pass",
        "vnc_view_only_password": "view",
        "status": "running",
        "is_ready": True,
        "location": "EU",
        "proxy_url": "https://proxy",
        "spectate_url": "https://spectate",
        "life_remaining": 123,
        "expires_at": "2024-01-02T00:00:00Z",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T01:00:00Z",
    }


def sherlock_entry(entry_id: int) -> Dict:
    return {
        "id": entry_id,
        "name": f"Sherlock-{entry_id}",
        "difficulty": "Easy",
        "state": "active",
        "category_id": 1,
        "category_name": "Web",
        "solves": 10,
        "is_owned": False,
        "rating": 4.0,
        "rating_count": 5,
        "auth_user_has_reviewed": False,
        "progress": 0.0,
        "release_date": "2024-01-01T00:00:00Z",
        "pinned": False,
    }


def machine_entry(entry_id: int) -> Dict:
    return {
        "id": entry_id,
        "name": f"Box-{entry_id}",
        "release": "2024-01-01",
        "os": "Linux",
    }


def vpn_data() -> Dict:
    return {
        "assigned": {"id": 2, "location_type_friendly": "EU-Assigned"},
        "options": {
            "EU": {
                "free": {
                    "servers": {
                        "2": {
                            "id": 2,
                            "friendly_name": "EU-1",
                            "location": "EU",
                            "full": False,
                            "current_clients": 10,
                        }
                    }
                }
            },
            "US": {
                "free": {
                    "servers": {
                        "3": {
                            "id": 3,
                            "friendly_name": "US-1",
                            "location": "US",
                            "full": False,
                            "current_clients": 5,
                        }
                    }
                }
            },
        },
    }


def test_get_user_by_id_fetches_profile_badges_and_ranking(client, stub_http) -> None:
    user_id = 42
    stub_http.add_get(f"user/profile/basic/{user_id}", {"profile": sample_user_profile(user_id)})
    stub_http.add_get("rankings/user/ranking_bracket", {"data": sample_ranking_bracket()})
    stub_http.add_get(f"user/profile/badges/{user_id}", {"badges": sample_badges()})

    user = client.get_user(user_id=user_id)

    assert user.id == user_id
    assert user.ranking_bracket.current_bracket == "Hacker"
    assert 7 in user.badges
    assert stub_http.endpoints_for("GET") == [
        f"user/profile/basic/{user_id}",
        "rankings/user/ranking_bracket",
        f"user/profile/badges/{user_id}",
    ]


def test_get_user_cache_hit_skips_http_calls(client, stub_http) -> None:
    user_id = 1
    stub_http.add_get(f"user/profile/basic/{user_id}", {"profile": sample_user_profile(user_id)})
    stub_http.add_get("rankings/user/ranking_bracket", {"data": sample_ranking_bracket()})
    stub_http.add_get(f"user/profile/badges/{user_id}", {"badges": []})

    first = client.get_user(user_id=user_id)
    call_count = len(stub_http.calls)
    second = client.get_user(user_id=user_id)

    assert first is second
    assert len(stub_http.calls) == call_count


def test_get_user_by_username_uses_search_and_skips_ranking(client, stub_http) -> None:
    stub_http.add_get('search/fetch?query="alice"', {"users": [{"id": 99}]})
    stub_http.add_get("user/profile/basic/99", {"profile": sample_user_profile(99, "alice")})
    stub_http.add_get("user/profile/badges/99", {"badges": []})

    user = client.get_user(username="alice")

    assert user.id == 99
    assert user.ranking_bracket is None
    assert "rankings/user/ranking_bracket" not in stub_http.endpoints_for("GET")


def test_get_user_returns_none_when_search_empty(client, stub_http) -> None:
    stub_http.add_get('search/fetch?query="ghost"', {})

    assert client.get_user(username="ghost") is None


def test_give_user_respect_posts_endpoint(client, stub_http) -> None:
    stub_http.add_post("user/respect/5", {})

    client.give_user_respect(5)

    assert stub_http.endpoints_for("POST") == ["user/respect/5"]


def test_search_challenges_filters_and_maps(client, stub_http) -> None:
    stub_http.add_get("challenges?keyword=web&sort_type=asc", {"data": challenge_search_data()})

    result = client.search_challenges(
        "web",
        unsolved=True,
        filter_todo=True,
        filter_category_list=[2],
        filter_difficulty="Hard",
    )

    assert len(result) == 1
    assert result[0].id == 2
    assert result[0].retired is True


def test_download_prolab_certificate_writes_pdf_and_adds_extension(client, stub_http, tmp_path) -> None:
    stub_http.add_get("certificate/123/download", b"%PDF-1.4")

    output_path = client.download_prolab_certificate(123, path=str(tmp_path / "cert"))

    assert output_path.endswith(".pdf")
    assert (tmp_path / "cert.pdf").read_bytes() == b"%PDF-1.4"


@pytest.mark.parametrize(
    "message, expected",
    [
        ("unauthorized", "not authorized"),
        ("Not Found", "Certificate not found"),
    ],
)
def test_download_prolab_certificate_handles_errors(client, stub_http, message, expected) -> None:
    stub_http.add_get("certificate/321/download", RequestException({"message": message}))

    with pytest.raises(RequestException) as exc:
        client.download_prolab_certificate(321, path="dummy")

    assert expected in str(exc.value)


def test_get_pwnbox_status_raises_when_message(client, stub_http) -> None:
    stub_http.add_get("pwnbox/status", {"message": "No active pwnbox"})

    with pytest.raises(NoPwnBoxActiveException):
        client.get_pwnbox_status()


def test_get_pwnbox_status_returns_none_when_no_data(client, stub_http) -> None:
    stub_http.add_get("pwnbox/status", None)

    assert client.get_pwnbox_status() is None


def test_get_pwnbox_status_returns_status_object(client, stub_http) -> None:
    stub_http.add_get("pwnbox/status", {"data": pwnbox_data()})

    status = client.get_pwnbox_status()

    assert status.id == 1
    assert status.hostname == "pwnbox-1"


def test_get_challenge_list_merges_unreleased_and_filters(client, stub_http) -> None:
    stub_http.add_get("challenge/list", {"challenges": challenge_list_data()})
    stub_http.add_get("challenges?state=unreleased&sort_type=asc", {"data": challenge_unreleased_data()})

    result = client.get_challenge_list(
        retired=False,
        unsolved=True,
        filter_todo=True,
        filter_category_list=[2],
        filter_difficulty="hard",
    )

    assert [x.id for x in result] == [2]
    assert "challenges?state=unreleased&sort_type=asc" in stub_http.endpoints_for("GET")


def test_get_challenge_list_retired_uses_retired_endpoint(client, stub_http) -> None:
    stub_http.add_get("challenge/list/retired", {"challenges": challenge_list_data()})

    result = client.get_challenge_list(retired=True)

    assert len(result) == 2
    assert "challenge/list/retired" in stub_http.endpoints_for("GET")
    assert "challenges?state=unreleased&sort_type=asc" not in stub_http.endpoints_for("GET")


def test_get_sherlocks_paginates_and_applies_filters(client, stub_http) -> None:
    categories = [
        SherlockCategory(_client=client, data={"id": 1, "name": "Web"}),
        SherlockCategory(_client=client, data={"id": 2, "name": "Forensics"}),
    ]
    endpoint_page1 = "sherlocks?page=1&state=active&category[]=1&category[]=2"
    endpoint_page2 = "sherlocks?page=2&state=active&category[]=1&category[]=2"

    stub_http.add_get(endpoint_page1, {"data": [sherlock_entry(1), sherlock_entry(2)], "meta": {"last_page": 2}})
    stub_http.add_get(endpoint_page2, {"data": [sherlock_entry(3)], "meta": {"last_page": 2}})

    result = client.get_sherlocks(only_active=True, filter_sherlock_category=categories)

    assert [x.id for x in result] == [1, 2, 3]
    assert stub_http.endpoints_for("GET") == [endpoint_page1, endpoint_page2]


def test_get_machine_list_paginates_and_adds_retired_flag(client, stub_http, monkeypatch) -> None:
    monkeypatch.setattr("htbapi.client.time.sleep", lambda *_: None)

    endpoint_page1 = "machine/paginated?per_page=100&page=1&keyword=box&sort_type=asc&os[]=linux&difficulty[]=easy"
    endpoint_page2 = "machine/paginated?per_page=100&page=2&keyword=box&sort_type=asc&os[]=linux&difficulty[]=easy"

    stub_http.add_get(endpoint_page1, {"data": [machine_entry(1), machine_entry(2)], "meta": {"last_page": 2}})
    stub_http.add_get(endpoint_page2, {"data": [machine_entry(3)], "meta": {"last_page": 2}})

    result = client.get_machine_list(
        retired=False,
        keyword="box",
        os_filter=["linux"],
        difficulty_filter=["easy"],
        sort_type="asc",
    )

    assert len(result) == 3
    assert all(machine.retired is False for machine in result)
    assert stub_http.endpoints_for("GET") == [endpoint_page1, endpoint_page2]


def test_get_machine_list_limit_short_circuits(client, stub_http, monkeypatch) -> None:
    monkeypatch.setattr("htbapi.client.time.sleep", lambda *_: None)

    endpoint_page1 = "machine/paginated?per_page=100&page=1&keyword=box&sort_type=asc"
    stub_http.add_get(endpoint_page1, {"data": [machine_entry(1), machine_entry(2)], "meta": {"last_page": 5}})

    result = client.get_machine_list(keyword="box", limit=1, sort_type="asc")

    assert len(result) == 1
    assert stub_http.endpoints_for("GET") == [endpoint_page1]


def test_get_machine_list_invalid_filters_raise(client) -> None:
    with pytest.raises(AssertionError):
        client.get_machine_list(os_filter=["mac"])


def test_get_all_vpn_server_uses_cache_and_location_filter(client, stub_http) -> None:
    stub_http.add_get("connections/servers?product=labs", {"data": vpn_data()})

    first = client.get_all_vpn_server(products=["labs"], vpn_location="EU")
    call_count = len(stub_http.calls)
    second = client.get_all_vpn_server(products=["labs"], vpn_location="EU")

    assert list(first.keys()) == [2]
    assert first[2].is_assigned is True
    assert first[2].product == "labs"
    assert len(stub_http.calls) == call_count
    assert list(second.keys()) == [2]
