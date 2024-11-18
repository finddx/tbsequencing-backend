from time import sleep

import pytest
from pytest_mock import MockerFixture
from rest_framework.exceptions import PermissionDenied

from submission.models import Package
from submission.services.matching import MatchingService


@pytest.mark.django_db(transaction=True)
def test_package_being_locked_while_matching(
    package_of,
    alice,
    countries,
    mocker: MockerFixture,
    start_race,
):  # pylint: disable=unused-argument
    """
    When one thread is working on a package, no other threads can work on it.

    The test make use of database transactions.
    """
    package = package_of(alice)

    # make our match procedure to take "forever" to complete
    MatchingService.perform_match = mocker.MagicMock(
        side_effect=lambda *args, **kwargs: sleep(0.1),
    )

    # increment for every thread, decrement for every thread that got permission error
    # we should have 1 at the end of the test
    package_locked_cnt = 0

    def perform_match():
        nonlocal package_locked_cnt
        package_locked_cnt += 1

        try:
            MatchingService.execute(dict(package=package))
        except PermissionDenied as exc:
            assert str(exc) == "Package is already being processed"
            package_locked_cnt -= 1

    start_race(threads_num=3, target=perform_match)

    assert package_locked_cnt == 1


def test_package_marked_changed_after_matched(package_of, new_alias_of, alice):
    """Package marked as changed if it was matched before."""
    package = package_of(alice)
    new_alias_of(package, name="A1")
    MatchingService.execute(dict(package=package))
    assert package.matching_state == package.MatchingState.MATCHED

    package.mark_changed()

    assert package.matching_state == package.MatchingState.CHANGED


def test_package_goes_draft_when_changed_after_rejected(package_of, alice):
    """Package goes back to draft when it was changed after reject."""
    package = package_of(alice)
    package.state = package.State.REJECTED
    package.save()

    package.mark_changed()

    assert package.state == package.State.DRAFT


def test_rejection_reason_saved_on_reject(package_of, alice, new_alias_of):
    """Rejection reason saved in package data."""
    package = package_of(alice)
    new_alias_of(package, "A1")
    MatchingService.execute(dict(package=package))
    package.to_pending()

    package.pending_to_rejected("ugly")

    assert package.rejection_reason == "ugly"


# pylint: disable=unused-argument
def test_data_unstaged_on_accept(alice_package, drugs, countries):
    """Tests are marked unstaged after package accepted."""
    pds_test = alice_package.new_pds_test(result="I", drug=drugs[0], staging=True)
    mic_test = alice_package.new_mic_test(drug=drugs[0], staging=True)
    package = alice_package.package
    MatchingService.execute(dict(package=package))
    package.to_pending()

    package.pending_to_accepted()

    pds_test.refresh_from_db()
    assert not pds_test.staging

    mic_test.refresh_from_db()
    assert not mic_test.staging


def test_other_user_packages_changed_on_accept(new_package_of, alice):
    """Other user packages reset their matching state to CHANGED, when package accepted."""
    package1 = new_package_of(alice)
    package2 = new_package_of(alice, state=Package.State.REJECTED)
    package3 = new_package_of(alice)

    # put package1 and package2 in MATCHED state
    package1.matching_state = Package.MatchingState.MATCHED
    package1.save()
    package2.matching_state = Package.MatchingState.MATCHED
    package2.save()

    # accept package3
    package3.matching_state = Package.MatchingState.MATCHED
    package3.to_pending()
    package3.pending_to_accepted()

    package1.refresh_from_db()
    assert package1.matching_state == Package.MatchingState.CHANGED
    package2.refresh_from_db()
    assert package2.matching_state == Package.MatchingState.CHANGED
