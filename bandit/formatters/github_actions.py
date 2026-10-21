# SPDX-License-Identifier: Apache-2.0
"""GitHub Actions workflow-command formatter.

This formatter emits annotations that GitHub displays inline in pull requests
and in the Actions log. See:
https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions
"""

import logging

from bandit.core import test_properties

LOG = logging.getLogger(__name__)


def _escape_property(value):
    """Escape a workflow-command property value."""
    return (
        str(value)
        .replace("%", "%25")
        .replace("\r", "%0D")
        .replace("\n", "%0A")
        .replace(":", "%3A")
        .replace(",", "%2C")
    )


def _escape_message(value):
    """Escape a workflow-command message."""
    return (
        str(value)
        .replace("%", "%25")
        .replace("\r", "%0D")
        .replace("\n", "%0A")
    )


def _annotation(issue):
    severity = issue.get("issue_severity", "LOW").upper()
    level = {
        "HIGH": "error",
        "MEDIUM": "warning",
        "LOW": "notice",
        "UNDEFINED": "notice",
    }.get(severity, "notice")

    properties = []
    filename = issue.get("filename")
    if filename:
        properties.append(f"file={_escape_property(filename)}")

    line = issue.get("line_number")
    if line is not None:
        properties.append(f"line={int(line)}")

    test_id = issue.get("test_id")
    if test_id:
        properties.append(f"title={_escape_property(test_id)}")

    metadata = " " + ",".join(properties) if properties else ""
    message = _escape_message(issue.get("issue_text", "Bandit finding"))
    return f"::{level}{metadata}::{message}"


@test_properties.accepts_baseline
def report(manager, fileobj, sev_level, conf_level, lines=-1):
    """Write Bandit findings as GitHub Actions annotations."""
    for filename, reason in manager.get_skipped():
        metadata = f" file={_escape_property(filename)}" if filename else ""
        message = _escape_message(f"Bandit skipped file: {reason}")
        fileobj.write(f"::warning{metadata}::{message}\n")

    results = manager.get_issue_list(
        sev_level=sev_level, conf_level=conf_level
    )
    if not isinstance(results, list):
        # Baseline output groups matching findings into a mapping.
        issues = []
        for baseline_issue, candidates in results.items():
            issues.extend(candidates if candidates else [baseline_issue])
    else:
        issues = results

    for item in issues:
        data = item.as_dict(max_lines=lines)
        fileobj.write(_annotation(data) + "\n")

    if hasattr(fileobj, "name") and fileobj.name not in ("<stdout>", "<stderr>"):
        LOG.info("GitHub Actions annotations written to file: %s", fileobj.name)
