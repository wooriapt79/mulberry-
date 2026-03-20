import re
import json
import asyncio
import logging # Added logging
import httpx   # Added httpx
from twilio.rest import Client # Added Twilio Client

# Import Settings class from src.settings
from src.settings import Settings

# For PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os

# Configure logging (for demonstration purposes, logging to console)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MulberryMind:
    @staticmethod
    async def distill_gold_data(raw_docs: list) -> dict:
        logger.info("MulberryMind is distilling raw documents into structured data.")
        await asyncio.sleep(0.1)
        structured_data = {
            "patient_info": {},
            "visit_details": [],
            "lab_results": {},
            "imaging_reports": [],
            "physician_notes_summary": ""
        }
        for doc in raw_docs:
            patient_visit_match = re.search(r"Patient_Name: (.*?), DOB: (.*?), Visit_Date: (.*?), Diagnosis: (.*?), Treatment: (.*)", doc)
            if patient_visit_match:
                structured_data["patient_info"]["name"] = patient_visit_match.group(1).strip()
                structured_data["patient_info"]["dob"] = patient_visit_match.group(2).strip()
                structured_data["patient_info"]["insurance_id"] = "INS789012"
                visit_detail = {
                    "visit_date": patient_visit_match.group(3).strip(),
                    "diagnosis_codes": [patient_visit_match.group(4).strip()],
                    "procedures": [],
                    "medications": [],
                    "total_cost": 150.75,
                    "provider": "Dr. Smith"
                }
                structured_data["visit_details"].append(visit_detail)
            lab_result_match = re.search(r"Lab_Result: (.*?), Temperature: (.*)", doc)
            if lab_result_match:
                structured_data["lab_results"]["WBC_count"] = lab_result_match.group(1).strip()
                structured_data["lab_results"]["temperature"] = lab_result_match.group(2).strip()
            physician_notes_match = re.search(r"Physician_Notes: (.*)", doc)
            if physician_notes_match:
                structured_data["physician_notes_summary"] = physician_notes_match.group(1).strip()
        if not structured_data["visit_details"]:
            structured_data["visit_details"].append({
                "visit_date": "Unknown",
                "diagnosis_codes": [],
                "procedures": [],
                "medications": [],
                "total_cost": 0.0,
                "provider": "Unknown"
            })
        return structured_data

    @staticmethod
    async def check_policy_coverage(insurance_id: str, structured_data: dict) -> dict:
        logger.info("MulberryMind is checking policy coverage with enhanced logic.")
        await asyncio.sleep(0.1)
        DEDUCTIBLE_AMOUNT = 100.00
        COPAY_PER_VISIT = 20.00
        COVERAGE_PERCENTAGE = 0.80
        EXCLUDED_DIAGNOSIS_CODES = []
        EXCLUDED_PROCEDURES = []
        patient_name = structured_data.get("patient_info", {}).get("name", "N/A")
        visit_details = structured_data.get("visit_details", [{}])
        first_visit = visit_details[0]
        date_of_service = first_visit.get("visit_date", "N/A")
        total_billed_amount = first_visit.get("total_cost", 0.0)
        diagnosis_codes = first_visit.get("diagnosis_codes", [])
        procedures = first_visit.get("procedures", [])
        covered_items = []
        non_covered_items = []
        total_covered_cost = 0.0
        for code in diagnosis_codes:
            if code in EXCLUDED_DIAGNOSIS_CODES:
                non_covered_items.append({"description": f"Diagnosis Code {code}", "amount": 0.0, "status": "Not Covered", "reason": "Policy Exclusion"})
            else:
                covered_items.append({"description": f"Diagnosis Code {code}", "amount": 0.0, "status": "Covered"})
        for proc in procedures:
            if proc in EXCLUDED_PROCEDURES:
                non_covered_items.append({"description": f"Procedure Code {proc}", "amount": 0.0, "status": "Not Covered", "reason": "Policy Exclusion"})
            else:
                covered_items.append({"description": f"Procedure Code {proc}", "amount": 0.0, "status": "Covered"})
        if total_billed_amount > 0:
            office_visit_cost = total_billed_amount
            if any(code in EXCLUDED_DIAGNOSIS_CODES for code in diagnosis_codes):
                 non_covered_items.append({"description": "Primary Medical Service", "amount": office_visit_cost, "status": "Not Covered", "reason": "Associated with excluded diagnosis"})
            else:
                covered_items.append({"description": "Primary Medical Service", "amount": office_visit_cost, "status": "Covered"})
                total_covered_cost = office_visit_cost
        deductible_remaining = DEDUCTIBLE_AMOUNT
        applied_to_deductible = 0.0
        if total_covered_cost > 0 and deductible_remaining > 0:
            applied_to_deductible = min(total_covered_cost, deductible_remaining)
            deductible_remaining -= applied_to_deductible
            total_covered_cost -= applied_to_deductible
        co_pay_amount = COPAY_PER_VISIT
        if total_covered_cost > 0 and co_pay_amount > 0:
             total_covered_cost -= co_pay_amount
        estimated_reimbursement = max(0.0, total_covered_cost * COVERAGE_PERCENTAGE)
        deductible_remaining = max(0.0, deductible_remaining)
        co_pay_amount = max(0.0, co_pay_amount)
        policy_applicability_summary = (
            f"Policy covers 80% after ${DEDUCTIBLE_AMOUNT:.2f} deductible and ${COPAY_PER_VISIT:.2f} co-pay. "
            f"Applied ${applied_to_deductible:.2f} to deductible. "
            f"Remaining deductible: ${deductible_remaining:.2f}."
        )
        claim_report = {
            "claim_id": f"CLM-{date_of_service}-{insurance_id}",
            "policy_id": insurance_id,
            "patient_name": patient_name,
            "date_of_service": date_of_service,
            "total_billed_amount": total_billed_amount,
            "covered_items": covered_items,
            "non_covered_items": non_covered_items,
            "estimated_reimbursement": round(estimated_reimbursement, 2),
            "deductible_remaining": round(deductible_remaining, 2),
            "co_pay_amount": round(co_pay_amount, 2),
            "policy_applicability_summary": policy_applicability_summary,
            "status": "Pending Approval"
        }
        return claim_report

    # Modified to accept settings object and use httpx for actual API call
    @staticmethod
    async def send_json_to_api(final_report: dict, settings: Settings) -> dict:
        logger.info(f"MulberryMind: Submitting claim via API to {settings.API_INSURER_URL}...")
        await asyncio.sleep(0.1) # Simulate network latency

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.API_INSURER_URL,
                    json=final_report,
                    headers={"Authorization": f"Bearer {settings.API_INSURER_API_KEY}"}
                )
                response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
                logger.info("Claim submitted via API successfully.")
                return {"status": "success", "message": "Claim submitted via API successfully", "claim_id": final_report.get("claim_id")}
        except httpx.HTTPStatusError as e:
            logger.error(f"API submission failed due to HTTP error: {e.response.status_code} - {e.response.text}")
            return {"status": "failed", "message": f"HTTP error during API submission: {e.response.status_code}", "details": e.response.text}
        except httpx.RequestError as e:
            logger.error(f"API submission failed due to network error: {e}")
            return {"status": "failed", "message": f"Network error during API submission: {e}"}
        except Exception as e:
            logger.error(f"An unexpected error occurred during API submission: {e}")
            return {"status": "failed", "message": f"Unexpected error during API submission: {e}"}

    @staticmethod
    async def generate_perfect_pdf(final_report: dict) -> str:
        """보험 청구 리포트를 PDF 파일로 생성"""
        logger.info("MulberryMind: Generating perfect PDF for claim submission...")
        await asyncio.sleep(0.1)
        filename = f"claim_{final_report['claim_id']}.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter

        # 헤더
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1*inch, height-1*inch, "Mulberry Insurance Claim")
        c.setFont("Helvetica", 10)
        c.drawString(1*inch, height-1.5*inch, f"Claim ID: {final_report.get('claim_id')}")
        c.drawString(1*inch, height-2*inch, f"Patient: {final_report.get('patient_name')}")
        c.drawString(1*inch, height-2.5*inch, f"Date of Service: {final_report.get('date_of_service')}")
        c.drawString(1*inch, height-3*inch, f"Total Billed: ${final_report.get('total_billed_amount', 0):,.2f}")
        c.drawString(1*inch, height-3.5*inch, f"Estimated Reimbursement: ${final_report.get('estimated_reimbursement', 0):,.2f}")

        # Add more details from final_report to the PDF
        y_position = height - 4.0 * inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, y_position, "Coverage Details:")
        y_position -= 0.2 * inch
        c.setFont("Helvetica", 10)
        for item in final_report.get('covered_items', []):
            y_position -= 0.2 * inch
            c.drawString(1.2*inch, y_position, f"- {item['description']}: {item['status']}")
            if y_position < 1*inch: # New page if content goes too low
                c.showPage()
                y_position = height - 1*inch
                c.setFont("Helvetica", 10)

        if final_report.get('non_covered_items'):
            y_position -= 0.4 * inch
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1*inch, y_position, "Non-Covered Details:")
            y_position -= 0.2 * inch
            c.setFont("Helvetica", 10)
            for item in final_report.get('non_covered_items', []):
                y_position -= 0.2 * inch
                c.drawString(1.2*inch, y_position, f"- {item['description']}: {item['reason']}")
                if y_position < 1*inch:
                    c.showPage()
                    y_position = height - 1*inch
                    c.setFont("Helvetica", 10)

        y_position -= 0.4 * inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, y_position, "Financial Summary:")
        y_position -= 0.2 * inch
        c.setFont("Helvetica", 10)
        c.drawString(1.2*inch, y_position, f"Deductible Remaining: ${final_report.get('deductible_remaining', 0):,.2f}")
        y_position -= 0.2 * inch
        c.drawString(1.2*inch, y_position, f"Co-Pay Amount: ${final_report.get('co_pay_amount', 0):,.2f}")
        y_position -= 0.2 * inch
        c.drawString(1.2*inch, y_position, f"Policy Summary: {final_report.get('policy_applicability_summary', 'N/A')}")


        c.save()
        return filename

    # Modified to accept settings object and use twilio for actual fax sending
    @staticmethod
    async def send_auto_fax(pdf_docs: str, settings: Settings) -> dict:
        logger.info(f"MulberryMind: Sending claim PDF via automated fax service to {settings.FAX_TO_NUMBER} (from {settings.FAX_FROM_NUMBER})...")
        await asyncio.sleep(0.1) # Simulate latency

        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # In a real scenario, the PDF needs to be hosted publicly and its URL passed to Twilio.
            # For demonstration, we'll use a placeholder URL.
            # You would need to implement `upload_to_cloud` function to upload the generated PDF
            # to a public storage (e.g., AWS S3, Google Cloud Storage, or a simple web server)
            # and get a publicly accessible URL.
            # For now, we use a mock URL.
            media_url = f"https://your-public-storage.com/{os.path.basename(pdf_docs)}"

            fax = client.fax.faxes.create(
                from_=settings.FAX_FROM_NUMBER,
                to=settings.FAX_TO_NUMBER,
                media_url=media_url
            )
            logger.info(f"Claim faxed successfully. Fax SID: {fax.sid}")
            return {"status": "success", "message": "Claim faxed successfully", "document_path": pdf_docs, "fax_sid": fax.sid}
        except Exception as e:
            logger.error(f"Failed to send fax via Twilio: {e}")
            return {"status": "failed", "message": f"Failed to send fax: {e}", "document_path": pdf_docs}
