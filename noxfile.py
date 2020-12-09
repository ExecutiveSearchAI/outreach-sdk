"""
Nox sessions.

Borrowed from https://github.com/cjolowicz/hypermodern-python/blob/master/noxfile.py
"""
import os
import tempfile
from typing import Any

import nox
from nox.sessions import Session


def install_with_constraints(session: Session, *args: str, **kwargs: Any) -> None:
    """Install packages constrained by Poetry's lock file.

    This function is a wrapper for nox.sessions.Session.install. It
    invokes pip to install packages inside of the session's virtualenv.
    Additionally, pip is passed a constraints file generated from
    Poetry's lock file, to ensure that the packages are pinned to the
    versions specified in poetry.lock. This allows you to manage the
    packages as Poetry development dependencies.

    Args:
        session: The Session object.
        args: Command-line arguments for pip.
        kwargs: Additional keyword arguments for Session.install.
    """
    # Windows gets mad if we try to write and then read before the file is closed.
    filename = ""
    with tempfile.NamedTemporaryFile(mode="w+t", delete=False) as requirements:
        filename = requirements.name
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={filename}",
            external=True,
        )
    session.install(f"--constraint={filename}", *args, **kwargs)
    os.remove(filename)


@nox.session(python=["3.9", "3.8", "3.7"])
def tests(session: Session) -> None:
    """Run the test suite."""
    args = session.posargs or ["--cov"]
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(session, "coverage[toml]", "pytest", "pytest-cov", "requests-mock")
    session.run("pytest", *args)


@nox.session(python="3.9")
def coverage(session: Session) -> None:
    """Upload coverage data."""
    install_with_constraints(session, "coverage[toml]", "codecov")
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)
