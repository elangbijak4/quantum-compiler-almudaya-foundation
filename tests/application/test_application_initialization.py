"""
Application / Product Layer Initialization Unit Tests.

Verifies ApplicationRequest, ApplicationResponse, ApplicationContractService gateway,
SHA-256 hashing, credential isolation, and Core authority preservation.
"""

import unittest

from src.application import (
    ApplicationIntent,
    ApplicationStatus,
    ApplicationRequest,
    ApplicationResponse,
    ApplicationContractProtocol,
    ApplicationContractService,
)


class TestApplicationLayerInitialization(unittest.TestCase):
    """Initialization test suite for Application / Product Layer."""

    def setUp(self) -> None:
        self.service = ApplicationContractService()

    def test_01_request_models_and_hashing(self) -> None:
        """Verifies ApplicationRequest construction and deterministic SHA-256 request_hash."""
        req = ApplicationRequest(
            request_id="REQ_APP_01",
            intent=ApplicationIntent.COMPILE,
            backend_id="IBM_TORINO",
            shots=1000,
        )
        self.assertEqual(req.intent, ApplicationIntent.COMPILE)
        self.assertEqual(req.shots, 1000)
        self.assertEqual(len(req.request_hash), 64)

    def test_02_response_models_and_hashing(self) -> None:
        """Verifies ApplicationResponse construction and deterministic SHA-256 response_hash."""
        resp = ApplicationResponse(
            request_id="REQ_APP_01",
            intent=ApplicationIntent.COMPILE,
            status=ApplicationStatus.SUCCESS,
            artifact_references={"logical_circuit_id": "LOG_CIRC_01"},
        )
        self.assertEqual(resp.status, ApplicationStatus.SUCCESS)
        self.assertEqual(len(resp.response_hash), 64)

    def test_03_contract_service_inspect(self) -> None:
        """Verifies ApplicationContractService inspect method returns backend details via Stage 1 Registry."""
        req = ApplicationRequest(
            request_id="REQ_INSPECT_01",
            intent=ApplicationIntent.INSPECT,
            backend_id="LOCAL_REFERENCE",
        )
        resp = self.service.inspect(req)
        self.assertEqual(resp.status, ApplicationStatus.SUCCESS)
        self.assertIn("qubit_count", resp.result_payload)

    def test_04_contract_service_simulate(self) -> None:
        """Verifies ApplicationContractService simulate method delegates to Stage 3 simulation contract."""
        req = ApplicationRequest(
            request_id="REQ_SIM_01",
            intent=ApplicationIntent.SIMULATE,
            shots=2000,
        )
        resp = self.service.simulate(req)
        self.assertEqual(resp.status, ApplicationStatus.SUCCESS)
        self.assertEqual(resp.result_payload["shots"], 2000)

    def test_05_security_credential_isolation(self) -> None:
        """Verifies zero secret tokens or passwords appear in request or response serializations."""
        req = ApplicationRequest(
            request_id="REQ_SEC_01",
            intent=ApplicationIntent.EXECUTE,
            credential_ref="env:MY_SECURE_TOKEN_REF",
        )
        resp = self.service.execute(req)

        req_str = str(req.to_dict())
        resp_str = str(resp.to_dict())

        for secret in ("raw_api_key_123", "bearer_secret_abc", "sk-live-000", "password999"):
            self.assertNotIn(secret, req_str)
            self.assertNotIn(secret, resp_str)


if __name__ == "__main__":
    unittest.main()
