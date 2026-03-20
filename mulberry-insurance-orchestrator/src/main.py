import asyncio
from src.user import UserA
from src.hospital import HospitalB
from src.insurer import Insurer
from src.orchestrator import InsuranceClaimOrchestrator
import json
from unittest.mock import patch, AsyncMock

# --- Mocking utilities for automated input --- (adapted for module structure)
_input_queue = asyncio.Queue()

async def mock_input(prompt):
    print(prompt, end='')
    return await _input_queue.get()

async def send_input_to_mock(input_str):
    await _input_queue.put(input_str)
# ----------------------------------------------

async def run_all_scenarios():
    print("\n--- Starting End-to-End Orchestrator Testing (Modular) ---")

    user_a = UserA(insurance_id='A123_MODULAR')
    hospital_b = HospitalB(name='Modular Hospital')

    # Scenario 1: API Insurer
    api_insurer = Insurer(name='Modular API Insurer', has_api=True)
    orchestrator_api = InsuranceClaimOrchestrator(user_a, hospital_b, api_insurer)
    print("\n--- Scenario 1: API Insurer (Modular) ---")

    with patch('src.user.input', new=mock_input):
        await send_input_to_mock('yes') # Simulate user approval
        api_result = await orchestrator_api.collect_and_verify()
    print("--- Test with API Insurer Complete (Modular) ---")
    print("Result:", json.dumps(api_result, indent=2))

    # Scenario 2: Fax-only Insurer
    fax_insurer = Insurer(name='Modular Fax Insurer', has_api=False)
    orchestrator_fax = InsuranceClaimOrchestrator(user_a, hospital_b, fax_insurer)
    print("\n--- Scenario 2: Fax Insurer (Modular) ---")

    with patch('src.user.input', new=mock_input):
        await send_input_to_mock('yes') # Simulate user approval
        fax_result = await orchestrator_fax.collect_and_verify()
    print("--- Test with Fax Insurer Complete (Modular) ---")
    print("Result:", json.dumps(fax_result, indent=2))

    print("\n--- End-to-End Orchestrator Testing Complete (Modular) ---")

if __name__ == '__main__':
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError: # No running loop
        loop = None

    if loop and loop.is_running():
        asyncio.create_task(run_all_scenarios())
    else:
        asyncio.run(run_all_scenarios())
