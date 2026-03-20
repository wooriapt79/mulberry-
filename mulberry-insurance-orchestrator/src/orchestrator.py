from src.user import UserA
from src.hospital import HospitalB
from src.insurer import Insurer
from src.mulberry_mind import MulberryMind
import asyncio

class InsuranceClaimOrchestrator:
    def __init__(self, user_a: UserA, hospital_b: HospitalB, insurer: Insurer):
        self.user = user_a        # Main: 사고 당사자
        self.hospital = hospital_b # Sub: 데이터 제공처
        self.insurer = insurer    # Insurer object
        self.status = "INITIATED"

    async def collect_and_verify(self):
        print("Orchestrator: Starting claim process...")
        # 1. 병원 B로부터 서류 수집 및 정리 (Sub 업무)
        raw_docs = await self.hospital.get_medical_records()
        structured_data = await MulberryMind.distill_gold_data(raw_docs)

        # 2. 당사자 A의 보험 약관과 매칭 (Main 검증)
        claim_report = await MulberryMind.check_policy_coverage(self.user.insurance_id, structured_data)

        # 3. 최종 승인 요청 (A의 최종 확인)
        if await self.user.confirm_claim(claim_report):
            return await self.submit_to_insurer(claim_report)
        else:
            self.status = "CLAIM_REJECTED_BY_USER"
            print("Claim submission cancelled by user.")
            return {"status": "cancelled", "message": "User did not approve the claim."}

    async def submit_to_insurer(self, final_report):
        print(f"Orchestrator: Submitting claim to {self.insurer.name}...")
        await asyncio.sleep(0.1)
        # 보험사 성향에 따른 맞춤 전송 (보수적 집단 대응)
        if self.insurer.has_api:
            response = await MulberryMind.send_json_to_api(final_report)
            self.status = "SUBMITTED_VIA_API"
            return response
        else:
            pdf_docs_path = await MulberryMind.generate_perfect_pdf(final_report)
            response = await MulberryMind.send_auto_fax(pdf_docs_path)
            self.status = "SUBMITTED_VIA_FAX"
            return response
