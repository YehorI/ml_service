class HaveNoSessionError(RuntimeError):
    """Raised when accessing the session outside of a transaction context."""

    def __init__(self) -> None:
        super().__init__(
            "No active database session. Use SQLAlchemyService.transaction() context manager."
        )
