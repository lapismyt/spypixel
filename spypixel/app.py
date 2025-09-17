from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
from sqlmodel import create_engine, SQLModel, Session, select
from aiogram import Bot
from aiogram.types import BufferedInputFile
from .models import BadgesResponse, Badge, CreateBadge
import aiohttp
from user_agents import parse as parse_user_agent
from .utils import generate_svg_badge
import os
import random
import json

load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SECRET = os.getenv("SECRET")
DATABASE_URI = os.getenv("DATABASE_URI")

if BOT_TOKEN is None:
    raise ValueError("BOT_TOKEN is not set")

if CHAT_ID is None:
    raise ValueError("CHAT_ID is not set")

if SECRET is None:
    raise ValueError("SECRET is not set")

if DATABASE_URI is None:
    raise ValueError("DATABASE_URI is not set")

app = FastAPI()
header_scheme = APIKeyHeader(name="X-API-Key")
bot = Bot(token=BOT_TOKEN)
engine = create_engine(DATABASE_URI, echo=True)
SQLModel.metadata.create_all(engine)


async def get_ip_info(ip_address: str | None) -> dict:
    """Get IP geolocation information using ipapi.co service"""
    if not ip_address or ip_address in ["127.0.0.1", "localhost", "::1"]:
        return {"country": None, "country_code": None, "city": None, "region": None}

    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"https://ipapi.co/{ip_address}/json/") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "country": data.get("country_name"),
                        "country_code": data.get("country_code"),
                        "city": data.get("city"),
                        "region": data.get("region"),
                        "latitude": data.get("latitude"),
                        "longitude": data.get("longitude"),
                        "timezone": data.get("timezone"),
                        "org": data.get("org"),
                    }
    except Exception:
        # If the service fails, return empty data
        pass

    return {"country": None, "country_code": None, "city": None, "region": None}


@app.get("/badges")
async def get_badges(api_key: str = Depends(header_scheme)) -> BadgesResponse:
    if api_key != SECRET:
        raise HTTPException(status_code=401, detail="Invalid API key")
    with Session(engine) as session:
        badges = session.exec(select(Badge)).all()
    return BadgesResponse(badges=list(badges))


@app.post("/create")
async def create_badge(badge: CreateBadge, api_key: str = Depends(header_scheme)):
    if api_key != SECRET:
        raise HTTPException(status_code=401, detail="Invalid API key")
    with Session(engine) as session:
        new_badge = Badge(name=badge.name)
        session.add(new_badge)
        session.commit()


@app.get(
    "/badges/{badge_name}.svg",
    response_class=Response,
    responses={
        200: {"content": {"image/svg+xml": {}}},
        404: {"description": "Badge not found"},
    },
)
async def get_badge_image(badge_name: str, request: Request):
    with Session(engine) as session:
        badge = session.exec(select(Badge).where(Badge.name == badge_name)).first()
        if not badge:
            raise HTTPException(status_code=404, detail="Badge not found")

        badge.counter += 1

        session.commit()
        session.refresh(badge)

        ip_address = request.client.host if request.client else None
        user_agent_str = request.headers.get("User-Agent")

        country: str | None = None
        device_info: str | None = None
        os_info: str | None = None

        visitor_data = {
            "ip_address": ip_address,
            "user_agent": user_agent_str,
            "badge_id": badge.id,
        }

        if not user_agent_str:
            raise HTTPException(status_code=400, detail="User-Agent header is required")

        user_agent = parse_user_agent(user_agent_str)
        visitor_data["user_agent_info"] = {
            "browser_family": user_agent.browser.family,
            "browser_version": user_agent.browser.version_string,
            "os_family": user_agent.os.family,
            "os_version": user_agent.os.version_string,
            "device_family": user_agent.device.family,
            "device_brand": user_agent.device.brand,
            "is_mobile": user_agent.is_mobile,
            "is_tablet": user_agent.is_tablet,
            "is_pc": user_agent.is_pc,
            "is_bot": user_agent.is_bot,
        }

        device_info = f"{user_agent.device.family} {user_agent.device.brand}"
        os_info = f"{user_agent.os.family} {user_agent.os.version_string}"

        # Get IP geolocation information
        ip_info = await get_ip_info(ip_address)
        visitor_data["ip_info"] = ip_info
        country = ip_info.get("country")

        file_content = json.dumps(visitor_data).encode()
        file = BufferedInputFile(
            file_content, filename=f"visitor_{random.randint(100000, 99999)}.json"
        )

        text = "👀 <b>Visit info</b>\n"
        text += f"🌎 Country: {country}\n"
        text += f"📱 Device: {device_info}\n"
        text += f"💻 OS: {os_info}\n"

        await bot.send_document(
            chat_id=CHAT_ID, document=file, caption=text, parse_mode="html"
        )  # pyright: ignore[reportArgumentType]

        # svg_content = generate_svg_badge("spy", "active", color_right="#4cbb17")
        svg_content = generate_svg_badge("views", f"{badge.counter}")

        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }

        return Response(
            content=svg_content, media_type="image/svg+xml", headers=headers
        )
