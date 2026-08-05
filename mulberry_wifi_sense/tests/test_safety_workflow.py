import unittest
from datetime import datetime, timedelta, timezone

from safety_workflow import ApprovalState, ConsentState, SafetyWorkflow, StewardAuthorizer


class MutableClock:
    def __init__(self):
        self.now = datetime(2026, 8, 5, tzinfo=timezone.utc)

    def __call__(self):
        return self.now


class SafetyWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.clock = MutableClock()
        self.workflow = SafetyWorkflow(
            StewardAuthorizer({"steward-human-1": "test-credential"}),
            clock=self.clock,
        )

    def grant_consent(self):
        self.workflow.set_consent(
            ConsentState.GRANTED,
            "resident-1",
            "research session",
            valid_for=timedelta(minutes=30),
        )

    def test_candidate_requires_granted_consent(self):
        with self.assertRaises(PermissionError):
            self.workflow.create_candidate("fall_suspected", 0.97, "lab-a")

    def test_score_is_explicitly_not_a_probability(self):
        self.grant_consent()
        candidate = self.workflow.create_candidate("fall_suspected", 0.97, "lab-a")
        self.assertFalse(candidate.score_is_calibrated_probability)
        self.assertEqual(candidate.approval_state, ApprovalState.PENDING)

    def test_expired_consent_is_automatic_and_blocks_candidate(self):
        self.grant_consent()
        self.clock.now += timedelta(minutes=30)
        with self.assertRaises(PermissionError):
            self.workflow.create_candidate("fall_suspected", 0.97, "lab-a")
        self.assertEqual(self.workflow.consent_state, ConsentState.EXPIRED)
        self.assertEqual(self.workflow.audit_log[-1].action, "consent.expired")

    def test_unregistered_or_invalid_steward_cannot_decide(self):
        self.grant_consent()
        candidate = self.workflow.create_candidate("fall_suspected", 0.97, "lab-a")
        for actor, credential in (("unknown", "x"), ("steward-human-1", "wrong")):
            with self.assertRaises(PermissionError):
                self.workflow.decide(candidate.event_id, True, actor, credential, "visual check")
        self.assertEqual(
            self.workflow.candidates[candidate.event_id].approval_state,
            ApprovalState.PENDING,
        )

    def test_dispatch_simulation_requires_authenticated_human_approval(self):
        self.grant_consent()
        candidate = self.workflow.create_candidate("fall_suspected", 0.97, "lab-a")
        dispatched = []
        self.workflow.decide(
            candidate.event_id,
            True,
            "steward-human-1",
            "test-credential",
            "visual check",
            dispatched.append,
        )
        self.assertEqual(dispatched[0].event_id, candidate.event_id)
        self.assertEqual(
            [record.action for record in self.workflow.audit_log][-2:],
            ["candidate.approved", "dispatch.simulated"],
        )

    def test_rejected_candidate_cannot_dispatch_or_be_decided_twice(self):
        self.grant_consent()
        candidate = self.workflow.create_candidate("fall_suspected", 0.97, "lab-a")
        dispatched = []
        self.workflow.decide(
            candidate.event_id,
            False,
            "steward-human-1",
            "test-credential",
            "false positive",
            dispatched.append,
        )
        self.assertEqual(dispatched, [])
        with self.assertRaises(RuntimeError):
            self.workflow.decide(
                candidate.event_id,
                True,
                "steward-human-1",
                "test-credential",
                "retry",
                dispatched.append,
            )


if __name__ == "__main__":
    unittest.main()
