"""End-to-end coverage of the exchange request lifecycle and its messaging."""
from app.models.common import RequestStatus


def test_accepting_a_request_opens_a_conversation_and_notifies_the_sender(client, db_session, exchange, auth_headers):
    request = exchange["request"]
    grace_headers = auth_headers(exchange["grace"])

    response = client.patch(f"/api/workspace/requests/{request.id}", json={"status": "ACCEPTED"}, headers=grace_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "ACCEPTED"

    db_session.refresh(request)
    assert request.status == RequestStatus.ACCEPTED
    assert request.conversation is not None

    ada_headers = auth_headers(exchange["ada"])
    notifications = client.get("/api/workspace/notifications", headers=ada_headers).json()
    assert notifications["unread"] == 1
    assert notifications["notifications"][0]["type"] == "REQUEST_ACCEPTED"


def test_sender_cannot_accept_their_own_request(client, exchange, auth_headers):
    response = client.patch(
        f"/api/workspace/requests/{exchange['request'].id}",
        json={"status": "ACCEPTED"},
        headers=auth_headers(exchange["ada"]),
    )
    assert response.status_code == 403


def test_request_cannot_be_decided_twice(client, exchange, auth_headers):
    grace_headers = auth_headers(exchange["grace"])
    url = f"/api/workspace/requests/{exchange['request'].id}"
    assert client.patch(url, json={"status": "ACCEPTED"}, headers=grace_headers).status_code == 200

    response = client.patch(url, json={"status": "REJECTED"}, headers=grace_headers)
    assert response.status_code == 409


def test_sender_can_cancel_a_pending_request(client, exchange, auth_headers):
    response = client.patch(
        f"/api/workspace/requests/{exchange['request'].id}",
        json={"status": "CANCELLED"},
        headers=auth_headers(exchange["ada"]),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_messaging_requires_an_accepted_request(client, exchange, auth_headers):
    response = client.post(
        f"/api/workspace/messages/{exchange['request'].id}",
        json={"body": "Hello!"},
        headers=auth_headers(exchange["ada"]),
    )
    assert response.status_code == 409


def test_message_thread_tracks_unread_until_it_is_opened(client, exchange, auth_headers):
    request_id = exchange["request"].id
    ada_headers = auth_headers(exchange["ada"])
    grace_headers = auth_headers(exchange["grace"])
    client.patch(f"/api/workspace/requests/{request_id}", json={"status": "ACCEPTED"}, headers=grace_headers)

    assert client.post(f"/api/workspace/messages/{request_id}", json={"body": "When shall we start?"}, headers=ada_headers).status_code == 200

    threads = client.get("/api/workspace/messages", headers=grace_headers).json()["threads"]
    assert len(threads) == 1
    assert threads[0]["partner"] == "Ada Lovelace"
    assert threads[0]["unread"] == 1
    assert threads[0]["messages"][0]["is_mine"] is False

    assert client.get("/api/dashboard/summary", headers=grace_headers).json()["unread_messages"] == 1

    read_response = client.post(f"/api/workspace/messages/{request_id}/read", headers=grace_headers)
    assert read_response.json()["marked_read"] == 1
    assert client.get("/api/dashboard/summary", headers=grace_headers).json()["unread_messages"] == 0


def test_outsiders_cannot_read_or_post_to_a_thread(client, db_session, exchange, auth_headers):
    from app.core.security import hash_password
    from app.models import User

    intruder = User(full_name="Alan Turing", username="alan", email="alan@example.com", hashed_password=hash_password("Secret123!"))
    db_session.add(intruder)
    db_session.commit()

    request_id = exchange["request"].id
    client.patch(f"/api/workspace/requests/{request_id}", json={"status": "ACCEPTED"}, headers=auth_headers(exchange["grace"]))

    intruder_headers = auth_headers(intruder)
    assert client.post(f"/api/workspace/messages/{request_id}", json={"body": "hi"}, headers=intruder_headers).status_code == 404
    assert client.get("/api/workspace/messages", headers=intruder_headers).json()["threads"] == []


def test_creating_a_request_notifies_the_receiver(client, exchange, auth_headers):
    response = client.post(
        "/api/requests",
        json={
            "receiver_id": exchange["grace"].id,
            "teaching_skill_id": exchange["python"].id,
            "learning_skill_id": exchange["design"].id,
            "message": "Swap Python for design?",
        },
        headers=auth_headers(exchange["ada"]),
    )
    assert response.status_code == 409, "the fixture already holds an identical pending request"

    grace_headers = auth_headers(exchange["grace"])
    created = client.post(
        "/api/requests",
        json={
            "receiver_id": exchange["ada"].id,
            "teaching_skill_id": exchange["design"].id,
            "learning_skill_id": exchange["python"].id,
            "message": "Happy to swap the other way too.",
        },
        headers=grace_headers,
    )
    assert created.status_code == 201

    notifications = client.get("/api/workspace/notifications", headers=auth_headers(exchange["ada"])).json()
    assert notifications["notifications"][0]["type"] == "NEW_REQUEST"
