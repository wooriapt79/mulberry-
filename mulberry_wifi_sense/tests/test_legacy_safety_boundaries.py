import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "kbin-wifi-sensing-mvp-20260314.py"
SPEC = importlib.util.spec_from_file_location("legacy_wifi_sense", MODULE_PATH)
legacy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(legacy)


class LegacySafetyBoundaryTest(unittest.TestCase):
    def test_high_risk_and_external_features_are_disabled_by_default(self):
        self.assertFalse(legacy.WHOFI_ENABLED)
        self.assertFalse(legacy.LEGACY_EXTERNAL_ACTIONS_ENABLED)

    def test_whofi_enrollment_and_identification_are_blocked(self):
        identifier = legacy.WhoFiIdentifier()
        with self.assertRaises(PermissionError):
            identifier.enroll_person("resident-1")
        with self.assertRaises(PermissionError):
            identifier.identify_person([0.1] * 64)
        self.assertEqual(identifier.body_signature_db, {})

    def test_legacy_api_and_emergency_paths_are_blocked(self):
        client = legacy.MHCClient(mock_mode=True)
        with self.assertRaises(PermissionError):
            client.send_fall_detection_alert({"eventType": "fall_suspected"})
        with self.assertRaises(PermissionError):
            legacy.WiFiSensingModule().alert_emergency()
        with self.assertRaises(PermissionError):
            legacy.MHCMultiModalSensor().trigger_emergency()
        with self.assertRaises(PermissionError):
            legacy.WiFiFallDetector().trigger_emergency()


if __name__ == "__main__":
    unittest.main()
