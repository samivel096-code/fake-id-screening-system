from typing import Dict, Any, Optional

class VerificationProvider:
    """Base class for all authoritative verification providers."""
    @property
    def provider_name(self) -> str:
        raise NotImplementedError

    @property
    def is_authoritative(self) -> bool:
        return False

    def verify(self, doc_type: str, document_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempts verification against authoritative source.
        Returns dict with status ("VERIFIED", "FAILED", "NOT AVAILABLE"), message, and metadata.
        """
        raise NotImplementedError

class MockVerificationProvider(VerificationProvider):
    """
    Demonstration verification provider.
    ALWAYS clearly tags responses with 'DEMO ONLY — NOT OFFICIAL VERIFICATION'
    and never claims real legal validation without authoritative connectivity.
    """
    @property
    def provider_name(self) -> str:
        return "Simulated Sandbox Provider (DEMO ONLY)"

    @property
    def is_authoritative(self) -> bool:
        return False

    def verify(self, doc_type: str, document_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "NOT AVAILABLE",
            "verified": False,
            "provider": self.provider_name,
            "notice": "DEMO ONLY — NOT OFFICIAL VERIFICATION. Official authoritative verification is not connected. Automated AI screening completed.",
            "is_demo": True
        }

class AadhaarVerificationProvider(VerificationProvider):
    @property
    def provider_name(self) -> str:
        return "Aadhaar e-KYC / CIDR Gateway"

    def verify(self, doc_type: str, document_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        # Production would connect to authorized AUA/KUA secure endpoint with HSM digital signature
        return {
            "status": "NOT AVAILABLE",
            "verified": False,
            "provider": self.provider_name,
            "notice": "Official UIDAI/AUA gateway connectivity requires authorized enterprise digital certificates.",
            "is_demo": True
        }

class PANVerificationProvider(VerificationProvider):
    @property
    def provider_name(self) -> str:
        return "NSDL / Protean / UTIITSL PAN Gateway"

    def verify(self, doc_type: str, document_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "NOT AVAILABLE",
            "verified": False,
            "provider": self.provider_name,
            "notice": "Authoritative PAN API requires government-licensed entity credentials.",
            "is_demo": True
        }

class DrivingLicenceVerificationProvider(VerificationProvider):
    @property
    def provider_name(self) -> str:
        return "Sarathi / Parivahan National Register"

    def verify(self, doc_type: str, document_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "NOT AVAILABLE",
            "verified": False,
            "provider": self.provider_name,
            "notice": "Parivahan state transport register integration is currently offline or unconfigured.",
            "is_demo": True
        }

class PassportVerificationProvider(VerificationProvider):
    @property
    def provider_name(self) -> str:
        return "Passport Seva Project Gateway"

    def verify(self, doc_type: str, document_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "NOT AVAILABLE",
            "verified": False,
            "provider": self.provider_name,
            "notice": "Passport verification requires Ministry of External Affairs authorized system.",
            "is_demo": True
        }

class CustomVerificationProvider(VerificationProvider):
    @property
    def provider_name(self) -> str:
        return "Custom Verification Provider"

    def verify(self, doc_type: str, document_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "NOT AVAILABLE",
            "verified": False,
            "provider": self.provider_name,
            "notice": "Custom verification endpoint not configured.",
            "is_demo": True
        }

def get_verification_provider(doc_type: str) -> VerificationProvider:
    dt = doc_type.lower()
    if "aadhaar" in dt:
        return AadhaarVerificationProvider()
    elif "pan" in dt:
        return PANVerificationProvider()
    elif "driving" in dt:
        return DrivingLicenceVerificationProvider()
    elif "passport" in dt:
        return PassportVerificationProvider()
    return MockVerificationProvider()
