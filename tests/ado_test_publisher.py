"""
Azure DevOps Test Plans publisher.

Uses the Azure DevOps REST API to:
  1. Find or create a Test Plan
  2. Find or create a Test Suite inside that plan
  3. Find or create a Test Case work item for every pytest test
  4. Create an automated Test Run
  5. Post each test outcome to that run

Required environment variables (set in azure-pipelines.yml or locally):
  ADO_PAT             Personal Access Token (or $(System.AccessToken) in pipelines)
  ADO_ORG_URL         https://dev.azure.com/<organisation>   (default: atul-kamble)
  ADO_PROJECT         Project name                           (default: project)
  ADO_TEST_PLAN_NAME  Test Plan name                         (default: WebApp Testing)
  ADO_TEST_SUITE_NAME Test Suite name                        (default: Automated Tests)
  ADO_AREA_PATH       Area path owning the default team      (default: project)
"""

import base64
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

# ADO outcome strings accepted by the REST API
_OUTCOME_MAP: Dict[str, str] = {
    "passed": "Passed",
    "failed": "Failed",
    "error": "Failed",
    "skipped": "NotApplicable",
}


class ADOTestPublisher:
    """Publishes pytest results to an Azure DevOps Test Plan via REST API."""

    _API_VERSION = "7.0"

    def __init__(
        self,
        org_url: str,
        project: str,
        pat: str,
        plan_name: str,
        suite_name: str,
        area_path: Optional[str] = None,
    ) -> None:
        self.plan_name = plan_name
        self.suite_name = suite_name
        # area_path must be owned by the project's default team or ADO rejects
        # plan-based test runs with "area path not owned by this project's default team".
        self._area_path = area_path or project
        self._base = f"{org_url.rstrip('/')}/{project}/_apis"
        token = base64.b64encode(f":{pat}".encode()).decode()
        self._headers = {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------
    # Internal HTTP helpers
    # ------------------------------------------------------------------

    def _get(self, path: str) -> dict:
        resp = requests.get(
            f"{self._base}/{path}",
            headers=self._headers,
            params={"api-version": self._API_VERSION},
        )
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, body, content_type: Optional[str] = None) -> dict:
        headers = dict(self._headers)
        if content_type:
            headers["Content-Type"] = content_type
        resp = requests.post(
            f"{self._base}/{path}",
            headers=headers,
            params={"api-version": self._API_VERSION},
            json=body,
        )
        resp.raise_for_status()
        return resp.json()

    def _patch(self, path: str, body) -> dict:
        resp = requests.patch(
            f"{self._base}/{path}",
            headers=self._headers,
            params={"api-version": self._API_VERSION},
            json=body,
        )
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Test Plan / Suite helpers
    # ------------------------------------------------------------------

    def get_or_create_plan(self) -> tuple:
        """Return (plan_id, root_suite_id), creating the plan when absent."""
        data = self._get("test/plans")
        for plan in data.get("value", []):
            if plan["name"] == self.plan_name:
                logger.debug("Found existing plan '%s' (id=%s)", self.plan_name, plan["id"])
                return plan["id"], plan["rootSuite"]["id"]

        plan = self._post(
            "test/plans",
            {
                "name": self.plan_name,
                "areaPath": self._area_path,
                "startDate": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        )
        logger.info("Created Test Plan '%s' (id=%s)", self.plan_name, plan["id"])
        return plan["id"], plan["rootSuite"]["id"]

    def get_or_create_suite(self, plan_id: int, root_suite_id: int) -> int:
        """Return suite_id for self.suite_name, creating it when absent."""
        data = self._get(f"test/plans/{plan_id}/suites")
        for suite in data.get("value", []):
            if suite["name"] == self.suite_name:
                logger.debug("Found existing suite '%s' (id=%s)", self.suite_name, suite["id"])
                return suite["id"]

        suite = self._post(
            f"test/plans/{plan_id}/suites",
            {
                "suiteType": "StaticTestSuite",
                "name": self.suite_name,
                "parentSuite": {"id": root_suite_id},
            },
        )
        logger.info("Created Test Suite '%s' (id=%s)", self.suite_name, suite["id"])
        return suite["id"]

    # ------------------------------------------------------------------
    # Test Case work item helpers
    # ------------------------------------------------------------------

    def find_test_case_by_title(self, title: str) -> Optional[int]:
        """Return the ID of the first Test Case with this title, or None."""
        safe_title = title.replace("'", "''")  # escape single quotes for WIQL
        wiql = {
            "query": (
                "SELECT [System.Id] FROM WorkItems "
                "WHERE [System.WorkItemType] = 'Test Case' "
                f"AND [System.Title] = '{safe_title}'"
            )
        }
        data = self._post("wit/wiql", wiql)
        items = data.get("workItems", [])
        return items[0]["id"] if items else None

    def create_test_case(self, title: str) -> int:
        """Create a new Test Case work item and return its ID."""
        patch_doc = [
            {"op": "add", "path": "/fields/System.Title", "value": title},
            {"op": "add", "path": "/fields/System.AreaPath", "value": self._area_path},
        ]
        resp = requests.post(
            f"{self._base}/wit/workitems/$Test Case",
            headers={**self._headers, "Content-Type": "application/json-patch+json"},
            params={"api-version": self._API_VERSION},
            json=patch_doc,
        )
        resp.raise_for_status()
        tc_id = resp.json()["id"]
        logger.info("Created Test Case '%s' (id=%s)", title, tc_id)
        return tc_id

    def add_to_suite(self, plan_id: int, suite_id: int, tc_id: int) -> None:
        """Add a test case to the suite (silently ignores if already present)."""
        try:
            requests.post(
                f"{self._base}/test/plans/{plan_id}/suites/{suite_id}/testcases/{tc_id}",
                headers=self._headers,
                params={"api-version": self._API_VERSION},
            ).raise_for_status()
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 409:
                pass  # already in the suite — not an error
            else:
                raise

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def publish(self, test_results: List[dict]) -> None:
        """
        Publish a list of pytest result dicts to Azure DevOps Test Plans.

        Each dict must contain:
          name          str   pytest test function name
          nodeid        str   pytest node id (unique key)
          outcome       str   "passed" | "failed" | "error" | "skipped"
          duration_ms   int   duration in milliseconds
          error         str | None  failure message / traceback
          testcase_id   int | None  existing ADO Test Case ID (from marker)
        """
        plan_id, root_suite_id = self.get_or_create_plan()
        suite_id = self.get_or_create_suite(plan_id, root_suite_id)

        # Resolve each test to an ADO Test Case ID
        tc_id_map: Dict[str, int] = {}
        for result in test_results:
            if result["testcase_id"]:
                # Caller supplied an existing Test Case ID via @pytest.mark.testcase
                tc_id = int(result["testcase_id"])
                self.add_to_suite(plan_id, suite_id, tc_id)
            else:
                # Auto-find or auto-create a Test Case by title
                existing = self.find_test_case_by_title(result["name"])
                if existing:
                    tc_id = existing
                    self.add_to_suite(plan_id, suite_id, tc_id)
                else:
                    tc_id = self.create_test_case(result["name"])
                    self.add_to_suite(plan_id, suite_id, tc_id)
            tc_id_map[result["nodeid"]] = tc_id

        # Create an automated test run
        run_name = (
            f"Automated Run – {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
        )
        run = self._post(
            "test/runs",
            {
                "name": run_name,
                "plan": {"id": plan_id},
                "isAutomated": True,
            },
        )
        run_id = run["id"]
        logger.info("Created Test Run '%s' (id=%s)", run_name, run_id)

        # Post individual results
        results_payload = [
            {
                "testCase": {"id": tc_id_map[r["nodeid"]]},
                "testCaseName": r["name"],
                "outcome": _OUTCOME_MAP.get(r["outcome"], "Blocked"),
                "durationInMs": r["duration_ms"],
                "errorMessage": (r["error"] or "")[:1000],
                "state": "Completed",
            }
            for r in test_results
        ]
        self._post(f"test/runs/{run_id}/results", results_payload)

        # Mark the run as completed
        self._patch(f"test/runs/{run_id}", {"state": "Completed"})
        logger.info(
            "Published %d result(s) to Test Plan '%s' (run id=%s)",
            len(test_results),
            self.plan_name,
            run_id,
        )
