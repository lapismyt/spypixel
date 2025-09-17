from sqlmodel import SQLModel, Field, JSON


class Badge(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str | None = Field(default=None, unique=True)
    counter: int = Field(default=0)


class BadgesResponse(SQLModel, table=False):
    badges: list[Badge] = Field(default=None, sa_type=JSON)


class CreateBadge(SQLModel, table=False):
    name: str | None = Field(default=None)
