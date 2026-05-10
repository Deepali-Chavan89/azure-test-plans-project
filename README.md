# 📘 Azure Test Plans with Azure Pipelines — Full Step-by-Step Project Guide

---

# 📌 Project Overview

This project demonstrates end-to-end testing using:

* Microsoft [Azure DevOps Services](https://azure.microsoft.com/en-in/products/devops?utm_source=chatgpt.com)
* Azure Test Plans
* Azure Pipelines
* Selenium Automation
* PyTest
* Manual Testing
* Test Reporting
* Bug Tracking

---

# 📌 Project Architecture

```text id="s0ezlr"
Developer
   ↓
Azure Repos
   ↓
Azure Pipeline
   ↓
Build & Install Dependencies
   ↓
Execute Selenium Tests
   ↓
Publish Test Results
   ↓
Azure Test Plans
   ↓
Progress Reports & Bug Tracking
```

---

# 📌 Prerequisites

## Install Required Tools

| Tool          | Purpose               |
| ------------- | --------------------- |
| Python 3      | Application & Testing |
| Git           | Version Control       |
| VS Code       | IDE                   |
| Google Chrome | Browser Testing       |
| ChromeDriver  | Selenium Driver       |

---

# 📌 Step 1 — Create Azure DevOps Project

Open:

[Azure DevOps Portal](https://dev.azure.com?utm_source=chatgpt.com)

---

## Create:

* Organization
* New Project

Example:

```text id="e2r24g"
Project Name: Azure-TestPlans-Project
Visibility: Private
Version Control: Git
```

---

# 📌 Step 2 — Clone Repository

```bash id="udn6sz"
git clone https://dev.azure.com/ORG_NAME/PROJECT_NAME/_git/azure-test-plans-project

cd azure-test-plans-project
```

---

# 📌 Step 3 — Create Project Structure

```bash id="0hzvud"
mkdir app
mkdir tests

touch app/app.py
touch tests/test_google.py
touch requirements.txt
touch azure-pipelines.yml
touch README.md
```

---

# 📌 Step 4 — Create Python Flask Application

## app/app.py

```python id="f3m1k9"
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Azure Test Plans Project Running"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

# 📌 Step 5 — Add Dependencies

## requirements.txt

```text id="ef3q5g"
flask
pytest
selenium
webdriver-manager
```

---

# 📌 Step 6 — Install Dependencies Locally

```bash id="w9t8l0"
pip install -r requirements.txt
```

---

# 📌 Step 7 — Create Selenium Automation Test

## tests/test_google.py

```python id="g52wrf"
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_google_title():

    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service)

    driver.get("https://www.google.com")

    assert "Google" in driver.title

    driver.quit()
```

---

# 📌 Step 8 — Run Tests Locally

```bash id="m4h6m5"
pytest tests/
```

---

# 📌 Step 9 — Create Azure Pipeline

## azure-pipelines.yml

```yaml id="wlalxy"
trigger:
- main

pool:
  vmImage: ubuntu-latest

steps:

- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.x'

- script: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
  displayName: Install Dependencies

- script: |
    pytest tests/ --junitxml=test-results.xml
  displayName: Execute Selenium Tests

- task: PublishTestResults@2
  inputs:
    testResultsFormat: 'JUnit'
    testResultsFiles: 'test-results.xml'
    failTaskOnFailedTests: true
```

---

# 📌 Step 10 — Push Code to Azure Repos

```bash id="jlwm83"
git init

git add .

git commit -m "Azure Test Plans Project"

git branch -M main

git push origin main
```

---

# 📌 Step 11 — Create Azure Pipeline in Azure DevOps

Open:

```text id="3v0h7r"
Pipelines → New Pipeline
```

---

## Select

* Azure Repos Git
* Select Repository
* Existing YAML File

Select:

```text id="qpr58l"
azure-pipelines.yml
```

---

# 📌 Step 12 — Run Pipeline

Click:

```text id="r7ng9g"
Run Pipeline
```

---

# 📌 Pipeline Executes

* Install Python
* Install Dependencies
* Run Selenium Tests
* Publish Test Results

---

# 📌 Step 13 — Open Azure Test Plans

Navigate:

```text id="t4ik44"
Azure DevOps → Test Plans
```

---

# 📌 Step 14 — Create Test Plan Manually in Azure DevOps

## Navigation

```text
Azure DevOps → atul-kamble / project → Test Plans → Test plans → New Test Plan
```

---

## Step-by-Step

### 1. Open Test Plans

- Go to your Azure DevOps project: `https://dev.azure.com/atul-kamble/project`
- In the left sidebar click **Test Plans**
- Click **Test plans** (top menu item)

### 2. Click "+ New Test Plan"

A dialog box opens.

### 3. Fill in the Details

| Field | Value to enter |
| --- | --- |
| **Name** | `WebApp Testing` |
| **Area path** | `project` (select from dropdown — must match the team's area) |
| **Iteration** | `project\Sprint 1` (or current iteration) |
| **Start date** | Today's date |
| **End date** | Sprint end date |

> ⚠️ **Important:** The **Area path** must be one owned by the project's default team.
> Go to **Project Settings → Boards → Team → Areas** to see which paths the team owns.
> If you pick an unowned area path, test runs will fail with _"area path is not owned by this project's default team"_.

### 4. Click **Create**

The new test plan opens automatically.

---

## Add a Test Suite inside the Plan

### 5. Click "+ Suite" → "Static suite"

| Field | Value |
| --- | --- |
| **Suite name** | `Automated Tests` |

Click **Create**.

---

## Add Test Cases to the Suite

### 6. Click "+ New Test Case"

| Field | Value |
| --- | --- |
| **Title** | `Verify Google Homepage` |
| **Steps – Action** | Open browser, Navigate to https://www.google.com, Verify page title |
| **Steps – Expected** | Browser opens, Page loads, Title contains "Google" |
| **Priority** | 2 |
| **Assigned To** | Your name |
| **Area path** | `project` |

Click **Save & Close**.

---

## Assign Configurations

### 7. Select the test case → Click "Column options" → Enable "Configuration"

Default configuration: **Windows 10** (already exists in your project).

---

## Link an Automated Test to a Test Case

### 8. Open a Test Case → go to "Associated Automation" tab

| Field | Value |
| --- | --- |
| **Automation status** | Automated |
| **Test method** | `tests.test_google::test_google_title` |

> This links the pytest test so pipeline results automatically appear inside the Test Case.

---

## Verify the Plan is Visible

Navigate to:

```text
Test Plans → Progress report
```

You should see **WebApp Testing** with test points populated after the next pipeline run.

---

## Quick Reference: Manual Test Plan Setup Checklist

```text
[ ] Created Test Plan "WebApp Testing"  (area path = project)
[ ] Created Static Suite "Automated Tests" inside the plan
[ ] Added Test Cases with steps and expected results
[ ] Set Area Path = "project" on every Test Case work item
[ ] Assigned testers
[ ] Verified configuration is "Windows 10"
[ ] Pushed code → pipeline ran → results appeared in Runs tab
```

---

# 📌 Step 15 — Create Test Suite

Click:

```text id="d6pkpr"
New Suite
```

---

## Example

```text id="jlwm22"
Suite Name: Login Module Tests
```

---

# 📌 Types of Test Suites

| Type                    | Purpose           |
| ----------------------- | ----------------- |
| Static Suite            | Manual grouping   |
| Requirement-based Suite | Linked work items |
| Query-based Suite       | Dynamic query     |

---

# 📌 Step 16 — Create Test Case

Click:

```text id="6gqk3z"
New Test Case
```

---

# 📌 Example Test Case

## Title

```text id="6vfk1z"
Verify Google Homepage
```

---

## Test Steps

| Action             | Expected Result       |
| ------------------ | --------------------- |
| Open browser       | Browser launches      |
| Navigate to Google | Google opens          |
| Verify title       | Title contains Google |

---

# 📌 Step 17 — Configure Parameters

Open:

```text id="43du4o"
Test Case → Parameters
```

---

# 📌 Example Parameters

| Username | Password |
| -------- | -------- |
| admin    | admin123 |
| user1    | pass123  |

---

# 📌 Purpose of Parameters

* Reusable testing
* Data-driven testing
* Avoid duplicate test cases

---

# 📌 Step 18 — Configure Configurations

Open:

```text id="9b4kki"
Test Plans → Configurations
```

---

# 📌 Example Configurations

| Browser | Operating System |
| ------- | ---------------- |
| Chrome  | Windows 11       |
| Firefox | Ubuntu           |
| Edge    | Windows 11       |

---

# 📌 Purpose of Configurations

Used for:

* Cross-browser testing
* OS compatibility testing
* Device validation

---

# 📌 Step 19 — Assign Tester

Open Test Case:

```text id="q6ej9p"
Assigned To → Select User
```

---

# 📌 Step 20 — Execute Manual Test Run

Click:

```text id="pscgmi"
Run → Run for Web Application
```

---

# 📌 During Execution

Mark:

* Pass
* Fail
* Blocked
* Not Applicable

---

# 📌 Add During Test Run

* Comments
* Screenshots
* Attachments
* Bug Details

---

# 📌 Step 21 — Create Bug from Failed Test

Click:

```text id="r2p5fv"
Create Bug
```

---

# 📌 Example Bug

```text id="jlwm44"
Title: Login button not responding
Severity: High
Priority: 1
```

---

# 📌 Step 22 — View Test Runs

Open:

```text id="3ab1fu"
Test Plans → Runs
```

---

# 📌 Runs Dashboard Shows

| Metric      | Description          |
| ----------- | -------------------- |
| Total Runs  | Number of executions |
| Passed      | Successful tests     |
| Failed      | Failed tests         |
| Active Runs | Running tests        |
| Duration    | Execution time       |

---

# 📌 Step 23 — View Progress Report

Open:

```text id="hwb3gd"
Test Plans → Progress Report
```

---

# 📌 Progress Report Includes

| Report          | Description        |
| --------------- | ------------------ |
| Passed Tests    | Successful cases   |
| Failed Tests    | Failed cases       |
| Active Bugs     | Linked defects     |
| Test Trend      | Historical results |
| Tester Activity | Execution tracking |

---

# 📌 Step 24 — Link Automated Tests

Open Test Case:

```text id="pq1ic7"
Associated Automation
```

---

# 📌 Link Pipeline Test

Example:

```text id="6x7vqf"
Pipeline: Selenium Tests
```

---

# 📌 Step 25 — View Pipeline Test Results

Open:

```text id="qqsy3l"
Pipelines → Latest Run → Tests
```

---

# 📌 Available Details

* Passed Tests
* Failed Tests
* Duration
* Logs
* Screenshots
* Errors

---

# 📌 Sample CI/CD Workflow

```text id="48a4k6"
Developer Pushes Code
        ↓
Azure Repo Updated
        ↓
Pipeline Triggered
        ↓
Dependencies Installed
        ↓
PyTest + Selenium Executed
        ↓
Test Results Published
        ↓
Azure Test Plans Updated
        ↓
QA Team Reviews Reports
        ↓
Bugs Created if Failed
```

---

# 📌 Common Commands

## Install Dependencies

```bash id="h4wwyt"
pip install -r requirements.txt
```

---

## Run Tests

```bash id="jlwm55"
pytest tests/
```

---

## Generate JUnit Report

```bash id="6z8q4q"
pytest tests/ --junitxml=test-results.xml
```

---

# 📌 Important Points to Remember

* Azure Test Plans supports:

  * Manual Testing
  * Automated Testing
  * Exploratory Testing

* Parameters reduce duplicate test cases.

* Configurations enable browser validation.

* Runs maintain execution history.

* Progress Reports help QA tracking.

* Pipelines automatically publish reports.

---

# 📌 Real-Time Enhancements

## Add:

* Docker
* AKS Deployment
* GitHub Actions
* SonarQube
* Load Testing
* API Testing
* Playwright
* Security Scanning

---

# 📌 Azure DevOps Services Modules

| Service          | Purpose            |
| ---------------- | ------------------ |
| Azure Repos      | Source Code        |
| Azure Pipelines  | CI/CD              |
| Azure Test Plans | Testing            |
| Azure Boards     | Work Tracking      |
| Azure Artifacts  | Package Management |

---

# 📌 Best Practices

* Use naming standards
* Separate automation/manual suites
* Publish reports automatically
* Reuse parameters
* Maintain sprint-wise execution history
* Link bugs with failed tests

---

# 📌 Sample Interview Questions

## What is Azure Test Plans?

Azure Test Plans is a testing management solution in Microsoft [Azure DevOps Services](https://azure.microsoft.com/en-in/products/devops?utm_source=chatgpt.com) for manual and automated testing.

---

## Why Publish Test Results?

Used for:

* Quality validation
* CI/CD tracking
* Failure analysis
* Historical reporting

---

## Difference Between Manual and Automated Testing?

| Manual Testing  | Automated Testing  |
| --------------- | ------------------ |
| Human execution | Tool execution     |
| Slow            | Fast               |
| More errors     | Less errors        |
| UI validation   | Regression testing |

---

# 📌 Useful Links

* [Azure DevOps Documentation](https://learn.microsoft.com/en-us/azure/devops/?view=azure-devops&utm_source=chatgpt.com)
* [Azure Test Plans Documentation](https://learn.microsoft.com/en-us/azure/devops/test/?view=azure-devops&utm_source=chatgpt.com)
* [PyTest Documentation](https://docs.pytest.org?utm_source=chatgpt.com)
* [Selenium Documentation](https://www.selenium.dev/documentation/?utm_source=chatgpt.com)
