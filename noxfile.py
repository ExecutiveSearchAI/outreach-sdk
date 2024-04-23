"""
Nox sessions.

Borrowed from
https://github.com/cjolowicz/cookiecutter-hypermodern-python-instance/blob/90e45cee4725c51c77864ab21efead23d5226306/noxfile.py#L26-L51
"""
from typing import Iterable

import nox
from nox.sessions import Session

targets = ["examples", "outreach_sdk", "tests", "noxfile.py", "docs/conf.py"]


def install(session: Session, groups: Iterable[str], root: bool = True) -> None:
    """Install the dependency groups using Poetry.

    This function installs the given dependency groups into the session's
    virtual environment. When ``root`` is true (the default), the function
    also installs the root package and its default dependencies.

    To avoid an editable install, the root package is not installed using
    ``poetry install``. Instead, the function invokes ``pip install .``
    to perform a PEP 517 build.

    Args:
        session: The Session object.
        groups: The dependency groups to install
        root: Install the root package
    """
    session.run_always(
        "poetry",
        "install",
        "--no-root",
        "--sync",
        "--{}={}".format("only" if not root else "with", ",".join(groups)),
        external=True,
    )
    if root:
        session.install(".")


@nox.session(python=["3.9", "3.10", "3.11"])
def lint(session: Session) -> None:
    """Lint using Flake8"""
    args = session.posargs or targets
    install(session, groups=["code-style"])
    session.run("flake8", *args)
    session.run("isort", "--check", ".")
    session.run("black", "--check", ".")


@nox.session(python=["3.9", "3.10", "3.11"])
def mypy(session: Session) -> None:
    """Type-check with mypy."""
    args = session.posargs or targets
    install(session, groups=["typing"])
    session.run("mypy", *args)


@nox.session(python=["3.9", "3.10", "3.11"])
def tests(session: Session) -> None:
    """Run the test suite."""
    groups = ["tests"]
    if "--cov" in session.posargs:
        groups.append("coverage")
    install(session, groups=groups)
    session.run("pytest", *session.posargs)


@nox.session(python="3.9")
def coverage(session: Session) -> None:
    """Upload coverage data."""
    install(session, groups=["coverage"], root=False)
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)


@nox.session(python="3.9")
def docs(session: Session) -> None:
    """Build the documentation."""
    install(session, groups=["docs"])
    session.run("sphinx-build", "docs", "docs/_build")
