# 🌿 Mulberry Insurance Orchestrator AI Agent

![Mulberry Logo](mulberry_logo.png)

[![English](https://img.shields.io/badge/Language-English-blue?style=flat-square)](README_en.md) [![Korean](https://img.shields.io/badge/Language-Korean-red?style=flat-square)](README_ko.md) [![Vietnamese](https://img.shields.io/badge/Language-Vietnamese-green?style=flat-square)](README_vi.md)

[![Hugging Face Spaces](https://img.shields.io/badge/Hugging_Face-Spaces-blue?style=flat-square&logo=huggingface&logoColor=white)](https://huggingface.co/spaces/re-eul/mulberry-demo) [![Server Status](https://img.shields.io/badge/Server-Live-brightgreen?style=flat-square)](https://mulberry-open-api-production.up.railway.app/)

## Project Description
The `Mulberry Insurance Orchestrator` is an AI-powered agent designed to automate and streamline the end-to-end insurance claim processing workflow. It integrates various components to collect medical records, distill relevant data, check policy coverage, facilitate user approval, and submit claims to insurers through multiple channels (API, PDF, Fax).

## Features
- **Automated Data Collection:** Gathers raw medical records from healthcare providers.
- **Intelligent Data Distillation:** Converts unstructured medical documents into a structured, 'gold' data format using NLP and regex.
- **Dynamic Policy Coverage Check:** Evaluates claims against insurance policies, calculating deductibles, co-pays, and estimated reimbursements.
- **Human-in-the-Loop Approval:** Requires policyholder (User A) confirmation of the claim report before submission, ensuring transparency and consent.
- **Flexible Claim Submission:** Adapts submission methods based on insurer capabilities:
  - Direct API integration for modern insurers.
  - Automated PDF generation and fax submission for traditional or conservative insurers.

## Project Structure
```
mulberry-insurance-orchestrator/
├── .env                 # Environment variables for configuration
├── requirements.txt     # Python dependencies
├── src/
│   ├── __init__.py      # Marks src as a Python package
│   ├── user.py          # Defines UserA class for claim approval logic
│   ├── hospital.py      # Defines HospitalB class for medical record collection
│   ├── insurer.py       # Defines Insurer class for insurer details (API capability)
│   ├── mulberry_mind.py # Contains MulberryMind logic for data distillation, policy check, and submission methods
│   ├── orchestrator.py  # Main orchestrator logic (InsuranceClaimOrchestrator)
│   ├── settings.py      # Pydantic BaseSettings for application configuration
│   └── main.py          # Example script to run end-to-end scenarios
└── tests/
    └── test_orchestrator.py # Unit tests for the InsuranceClaimOrchestrator
```

## Installation

1.  **Clone the repository:**
    ```bash
    git clone [your-github-repo-url]
    cd mulberry-insurance-orchestrator
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\\Scripts\\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the root directory and populate it with your configuration. An example `.env` file is provided in the project structure for reference.

    ```ini
    APP_NAME="Mulberry Insurance Orchestrator Dev"
    DEBUG=True

    API_INSURER_URL="https://dev.api.insurer.com/v1/claims"
    API_INSURER_API_KEY="dev-api-key-123"

    FAX_FROM_NUMBER="+15551234567" # Your Twilio number
    FAX_TO_NUMBER="+821098765432" # Recipient fax number
    TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" # Your Twilio Account SID
    TWILIO_AUTH_TOKEN="your_twilio_auth_token" # Your Twilio Auth Token

    MCCC_WEBHOOK_URL="https://dev.mccc.mulberry.com/webhook/approval"
    ```
    *Note: For actual faxing functionality, you will need a Twilio account and a publicly accessible URL for PDF media. The current `send_auto_fax` function uses a placeholder.*

## Usage

To run the end-to-end demonstration of the claim processing pipeline:

```bash
python src/main.py
```

Upon execution, you will be prompted for user approval. Enter 'yes' to proceed with the claim submission.

## Testing

To run the unit tests for the orchestrator:

```bash
python -m unittest tests/test_orchestrator.py
```

## Future Enhancements

### For Seniors
- **Improved Accessibility:** Voice commands and simplified UI.
- **Simplified Explanations:** Plain language summaries of policies and reports.
- **Assisted Filing:** Integration with phone support.
- **Proactive Alerts:** Reminders for missing info/deadlines.
- **Caregiver Access:** Secure, permission-based access for family/caregivers.

### For Rural Residents
- **Offline Capabilities:** Data collection and claim initiation without constant internet access.
- **Telehealth Integration:** Seamless pulling of data from remote care platforms.
- **Mobile Scanning:** Leveraging smartphone cameras for document uploads.
- **Location-Aware Assistance:** Finding nearest covered providers.
- **Batch Processing:** Optimized data transfer for limited bandwidth.

## License
[Specify your project's license here, e.g., MIT, Apache 2.0]

## Contact
[Your Name/Email/GitHub Profile]
