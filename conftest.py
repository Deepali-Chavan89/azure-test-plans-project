"""
Root conftest.py – pytest hooks that collect results and push them to
Azure DevOps Test Plans after every test session.

Usage
-----
Set these environment variables (or pipeline variables) before running pytest:

  ADO_PAT             PAT with "Test Plans" read/write + "Work Items" read/write.
                      In Azure Pipelines use $(System.AccessToken) – see
                      azure-pipelines.yml for the env mapping.
  ADO_ORG_URL         https://dev.azure.com/atul-kamble   (default)
  ADO_PROJECT         project                             (default)
  ADO_TEST_PLAN_NAME  WebApp Testing                      (default – matches existing plan)
  ADO_TEST_SUITE_NAME Automated Tests                     (default)
  ADO_AREA_PATH       Area path owning the default team   (defaults to ADO_PROJECT)

Optional marker
---------------
Tag a test with an *existing* ADO Test Case ID to link results to that item:

    @pytest.mark.testcase(1234)
    def test_something():
        ...

Without the marker a Test Case is automatically created (once) by title.
"""

import logging
import os

import pytest

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Register the custom marker so pytest does not warn about unknown marks
# ---------------------------------------------------------------------------
def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "testcase(id): link test to an existing Azure DevOps Test Case ID",
    )


# ---------------------------------------------------------------------------
# Collect per-test outcomes
# ---------------------------------------------------------------------------
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call):  # noqa: ANN001
    outcome = yield
    rep = outcome.get_result()

    if rep.when != "call":
        return  # only care about the test body, not setup/teardown

    if not hasattr(item.session, "ado_test_results"):
        item.session.ado_test_results = []

    marker = item.get_closest_marker("testcase")
    item.session.ado_test_results.append(
        {
            "name": item.name,
            "nodeid": item.nodeid,
            "outcome": rep.outcome,           # "passed" | "failed" | "error"
            "duration_ms": int(rep.duration * 1000),
            "error": str(rep.longrepr) if rep.longrepr else None,
            "testcase_id": marker.args[0] if marker else None,
        }
    )


# ---------------------------------------------------------------------------
# Publish to Azure DevOps after the session ends
# ---------------------------------------------------------------------------
def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    results = getattr(session, "ado_test_results", [])
    if not results:
        return

    pat = os.environ.get("ADO_PAT") or os.environ.get("SYSTEM_ACCESSTOKEN")
    if not pat:
        logger.info(
            "ADO_PAT / SYSTEM_ACCESSTOKEN not set – skipping Azure DevOps Test Plans update."
        )
        return

    from tests.ado_test_publisher import ADOTestPublisher

    publisher = ADOTestPublisher(
        org_url=os.environ.get("ADO_ORG_URL", "https://dev.azure.com/atul-kamble"),
        project=os.environ.get("ADO_PROJECT", "project"),
        pat=pat,
        plan_name=os.environ.get("ADO_TEST_PLAN_NAME", "WebApp Testing"),
        suite_name=os.environ.get("ADO_TEST_SUITE_NAME", "Automated Tests"),
        area_path=os.environ.get("ADO_AREA_PATH") or os.environ.get("ADO_PROJECT", "project"),
    )

    try:
        publisher.publish(results)
        print(
            f"\nResults for {len(results)} test(s) published to Azure DevOps Test Plans."
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not publish results to Azure DevOps: %s", exc)
