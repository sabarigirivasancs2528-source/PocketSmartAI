import json

from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    Depends,
    Form,
    File,
    UploadFile,
    HTTPException,
    Request
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from fastapi.responses import HTMLResponse

from fastapi.staticfiles import (
    StaticFiles
)

from fastapi.templating import (
    Jinja2Templates
)

from starlette.middleware.sessions import (
    SessionMiddleware
)

from sqlalchemy.orm import Session

from .core import settings

from .db import (
    init_db,
    db
)

from .models import (
    User,
    Recommendation
)

from .schemas import (
    Register,
    Home,
    Party,
    Jewelry,
    Envelope,
    Result
)

from .auth import (
    hash_pw,
    check_pw,
    norm,
    token,
    current
)

from .ai import ai


s = settings()

templates = Jinja2Templates(
    "app/templates"
)


@asynccontextmanager
async def lifespan(app):

    init_db()

    yield


app = FastAPI(

    title=s.app_name,

    version="1.0.0",

    lifespan=lifespan
)


app.add_middleware(

    CORSMiddleware,

    allow_origins=s.origins,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


app.add_middleware(

    SessionMiddleware,

    secret_key=s.secret_key,

    session_cookie=s.session_cookie_name,

    same_site="lax"
)


app.mount(

    "/static",

    StaticFiles(
        directory="app/static"
    ),

    name="static"
)


def save(
    data,
    user,
    planner,
    result,
    database
):

    recommendation = Recommendation(

        user_id=user.id,

        planner_type=planner,

        budget=data.budget,

        request_json=data.model_dump_json(),

        result_json=result.model_dump_json()
    )

    database.add(
        recommendation
    )

    database.commit()

    database.refresh(
        recommendation
    )

    return Envelope(

        id=recommendation.id,

        planner_type=planner,

        created_at=(
            recommendation
            .created_at
            .isoformat()
        ),

        result=result
    )


@app.get(
    "/",
    response_class=HTMLResponse
)
def page(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="index.html",

        context={
            "page_title": "Home"
        }
    )


@app.get(
    "/login",
    response_class=HTMLResponse
)
def login_page(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="login.html",

        context={
            "page_title": "Login"
        }
    )


@app.get(
    "/register",
    response_class=HTMLResponse
)
def register_page(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="register.html",

        context={
            "page_title": "Register"
        }
    )


@app.get(
    "/dashboard",
    response_class=HTMLResponse
)
def dashboard_page(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="dashboard.html",

        context={
            "page_title": "Dashboard"
        }
    )


@app.get(
    "/planner/home",
    response_class=HTMLResponse
)
def home_page(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="home.html",

        context={
            "page_title": "Home Planner"
        }
    )


@app.get(
    "/planner/party",
    response_class=HTMLResponse
)
def party_page(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="party.html",

        context={
            "page_title": "Party Planner"
        }
    )


@app.get(
    "/planner/jewelry",
    response_class=HTMLResponse
)
def jewelry_page(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="jewelry.html",

        context={
            "page_title": "Jewelry Planner"
        }
    )


@app.get(
    "/history",
    response_class=HTMLResponse
)
def history_page(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="history.html",

        context={
            "page_title": "History"
        }
    )


@app.get("/health")
def health():

    return {
        "status": "ok"
    }


@app.post("/register")
def register(
    data: Register,
    database: Session = Depends(db)
):

    email = norm(
        data.email
    )

    existing = database.query(
        User
    ).filter(
        User.email == email
    ).first()

    if existing:

        raise HTTPException(
            409,
            "Email already registered"
        )

    user = User(

        full_name=data.full_name.strip(),

        email=email,

        password_hash=hash_pw(
            data.password
        )
    )

    database.add(user)

    database.commit()

    database.refresh(user)

    return {

        "id": user.id,

        "full_name": user.full_name,

        "email": user.email
    }


@app.post("/token")
def login_token(

    email: str = Form(...),

    password: str = Form(...),

    database: Session = Depends(db)
):

    user = database.query(
        User
    ).filter(
        User.email == norm(email)
    ).first()

    if (
        not user
        or not check_pw(
            password,
            user.password_hash
        )
    ):

        raise HTTPException(
            401,
            "Incorrect email or password"
        )

    return {

        "access_token":
            token(user),

        "token_type":
            "bearer"
    }


@app.post("/login")
def login(

    request: Request,

    email: str = Form(...),

    password: str = Form(...),

    database: Session = Depends(db)
):

    user = database.query(
        User
    ).filter(
        User.email == norm(email)
    ).first()

    if (
        not user
        or not check_pw(
            password,
            user.password_hash
        )
    ):

        raise HTTPException(
            401,
            "Incorrect email or password"
        )

    request.session[
        "user_id"
    ] = user.id

    return {

        "message":
            "Logged in",

        "user": {

            "id": user.id,

            "full_name":
                user.full_name,

            "email":
                user.email
        }
    }


@app.post("/logout")
def logout(
    request: Request
):

    request.session.clear()

    return {
        "message":
            "Logged out"
    }


@app.get("/session-info")
def session_info(
    user=Depends(current)
):

    return {

        "authenticated":
            True,

        "user": {

            "id":
                user.id,

            "full_name":
                user.full_name,

            "email":
                user.email
        }
    }


@app.get("/session-data")
def session_data(

    user=Depends(current),

    database: Session = Depends(db)
):

    count = database.query(
        Recommendation
    ).filter(
        Recommendation.user_id
        == user.id
    ).count()

    return {

        "user": {

            "id":
                user.id,

            "full_name":
                user.full_name,

            "email":
                user.email
        },

        "recommendation_count":
            count
    }


@app.post(
    "/generate-home",
    response_model=Envelope
)
async def generate_home(

    data: Home,

    user=Depends(current),

    database: Session = Depends(db)
):

    result = await ai.generate(
        "home",
        data
    )

    return save(
        data,
        user,
        "home",
        result,
        database
    )


@app.post(
    "/generate-party",
    response_model=Envelope
)
async def generate_party(

    data: Party,

    user=Depends(current),

    database: Session = Depends(db)
):

    result = await ai.generate(
        "party",
        data
    )

    return save(
        data,
        user,
        "party",
        result,
        database
    )


@app.post(
    "/generate-jewelry",
    response_model=Envelope
)
async def generate_jewelry(

    budget: float = Form(...),

    occasion: str = Form(...),

    style: str = Form(
        "elegant"
    ),

    outfit_color: str = Form(
        ""
    ),

    notes: str = Form(
        ""
    ),

    outfit_image:
        UploadFile | None =
        File(None),

    user=Depends(current),

    database: Session =
        Depends(db)
):

    data = Jewelry(

        budget=budget,

        occasion=occasion,

        style=style,

        outfit_color=outfit_color,

        notes=notes
    )

    image = None

    mime = None

    if outfit_image:

        allowed = {

            "image/jpeg",

            "image/png",

            "image/webp"
        }

        if (
            outfit_image.content_type
            not in allowed
        ):

            raise HTTPException(
                400,
                "Only JPEG, PNG or WebP images are supported"
            )

        image = await (
            outfit_image.read()
        )

        if len(image) > 5 * 1024 * 1024:

            raise HTTPException(
                413,
                "Image exceeds 5 MB"
            )

        mime = (
            outfit_image.content_type
        )

    result = await ai.generate(

        "jewelry",

        data,

        image,

        mime
    )

    return save(

        data,

        user,

        "jewelry",

        result,

        database
    )


@app.get("/history")
def history(

    user=Depends(current),

    database: Session = Depends(db)
):

    rows = database.query(
        Recommendation
    ).filter(
        Recommendation.user_id
        == user.id
    ).order_by(
        Recommendation.created_at.desc()
    ).limit(50).all()

    return [

        {

            "id":
                row.id,

            "planner_type":
                row.planner_type,

            "budget":
                row.budget,

            "created_at":
                row.created_at.isoformat(),

            "title":
                json.loads(
                    row.result_json
                )["title"]
        }

        for row in rows
    ]


@app.get(
    "/recommendations-details/{rid}"
)
def recommendation_details(

    rid: int,

    user=Depends(current),

    database: Session = Depends(db)
):

    row = database.query(
        Recommendation
    ).filter(

        Recommendation.id == rid,

        Recommendation.user_id
        == user.id

    ).first()

    if not row:

        raise HTTPException(
            404,
            "Recommendation not found"
        )

    return {

        "id":
            row.id,

        "planner_type":
            row.planner_type,

        "created_at":
            row.created_at.isoformat(),

        "result":
            Result
            .model_validate_json(
                row.result_json
            )
            .model_dump()
    }