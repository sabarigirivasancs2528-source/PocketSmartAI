from pydantic import BaseModel, Field


class Register(BaseModel):

    full_name: str = Field(
        min_length=2,
        max_length=120
    )

    email: str = Field(
        min_length=5,
        max_length=255
    )

    password: str = Field(
        min_length=8,
        max_length=128
    )


class Home(BaseModel):

    budget: float = Field(
        gt=0
    )

    rooms: list[str] = Field(
        min_length=1
    )

    items: dict[str, int] = {}

    style: str = "modern"

    priorities: str = (
        "functionality, style, value"
    )


class Party(BaseModel):

    budget: float = Field(
        gt=0
    )

    guests: int = Field(
        gt=0
    )

    event_type: str = Field(
        min_length=2
    )

    venue: str = "flexible"

    city: str = ""

    preferences: str = ""


class Jewelry(BaseModel):

    budget: float = Field(
        gt=0
    )

    occasion: str = Field(
        min_length=2
    )

    style: str = "elegant"

    outfit_color: str = ""

    notes: str = ""


class Item(BaseModel):

    category: str

    name: str

    platform: str

    estimated_price: float

    reason: str

    search_url: str


class Allocation(BaseModel):

    category: str

    amount: float

    percentage: float


class Result(BaseModel):

    title: str

    summary: str

    budget_used: float

    budget_remaining: float

    allocations: list[Allocation] = []

    recommendations: list[Item] = []

    tips: list[str] = []

    source_mode: str = "ai"


class Envelope(BaseModel):

    id: int

    planner_type: str

    created_at: str

    result: Result