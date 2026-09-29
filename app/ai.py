import json

from urllib.parse import quote_plus

from google import genai

from google.genai import types

from .core import settings

from .schemas import Result


PLATFORMS = {

    "Amazon":
        "https://www.amazon.in/s?k={}",

    "Flipkart":
        "https://www.flipkart.com/search?q={}",

    "IKEA":
        "https://www.ikea.com/in/en/search/?q={}",

    "Swiggy":
        "https://www.swiggy.com/search?query={}",

    "Zomato":
        "https://www.zomato.com/search?q={}",

    "OYO":
        "https://www.oyorooms.com/search?location={}"
}


def url(platform, query):

    return PLATFORMS[
        platform
    ].format(
        quote_plus(query)
    )


def mk(planner, data):

    budget = data.budget

    if planner == "home":

        rows = [

            (
                "furniture",
                "Compact modular sofa",
                budget * 0.20,
                "Keeps seating practical."
            ),

            (
                "furniture",
                "Space-saving dining table",
                budget * 0.14,
                "Balances function and budget."
            ),

            (
                "lighting",
                "LED ceiling light set",
                budget * 0.08,
                "Efficient general lighting."
            ),

            (
                "decor",
                "Minimal wall-art set",
                budget * 0.08,
                "Adds character at low cost."
            ),

            (
                "storage",
                "Multipurpose cabinet",
                budget * 0.16,
                "Improves organization."
            )
        ]

        allocations = [
            ("Furniture", 45),
            ("Lighting", 15),
            ("Decor", 20),
            ("Storage", 20)
        ]

        title = "Home Interior Budget Plan"

        summary = (
            f"Plan for {', '.join(data.rooms)}."
        )

        providers = {
            "furniture": "IKEA",
            "lighting": "IKEA",
            "decor": "Amazon",
            "storage": "Amazon"
        }

    elif planner == "party":

        rows = [

            (
                "food",
                f"{data.event_type} catering for "
                f"{data.guests} guests",
                budget * 0.45,
                "Food scales with guest count."
            ),

            (
                "venue",
                f"Event venue near "
                f"{data.city or 'your location'}",
                budget * 0.25,
                "Controls venue cost."
            ),

            (
                "decoration",
                f"{data.event_type} decoration package",
                budget * 0.15,
                "Creates a theme."
            )
        ]

        allocations = [
            ("Food & Catering", 45),
            ("Venue", 25),
            ("Decoration", 15),
            ("Entertainment", 10),
            ("Contingency", 5)
        ]

        title = "Party Budget Plan"

        summary = (
            f"{data.event_type} plan for "
            f"{data.guests} guests."
        )

        providers = {
            "food": "Swiggy",
            "venue": "OYO",
            "decoration": "Amazon"
        }

    else:

        rows = [

            (
                "necklace",
                f"{data.style.title()} statement necklace",
                budget * 0.42,
                "Versatile centerpiece."
            ),

            (
                "earrings",
                "Matching drop earrings",
                budget * 0.25,
                "Balances the set."
            ),

            (
                "bangles",
                "Coordinated bangle set",
                budget * 0.18,
                "Finishing accent."
            )
        ]

        allocations = [
            ("Necklace", 42),
            ("Earrings", 25),
            ("Bangles", 18),
            ("Reserve", 15)
        ]

        title = "Jewelry Budget Plan"

        summary = (
            f"{data.occasion} jewelry ideas "
            f"within budget."
        )

        providers = {
            "necklace": "Amazon",
            "earrings": "Flipkart",
            "bangles": "Amazon"
        }

    recommendations = []

    for category, name, price, reason in rows:

        platform = providers[category]

        recommendations.append(
            {
                "category": category,
                "name": name,
                "platform": platform,
                "estimated_price": round(
                    price,
                    2
                ),
                "reason": reason,
                "search_url": url(
                    platform,
                    name
                )
            }
        )

    used = sum(
        item["estimated_price"]
        for item in recommendations
    )

    return Result(

        title=title,

        summary=summary,

        budget_used=used,

        budget_remaining=max(
            0,
            round(
                budget - used,
                2
            )
        ),

        allocations=[
            {
                "category": name,
                "amount": round(
                    budget * percentage / 100,
                    2
                ),
                "percentage": percentage
            }

            for name, percentage
            in allocations
        ],

        recommendations=recommendations,

        tips=[
            "Compare dimensions or quotations before purchase.",
            "Keep a contingency for delivery or unexpected costs."
        ],

        source_mode="local-fallback"
    )


class AI:

    def __init__(self):

        self.settings = settings()

        self.client = (

            genai.Client(
                api_key=self.settings.gemini_api_key
            )

            if self.settings.gemini_api_key

            else None
        )

    async def generate(
        self,
        planner,
        data,
        image=None,
        mime=None
    ):

        fallback = mk(
            planner,
            data
        )

        if not self.client:

            return fallback

        contents = [

            f"""
You are PocketSmart AI.

Create a practical budget recommendation.

Planner:
{planner}

Input:
{json.dumps(
    data.model_dump(),
    ensure_ascii=False
)}

Requirements:

1. Use Indian rupees.
2. Keep recommended spending within the budget.
3. Do not claim live inventory.
4. Do not claim live prices.
5. Marketplace names are search destinations.
6. Return only the requested JSON schema.
"""
        ]

        if image:

            contents += [

                types.Part.from_bytes(
                    data=image,
                    mime_type=mime
                ),

                (
                    "Use this image only for broad "
                    "outfit color and style coordination."
                )
            ]

        try:

            response = (
                self.client
                .models
                .generate_content(

                    model=self.settings.gemini_model,

                    contents=contents,

                    config=types.GenerateContentConfig(

                        response_mime_type="application/json",

                        response_schema=Result,

                        temperature=0.4,

                        max_output_tokens=4096
                    )
                )
            )

            parsed = getattr(
                response,
                "parsed",
                None
            )

            if isinstance(
                parsed,
                Result
            ):

                parsed.source_mode = "gemini"

                return parsed

            if getattr(
                response,
                "text",
                None
            ):

                parsed = (
                    Result
                    .model_validate_json(
                        response.text
                    )
                )

                parsed.source_mode = "gemini"

                return parsed

        except Exception:

            return fallback

        return fallback


ai = AI()