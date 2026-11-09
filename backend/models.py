
from sqlmodel import SQLModel, Field  # type: ignore[reportMissingImports]


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    username: str = Field(
        index=True,
        unique=True,
        max_length=30,
    )

    password_hash: str

    university: str = Field(max_length=120)
    field_of_study: str = Field(max_length=120)


class AuthSession(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id", index=True)

    token_hash: str = Field(index=True, unique=True)

    expires_at: int
