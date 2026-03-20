import json
import asyncio

class UserA:
    def __init__(self, insurance_id):
        self.insurance_id = insurance_id

    async def confirm_claim(self, claim_report: dict) -> bool:
        print("\n--- User A: Please review the claim report --- ")
        print(json.dumps(claim_report, indent=4))

        # Use asyncio.to_thread for blocking input() in async context
        user_input = await asyncio.to_thread(input, "Do you approve this claim report? (yes/no): ")
        user_input = user_input.lower()

        if user_input == 'yes':
            print("User A approved the claim.")
            return True
        else:
            print("User A did not approve the claim.")
            return False
