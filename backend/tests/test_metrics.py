import os
import sys
import unittest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

os.environ["BOOKHIVE_ENV"] = "test"

from fastapi.testclient import TestClient  # noqa: E402
from bookhive.main import app  # noqa: E402


class MetricsTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_metrics_endpoint_exists_and_returns_keys(self):
        # Make a couple requests first so metrics has something
        self.client.get("/health")
        self.client.get("/health")

        res = self.client.get("/metrics")
        self.assertEqual(res.status_code, 200)

        data = res.json()
        self.assertIn("requests_total", data)
        self.assertIn("errors_total", data)
        self.assertIn("error_rate", data)
        self.assertIn("latency_ms_p95", data)

    def test_metrics_errors_increase_on_401(self):
        before = self.client.get("/metrics").json()["errors_total"]

        # cause an error (401)
        self.client.get("/auth/me")

        after = self.client.get("/metrics").json()["errors_total"]
        self.assertGreaterEqual(after, before + 1)


if __name__ == "__main__":
    unittest.main()
