# SPDX-License-Identifier: Apache-2.0
import io
import unittest
from unittest import mock

from bandit.formatters import github_actions


class GitHubActionsFormatterTests(unittest.TestCase):
    def test_annotation_escapes_values_and_includes_same_line_columns(self):
        annotation = github_actions._annotation(
            {
                "filename": "src/a,b.py",
                "line_number": 12,
                "line_range": [12],
                "col_offset": 7,
                "end_col_offset": 15,
                "test_id": "B301:unsafe",
                "issue_severity": "HIGH",
                "issue_text": "bad % value\nsecond line",
            }
        )

        self.assertEqual(
            annotation,
            "::error file=src/a%2Cb.py,line=12,endLine=12,col=8,"
            "endColumn=15,title=B301%3Aunsafe::"
            "bad %25 value%0Asecond line",
        )

    def test_multiline_annotation_omits_columns(self):
        annotation = github_actions._annotation(
            {
                "filename": "app.py",
                "line_number": 7,
                "line_range": [7, 8],
                "col_offset": 3,
                "end_col_offset": 10,
                "test_id": "B301",
                "issue_severity": "HIGH",
                "issue_text": "Potential issue",
            }
        )

        self.assertEqual(
            annotation,
            "::error file=app.py,line=7,endLine=8,title=B301::Potential issue",
        )

    def test_file_level_annotation_omits_invalid_line_zero(self):
        annotation = github_actions._annotation(
            {
                "filename": "app.py",
                "line_number": 0,
                "line_range": [0, 1],
                "col_offset": 0,
                "end_col_offset": 0,
                "test_id": "B999",
                "issue_severity": "LOW",
                "issue_text": "File-level finding",
            }
        )

        self.assertEqual(
            annotation, "::notice file=app.py,title=B999::File-level finding"
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
                        "line_range": [7],
                        "col_offset": -1,
                        "end_col_offset": 0,
                        "test_id": "B101",
                        "issue_severity": "MEDIUM",
                        "issue_text": "Use of assert detected.",
                    }
                }
            )
        ]
        output = io.StringIO()

        github_actions.report(manager, output, 1, 1)

        self.assertEqual(
            output.getvalue().splitlines(),
            [
                (
                    "::warning file=missing.py::Bandit skipped file: "
                    "file not found"
                ),
                "::warning file=app.py,line=7,endLine=7,title=B101::"
                "Use of assert detected.",
            ],
        )
        manager.get_issue_list.assert_called_once_with(
            sev_level=1, conf_level=1
        )

    def test_low_severity_defaults_to_notice(self):
        annotation = github_actions._annotation(
            {
                "filename": "app.py",
                "line_number": 1,
                "test_id": "B999",
                "issue_severity": "LOW",
                "issue_text": "Low severity finding",
            }
        )

        self.assertTrue(
            annotation.startswith("::notice file=app.py,line=1,title=B999::")
        )
