import json
import random
from datetime import datetime, timedelta

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import create_engine, func, select, insert
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from starlette.responses import JSONResponse, RedirectResponse

DATABASE_URL: str = "sqlite:///data/tracker.db"
engine = create_engine(DATABASE_URL, echo=True)

Base = declarative_base()

class Metrics(Base):
    __tablename__: str = "metrics"
    id: Mapped[int] = mapped_column(primary_key=True)
    measured_at: Mapped[datetime] = mapped_column(default=datetime.now())
    weight: Mapped[float]
    waist_circ: Mapped[float]
    chest_circ: Mapped[float]
    bicep_circ: Mapped[float]
    hip_circ: Mapped[float]
    p_len: Mapped[float]

Base.metadata.create_all(engine)
Metrics.metadata.create_all(engine)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# @app.get("/{name}", response_class=HTMLResponse)
# async def index(request: Request, name: str):
#     return templates.TemplateResponse(
#         request=request, name="index.html", context={"name": name}
#     )
#

def random_date(start_date: datetime = datetime(2026, 1, 1, 0 , 0 , 0), end_date: datetime= datetime.now()) -> datetime:
    delta = end_date - start_date
    rand_seconds = random.randint(0, int(delta.total_seconds()))
    return start_date + timedelta(seconds=rand_seconds)

# for i in range(20):
#     stmt = insert(Metrics).values(
#             measured_at=random_date(),
#             weight=random.uniform(0, 250),
#             waist_circ=random.uniform(0, 250),
#             chest_circ=random.uniform(0, 250),
#             bicep_circ=random.uniform(0, 250),
#             hip_circ=random.uniform(0, 250),
#             p_len=random.uniform(0, 8),
#         )
#     with engine.connect() as conn:
#         conn.execute(stmt)
#         conn.commit()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    re_stmt = select(Metrics)
    with engine.connect() as conn:
            result = conn.execute(re_stmt)
            print(f"res: {result}")
            rows_as_dict = [row._asdict() for row in result]
            print(rows_as_dict)
    metrics_json = json.dumps(rows_as_dict, default=str)
    return templates.TemplateResponse(request=request, name="index.html", context={"rows": metrics_json})

@app.post("/log")
async def log_metric(
    weight: float = Form(...),
    waist_circ: float = Form(...),
    chest_circ: float = Form(...),
    bicep_circ: float = Form(...),
    hip_circ: float = Form(...),
    p_len: float = Form(...)
):
    log_stmt = insert(Metrics).values(
        weight=weight,
        waist_circ=waist_circ,
        chest_circ=chest_circ,
        bicep_circ=bicep_circ,
        hip_circ=hip_circ,
        p_len=p_len
    )

    with engine.connect() as conn:
        conn.execute(log_stmt)
        conn.commit()

    return RedirectResponse(url="/", status_code=303)