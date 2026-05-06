# tests/test_job_service.py
import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from src.service.job_service import AssignJobService, JobNotFoundError, PermissionDeniedError, TechnicianNotAvailableError
from src.domain.repair_job import RepairJob, Technician, StatusEnum, AvailabilityEnum


@pytest.fixture
def mock_job_repo():
    return MagicMock()


@pytest.fixture
def mock_tech_repo():
    return MagicMock()


@pytest.fixture
def mock_notifier():
    return MagicMock()


@pytest.fixture
def service(mock_job_repo, mock_tech_repo, mock_notifier):
    return AssignJobService(
        job_repo=mock_job_repo,
        tech_repo=mock_tech_repo,
        notifier=mock_notifier,
    )


@pytest.fixture
def available_technician():
    return Technician(
        id=uuid4(),
        name="Alex Chen",
        email="alex@fieldco.com",
        availability=AvailabilityEnum.AVAILABLE,
    )


@pytest.fixture
def unassigned_job():
    return RepairJob(
        id=uuid4(),
        site_address="123 Main St",
        fault_description="Power outage",
        priority="high",
        status=StatusEnum.UNASSIGNED,
    )


class TestAssignJob:
    def test_assigns_job_to_available_technician(
        self, service, mock_job_repo, mock_tech_repo,
        unassigned_job, available_technician
    ) -> None:
        mock_job_repo.find_by_id.return_value = unassigned_job
        mock_tech_repo.find_by_email.return_value = available_technician

        result = service.assign(job_id=unassigned_job.id, assignee_email="alex@fieldco.com")

        assert result.status == StatusEnum.ASSIGNED
        assert result.assignee_id == available_technician.id
        mock_job_repo.update_assignee.assert_called_once_with(
            unassigned_job.id, available_technician.id
        )

    def test_sends_notification_on_successful_assignment(
        self, service, mock_job_repo, mock_tech_repo, mock_notifier,
        unassigned_job, available_technician
    ) -> None:
        mock_job_repo.find_by_id.return_value = unassigned_job
        mock_tech_repo.find_by_email.return_value = available_technician

        service.assign(job_id=unassigned_job.id, assignee_email="alex@fieldco.com")

        mock_notifier.send.assert_called_once_with(
            recipient="alex@fieldco.com",
            message=f"You have been assigned job {unassigned_job.id}",
        )

    def test_raises_job_not_found_when_job_does_not_exist(
        self, service, mock_job_repo
    ) -> None:
        mock_job_repo.find_by_id.return_value = None

        with pytest.raises(JobNotFoundError):
            service.assign(job_id=uuid4(), assignee_email="alex@fieldco.com")

    def test_does_not_send_notification_when_job_not_found(
        self, service, mock_job_repo, mock_notifier
    ) -> None:
        mock_job_repo.find_by_id.return_value = None

        with pytest.raises(JobNotFoundError):
            service.assign(job_id=uuid4(), assignee_email="alex@fieldco.com")

        mock_notifier.send.assert_not_called()

    def test_raises_permission_denied_when_caller_is_not_a_manager(
        self, service
    ) -> None:
        with pytest.raises(PermissionDeniedError):
            service.assign(
                job_id=uuid4(),
                assignee_email="alex@fieldco.com",
                caller_role="technician",
            )

    def test_raises_technician_not_available_when_technician_not_found(
        self, service, mock_job_repo, mock_tech_repo, unassigned_job
    ) -> None:
        mock_job_repo.find_by_id.return_value = unassigned_job
        mock_tech_repo.find_by_email.return_value = None

        with pytest.raises(TechnicianNotAvailableError):
            service.assign(job_id=unassigned_job.id, assignee_email="unknown@fieldco.com")

    def test_raises_technician_not_available_when_on_leave(
        self, service, mock_job_repo, mock_tech_repo, unassigned_job
    ) -> None:
        on_leave_tech = Technician(
            id=uuid4(),
            name="Sam Rivera",
            email="sam@fieldco.com",
            availability=AvailabilityEnum.ON_LEAVE,
        )
        mock_job_repo.find_by_id.return_value = unassigned_job
        mock_tech_repo.find_by_email.return_value = on_leave_tech

        with pytest.raises(TechnicianNotAvailableError):
            service.assign(job_id=unassigned_job.id, assignee_email="sam@fieldco.com")

    def test_does_not_send_notification_when_technician_not_available(
        self, service, mock_job_repo, mock_tech_repo, mock_notifier, unassigned_job
    ) -> None:
        on_leave_tech = Technician(
            id=uuid4(),
            name="Sam Rivera",
            email="sam@fieldco.com",
            availability=AvailabilityEnum.ON_LEAVE,
        )
        mock_job_repo.find_by_id.return_value = unassigned_job
        mock_tech_repo.find_by_email.return_value = on_leave_tech

        with pytest.raises(TechnicianNotAvailableError):
            service.assign(job_id=unassigned_job.id, assignee_email="sam@fieldco.com")

        mock_notifier.send.assert_not_called()
