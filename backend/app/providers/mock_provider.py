from .verification_provider import VerificationProvider

class MockVerificationProvider(VerificationProvider):
    def verify(self, data: dict) -> dict:
        return {"available": False, "message": "DEMO ONLY — NOT OFFICIAL VERIFICATION"}
