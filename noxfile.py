import nox
from nox.sessions import Session


@nox.session(python=["3.9", "3.8", "3.7"])
def tests(session: Session) -> None:
    session.run("poetry", "install", external=True)
    session.run("pytest", "--cov")
