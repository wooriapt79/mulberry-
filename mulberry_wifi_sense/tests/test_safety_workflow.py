import unittest

from safety_workflow import ApprovalState, ConsentState, SafetyWorkflow


class SafetyWorkflowTest(unittest.TestCase):
    def test_candidate_requires_granted_consent(self):
        workflow = SafetyWorkflow()
        with self.assertRaises(PermissionError):
            workflow.create_candidate("fall_suspected", 0.97, "lab-a")

    def test_score_is_explicitly_not_a_probability(self):
        workflow = SafetyWorkflow()
        workflow.set_consent(ConsentState.GRANTED, "resident-1", "research session")
        candidate = workflow.create_candidate("fall_suspected", 0.97, "lab-a")
        self.assertFalse(candidate.score_is_calibrated_probability)
        self.assertEqual(candidate.approval_state, ApprovalState.PENDING)

    def test_dispatch_simulation_requires_human_approval(self):
        workflow = SafetyWorkflow()
        workflow.set_consent(ConsentState.GRANTED, "resident-1", "research session")
        candidate = workflow.create_candidate("fall_suspected", 0.97, "lab-a")
        dispatched = []
        workflow.decide(candidate.event_id, True, "steward-human-1", "visual check", dispatched.append)
        self.assertEqual(dispatched[0].event_id, candidate.event_id)
        self.assertEqual(
            [record.action for record in workflow.audit_log][-2:],
            ["candidate.approved", "dispatch.simulated"],
        )

    def test_rejected_candidate_cannot_dispatch_or_be_decided_twice(self):
        workflow = SafetyWorkflow()
        workflow.set_consent(ConsentState.GRANTED, "resident-1", "research session")
        candidate = workflow.create_candidate("fall_suspected", 0.97, "lab-a")
        dispatched = []
        workflow.decide(candidate.event_id, False, "steward-human-1", "false positive", dispatched.append)
        self.assertEqual(dispatched, [])
        with self.assertRaises(RuntimeError):
            workflow.decide(candidate.event_id, True, "steward-human-1", "retry", dispatched.append)


if __name__ == "__main__":
    unittest.main()
