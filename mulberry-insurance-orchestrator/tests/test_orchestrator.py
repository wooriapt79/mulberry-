import asyncio
import unittest
from unittest.mock import AsyncMock, patch
import json

# Import classes from the src directory
from src.user import UserA
from src.hospital import HospitalB
from src.insurer import Insurer
from src.mulberry_mind import MulberryMind
from src.orchestrator import InsuranceClaimOrchestrator

class TestInsuranceClaimOrchestrator(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.mock_user = AsyncMock(spec=UserA)
        self.mock_hospital = AsyncMock(spec=HospitalB)
        self.mock_mulberry_mind = AsyncMock(spec=MulberryMind)

        self.mock_hospital.get_medical_records.return_value = [
            "Patient_Name: Jane Doe, DOB: 1980-10-20, Visit_Date: 2024-03-10, Diagnosis: Flu, Treatment: Bed Rest",
        ]
        self.mock_mulberry_mind.distill_gold_data.return_value = {
            "patient_info": {"name": "Jane Doe", "dob": "1980-10-20", "insurance_id": "TEST001"},
            "visit_details": [{
                "visit_date": "2024-03-10",
                "diagnosis_codes": ["Flu"],
                "total_cost": 200.00
            }]
        }
        self.mock_mulberry_mind.check_policy_coverage.return_value = {
            "claim_id": "CLM-2024-03-10-TEST001",
            "status": "Pending Approval",
            "estimated_reimbursement": 100.00
        }

    @patch('src.mulberry_mind.MulberryMind.send_json_to_api', new_callable=AsyncMock)
    @patch('src.user.UserA.confirm_claim', new_callable=AsyncMock)
    async def test_api_submission_success(self, mock_confirm_claim, mock_send_json_to_api):
        mock_confirm_claim.return_value = True
        mock_send_json_to_api.return_value = {"status": "success", "message": "API submitted"}

        api_insurer = Insurer(name='API Test Insurer', has_api=True)
        orchestrator = InsuranceClaimOrchestrator(self.mock_user, self.mock_hospital, api_insurer)

        # Patch MulberryMind methods directly within the test to avoid re-patching in Orchestrator
        with patch('src.orchestrator.MulberryMind', new=self.mock_mulberry_mind):
            result = await orchestrator.collect_and_verify()

        self.assertEqual(orchestrator.status, "SUBMITTED_VIA_API")
        self.assertEqual(result["status"], "success")
        mock_confirm_claim.assert_called_once()
        mock_send_json_to_api.assert_called_once()

    @patch('src.mulberry_mind.MulberryMind.send_auto_fax', new_callable=AsyncMock)
    @patch('src.mulberry_mind.MulberryMind.generate_perfect_pdf', new_callable=AsyncMock)
    @patch('src.user.UserA.confirm_claim', new_callable=AsyncMock)
    async def test_fax_submission_success(self, mock_confirm_claim, mock_generate_pdf, mock_send_auto_fax):
        mock_confirm_claim.return_value = True
        mock_generate_pdf.return_value = "/path/to/test_claim.pdf"
        mock_send_auto_fax.return_value = {"status": "success", "message": "Fax sent"}

        fax_insurer = Insurer(name='Fax Test Insurer', has_api=False)
        orchestrator = InsuranceClaimOrchestrator(self.mock_user, self.mock_hospital, fax_insurer)

        with patch('src.orchestrator.MulberryMind', new=self.mock_mulberry_mind):
            result = await orchestrator.collect_and_verify()

        self.assertEqual(orchestrator.status, "SUBMITTED_VIA_FAX")
        self.assertEqual(result["status"], "success")
        mock_confirm_claim.assert_called_once()
        mock_generate_pdf.assert_called_once()
        mock_send_auto_fax.assert_called_once()

    @patch('src.user.UserA.confirm_claim', new_callable=AsyncMock)
    async def test_claim_rejected_by_user(self, mock_confirm_claim):
        mock_confirm_claim.return_value = False

        api_insurer = Insurer(name='API Test Insurer', has_api=True)
        orchestrator = InsuranceClaimOrchestrator(self.mock_user, self.mock_hospital, api_insurer)

        with patch('src.orchestrator.MulberryMind', new=self.mock_mulberry_mind):
            result = await orchestrator.collect_and_verify()

        self.assertEqual(orchestrator.status, "CLAIM_REJECTED_BY_USER")
        self.assertEqual(result["status"], "cancelled")
        mock_confirm_claim.assert_called_once()

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
