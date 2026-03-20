import asyncio

class HospitalB:
    def __init__(self, name="Hospital B"):
        self.name = name

    async def get_medical_records(self) -> list:
        print(f"{self.name} is providing medical records.")
        # Simulate an async I/O operation
        await asyncio.sleep(0.1)
        return [
            "Patient_Name: John Doe, DOB: 1990-05-15, Visit_Date: 2023-01-20, Diagnosis: Common Cold, Treatment: Rest and fluids",
            "Lab_Result: White blood cell count normal, Temperature: 99.8F",
            "Physician_Notes: Patient presented with mild fever and cough. Prescribed OTC medication."
        ]
