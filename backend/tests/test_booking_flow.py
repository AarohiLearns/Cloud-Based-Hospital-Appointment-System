from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from tests.conftest import API


def tomorrow() -> str:
    return (datetime.now(ZoneInfo("Asia/Kolkata")) + timedelta(days=1)).date().isoformat()


async def setup_doctor(client, admin_headers) -> str:
    r = await client.post(f"{API}/doctors", headers=admin_headers, json={
        "full_name": "Dr. Asha Rao", "specialization": "Cardiology", "slot_minutes": 30})
    assert r.status_code == 201, r.text
    doctor_id = r.json()["id"]
    entries = [{"weekday": d, "start_time": "09:00:00", "end_time": "12:00:00"} for d in range(7)]
    r = await client.put(f"{API}/doctors/{doctor_id}/schedule", headers=admin_headers,
                         json={"entries": entries})
    assert r.status_code == 200, r.text
    return doctor_id


async def slots(client, doctor_id) -> list[dict]:
    r = await client.get(f"{API}/doctors/{doctor_id}/availability", params={"date": tomorrow()})
    assert r.status_code == 200, r.text
    return r.json()["slots"]


async def test_full_booking_flow(client, admin_headers, make_patient):
    doctor_id = await setup_doctor(client, admin_headers)
    alice = await make_patient("alice@test.com")
    bob = await make_patient("bob@test.com")

    free = await slots(client, doctor_id)
    assert len(free) == 6

    body = {"doctor_id": doctor_id, "start_time": free[0]["start_time"], "reason": "Checkup"}
    r = await client.post(f"{API}/appointments", headers=alice, json=body)
    assert r.status_code == 201, r.text
    appt_id = r.json()["id"]
    assert len(await slots(client, doctor_id)) == 5

    # Same slot, different patient -> conflict
    r = await client.post(f"{API}/appointments", headers=bob, json=body)
    assert r.status_code == 409

    # Another patient cannot cancel it
    r = await client.post(f"{API}/appointments/{appt_id}/cancel", headers=bob)
    assert r.status_code == 403

    # Owner cancels, slot becomes free again and can be re-booked
    r = await client.post(f"{API}/appointments/{appt_id}/cancel", headers=alice)
    assert r.status_code == 200 and r.json()["status"] == "cancelled"
    assert len(await slots(client, doctor_id)) == 6
    r = await client.post(f"{API}/appointments", headers=bob, json=body)
    assert r.status_code == 201

    mine = await client.get(f"{API}/appointments/me", headers=bob)
    assert len(mine.json()) == 1


async def test_booking_requires_auth_and_valid_slot(client, admin_headers, make_patient):
    doctor_id = await setup_doctor(client, admin_headers)
    alice = await make_patient("alice@test.com")
    free = await slots(client, doctor_id)

    body = {"doctor_id": doctor_id, "start_time": free[0]["start_time"]}
    assert (await client.post(f"{API}/appointments", json=body)).status_code == 401

    # A time that is not on the slot grid
    bad = datetime.fromisoformat(free[0]["start_time"].replace("Z", "+00:00")) + timedelta(minutes=7)
    r = await client.post(f"{API}/appointments", headers=alice,
                          json={"doctor_id": doctor_id, "start_time": bad.isoformat()})
    assert r.status_code == 409


async def test_only_admin_can_create_doctor(client, make_patient):
    alice = await make_patient("alice@test.com")
    r = await client.post(f"{API}/doctors", headers=alice, json={
        "full_name": "Dr X", "specialization": "ENT"})
    assert r.status_code == 403
