# SPDX-License-Identifier: Apache-2.0
import io
from unittest import mock

from bandit.formatters import github_actions


class GitHubActionsFormatterTests:
    def test_annotation_escapes_workflow_command_values(self):
        annotation = github_actions._annotation(
            {
                "filename": "src/a,b.py",
                "line_number": 12,
                "test_id": "B301:unsafe",
                "issue_severity": "HIGH",
                "issue_text": "bad % value\nsecond line",
            }
        )

        assert annotation == (
            "::error file=src/a%2Cb.py,line=12,title=B301%3Aunsafe::"
            "bad %25 value%0Asecond line"
        )

    def test_report_emits_annotations_and_skipped_files(self):
        manager = mock.Mock()
        manager.get_skipped.return_value = [("missing.py", "file not found")]
        manager.get_issue_list.return_value = [
            mock.Mock(
                **{
                    "as_dict.return_value": {
                        "filename": "app.py",
                        "line_number": 7,
                        "test_id": "B101",
                        "issue_severity": "MEDIUM",
                        "issue_text": "Use of assert detected.",
                    }
                }
            )
        ]
        output = io.StringIO()

        github_actions.report(manager, output, 1, 1)

        assert output.getvalue().splitlines() == [
            "::warning file=missing.py::Bandit skipped file: file not found",
            "::warning file=app.py,line=7,title=B101::Use of assert detected.",
        ]
        manager.get_issue_list.assert_called_once_with(
            sev_level=1, conf_level=1
        )

    def test_low_severity_uses_notice(self):
        annotation = github_actions._annotation(
            {
                "filename": "app.py",
                "line_number": 1,
                "test_id": "B999",
                "issue_severity": "LOW",
                "issue_text": "Low severity finding",
            }
        )

        assert annotation.startswith(
            "::notice file=app.py,line=1,title=B999::"
        )
