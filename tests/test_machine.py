from __future__ import annotations

import pytest

from htbapi.machine import MachineInfo


def base_machine_data(machine_id: int = 10) -> dict:
    return {
        "id": machine_id,
        "name": f"Box-{machine_id}",
        "release": "2024-01-01",
        "os": "Linux",
    }


def test_machine_getattr_activity_sorts_by_date_desc(client, stub_http) -> None:
    machine = MachineInfo(_client=client, data=base_machine_data())

    stub_http.add_get(
        f"machine/activity/{machine.id}",
        {
            "info": {
                "activity": [
                    {
                        "user_id": 1,
                        "type": "own",
                        "user_name": "alice",
                        "blood_type": None,
                        "created_at": "2024-01-01T00:00:00Z",
                        "date_diff": "1d",
                        "date": "2024-01-01",
                    },
                    {
                        "user_id": 2,
                        "type": "own",
                        "user_name": "bob",
                        "blood_type": None,
                        "created_at": "2024-01-02T00:00:00Z",
                        "date_diff": "0d",
                        "date": "2024-01-02",
                    },
                ]
            }
        },
    )

    activities = machine.machine_activity

    assert [x.id for x in activities] == [2, 1]


def test_machine_getattr_changelog_sorts_and_maps_types(client, stub_http) -> None:
    machine = MachineInfo(_client=client, data=base_machine_data())

    stub_http.add_get(
        f"machine/changelog/{machine.id}",
        {
            "info": [
                {
                    "id": 5,
                    "user_id": 99,
                    "title": "Fix",
                    "description": "Bugfix",
                    "released": 1,
                    "created_at": "2024-01-02T00:00:00Z",
                    "updated_at": "2024-01-03T00:00:00Z",
                    "type": "3",
                },
                {
                    "id": 4,
                    "user_id": 98,
                    "title": "Update",
                    "description": "Improvement",
                    "released": 1,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-02T00:00:00Z",
                    "type": "2",
                },
            ]
        },
    )

    changelog = machine.changelog

    assert [x.id for x in changelog] == [5, 4]
    assert changelog[0].type == "Bug"
    assert changelog[1].type == "Update"


def test_machine_getattr_missing_activity_returns_empty(client, stub_http) -> None:
    machine = MachineInfo(_client=client, data=base_machine_data())

    stub_http.add_get(f"machine/activity/{machine.id}", {"info": {}})

    assert machine.machine_activity == []


def test_machine_getattr_unknown_attribute_raises(client) -> None:
    machine = MachineInfo(_client=client, data=base_machine_data())

    with pytest.raises(AttributeError):
        _ = machine.unknown_attribute
