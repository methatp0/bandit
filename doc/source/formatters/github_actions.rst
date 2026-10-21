GitHub Actions
==============

The GitHub Actions formatter emits workflow-command annotations for each
finding. GitHub displays these as annotations in the Actions log and, when
the workflow has the relevant permissions and context, alongside changed
files in pull requests.

Run Bandit with the ``github-actions`` formatter:

.. code-block:: console

    bandit -f github-actions -r .

High-severity findings are emitted as ``error`` annotations, medium-severity
findings as ``warning`` annotations, and low-severity findings as ``notice``
annotations. Skipped files are reported as warnings. File paths, titles, and
messages are escaped according to GitHub Actions workflow-command syntax.

See the `GitHub Actions workflow commands documentation
<https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-error-message>`_
for details about annotations.
