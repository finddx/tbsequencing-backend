from rest_framework.reverse import reverse

from submission.models import Message


def test_send_message(client_of, package_of, alice):
    """Message is created, sender is current user."""
    endpoint = reverse("v1:submission:message-list", (package_of(alice).pk,))
    response = client_of(alice).post(
        endpoint,
        data={"content": "hey"},
    )

    data = response.json()
    message = Message.objects.get(pk=data["pk"])

    assert message.sender == alice
    assert message.package == package_of(alice)
    assert message.content == "hey"


def test_send_message_to_alien_package_forbidden(client_of, package_of, john, alice):
    """Cannot create message for another's package."""
    endpoint = reverse("v1:submission:message-list", (package_of(alice).pk,))

    response = client_of(john).post(
        endpoint,
        data={"content": "why"},
    )

    assert response.status_code == 403
    assert not package_of(alice).messages.filter(sender=john).exists()


def test_get_message_history(client_of, package_of, alice, admin):
    """Can see all created messages by the package."""
    for user in [alice, admin, alice, admin]:
        Message.objects.create(
            sender=user,
            content="no you first",
            package=package_of(alice),
        )
    endpoint = reverse("v1:submission:message-list", (package_of(alice).pk,))

    response = client_of(alice).get(endpoint)
    assert response.status_code == 200
    assert len(response.json()) == package_of(alice).messages.count()


def test_cant_get_alien_package_message_history(client_of, package_of, alice, john):
    """Cannot get history of alien package messages."""
    endpoint = reverse("v1:submission:message-list", (package_of(alice).pk,))
    response = client_of(john).get(endpoint)
    assert response.status_code == 403
