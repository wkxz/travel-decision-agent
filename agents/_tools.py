"""
Agent Tools — private module (starts with _), not mapped as a route.

出行决策 Agent 的工具集，基于高德地图 Web 服务 API。

设计原则：
  1. 所有 Key 只从环境变量 AMAP_API_KEY 读取，绝不硬编码、绝不打印。
  2. 地点、门店、距离一律以高德接口返回为准，不交给模型自行生成。
  3. 工具描述里写清「什么时候调用」，保证 Agent 在正确场景选中正确接口。

替换说明：本文件原为 Starter 的四个示例工具（get_weather / get_clothing_advice /
translate_text / text_statistics），已按课程要求整体替换为出行决策工具链。
"""

import json
import os
import threading
import time
from typing import Annotated

import httpx
from agents import function_tool

AMAP_BASE = "https://restapi.amap.com/v3"
TIMEOUT = 10.0

# 高德免费版 Web 服务 Key 的 QPS 很低（并发稍高就返回 10021）。
# 用「最小请求间隔 + 退避重试」兜住，避免 Agent 连续核对多个商场时被限流。
MIN_INTERVAL = 0.35
_qps_lock = threading.Lock()
_last_call_at = 0.0

# 高德 POI 分类码：购物服务 > 商场 > 购物中心
SHOPPING_MALL_TYPE = "060100"

QPS_EXCEEDED = "10021"


def _throttle() -> None:
    """全局最小请求间隔，避免触发高德 QPS 限流。"""
    global _last_call_at
    with _qps_lock:
        gap = MIN_INTERVAL - (time.monotonic() - _last_call_at)
        if gap > 0:
            time.sleep(gap)
        _last_call_at = time.monotonic()


def _amap_get(path: str, params: dict, retries: int = 3) -> dict:
    """统一的 GET 封装：注入 Key、节流、QPS 退避重试、校验高德 status。

    高德约定 status == "1" 为成功，"0" 为失败（此时 info / infocode 里有原因）。
    错误一律以 {"error": "..."} 形式返回，让模型能向用户解释失败原因。
    """
    key = os.getenv("AMAP_API_KEY")
    if not key:
        return {"error": "AMAP_API_KEY 未配置：请在 .env 中填写高德 Web 服务 Key"}

    last_error = ""
    for attempt in range(retries):
        _throttle()
        try:
            resp = httpx.get(
                f"{AMAP_BASE}{path}",
                params={"key": key, **params},
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as e:
            last_error = f"高德接口请求失败：{type(e).__name__}: {e}"
            time.sleep(0.6 * (attempt + 1))
            continue
        except ValueError:
            return {"error": "高德接口返回了非 JSON 内容，请稍后重试"}

        if str(data.get("status")) == "1":
            return data

        info = f"{data.get('info')}（infocode={data.get('infocode')}）"
        # QPS 超限是可恢复的，退避后重试；其余错误直接返回
        if str(data.get("infocode")) == QPS_EXCEEDED and attempt < retries - 1:
            last_error = f"高德接口限流，已重试 {attempt + 1} 次：{info}"
            time.sleep(1.0 * (attempt + 1))
            continue
        return {"error": f"高德接口返回错误：{info}"}

    return {"error": last_error or "高德接口连续失败，请稍后重试"}


def _to_int(value: object) -> int | None:
    """高德的距离字段有时是字符串、有时是空列表，统一成 int 或 None。"""
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


# ========== Tool 1: 地点解析 ==========
@function_tool
def geocode_location(
    address: Annotated[str, "要解析的地点名称或地址，例如「红莲南路地铁站」「北京市朝阳区建国路87号」"],
    city: Annotated[str, "可选。限定城市名或 citycode，能显著提高解析准确率；不确定时留空"] = "",
) -> str:
    """把用户口语描述的地点解析成经纬度坐标。

    任何基于位置的检索都必须先调用本工具拿到坐标，再调用其他工具。
    如果解析失败或结果过于宽泛，应让用户补充城市或更精确的地址。
    """
    params: dict = {"address": address}
    if city:
        params["city"] = city

    data = _amap_get("/geocode/geo", params)
    if "error" in data:
        return json.dumps(data, ensure_ascii=False)

    geocodes = data.get("geocodes") or []
    if not geocodes:
        return json.dumps(
            {"error": f"无法解析地点「{address}」。请向用户确认城市或更精确的地址。"},
            ensure_ascii=False,
        )

    g = geocodes[0]
    return json.dumps(
        {
            "query": address,
            "formatted_address": g.get("formatted_address"),
            "location": g.get("location"),
            "province": g.get("province"),
            "city": g.get("city"),
            "district": g.get("district"),
            "level": g.get("level"),
        },
        ensure_ascii=False,
    )


# ========== Tool 2: 搜索附近商场 ==========
@function_tool
def search_nearby_malls(
    location: Annotated[str, "中心点坐标，格式为 lng,lat，来自 geocode_location 的返回值"],
    radius: Annotated[int, "搜索半径，单位米。默认 3000，最大 50000"] = 3000,
    keyword: Annotated[str, "可选。商场名称关键词，例如「万达」「大悦城」；用户没有指定时留空"] = "",
) -> str:
    """按坐标搜索附近的购物中心，返回按距离升序排列的候选商场列表。

    每个结果包含名称、地址、坐标、与中心点的直线距离（米）。这是推荐流程的第一步，
    拿到候选列表后再逐个用 check_brand_in_mall 核对品牌。
    """
    params: dict = {
        "location": location,
        "types": SHOPPING_MALL_TYPE,
        "radius": max(1, min(int(radius), 50000)),
        "offset": 25,
        "page": 1,
        "sortrule": "distance",
        "extensions": "all",
    }
    if keyword:
        params["keywords"] = keyword

    data = _amap_get("/place/around", params)
    if "error" in data:
        return json.dumps(data, ensure_ascii=False)

    malls = []
    for poi in data.get("pois") or []:
        malls.append(
            {
                "name": poi.get("name"),
                "address": poi.get("address"),
                "location": poi.get("location"),
                "distance_m": _to_int(poi.get("distance")),
                "type": poi.get("type"),
                "tel": poi.get("tel") if poi.get("tel") else None,
            }
        )

    return json.dumps(
        {
            "center": location,
            "radius_m": params["radius"],
            "count": len(malls),
            "malls": malls,
        },
        ensure_ascii=False,
    )


# ========== Tool 3: 核对品牌是否在商场内 ==========
@function_tool
def check_brand_in_mall(
    mall_location: Annotated[str, "商场坐标，格式 lng,lat，来自 search_nearby_malls 的结果"],
    brand: Annotated[str, "要核对的品牌或门店名，例如「倍轻松」「西厅村屋」"],
    radius: Annotated[int, "认定「位于该商场内」的半径，单位米。默认 300，商场体量大时可放宽到 500"] = 300,
) -> str:
    """核对某个商场内是否存在指定品牌的门店。

    以商场坐标为圆心做小半径 POI 搜索：命中即认为该品牌在该商场内（高德不提供
    「商场包含哪些店铺」的直接接口，这是行业通用的等效做法）。
    返回 matched 布尔值、命中的门店名与距离，供 Agent 判断是否满足用户的品牌要求。
    """
    params: dict = {
        "location": mall_location,
        "keywords": brand,
        "radius": max(50, min(int(radius), 50000)),
        "offset": 10,
        "page": 1,
        "sortrule": "distance",
    }

    data = _amap_get("/place/around", params)
    if "error" in data:
        return json.dumps(data, ensure_ascii=False)

    hits = []
    for poi in data.get("pois") or []:
        hits.append(
            {
                "name": poi.get("name"),
                "address": poi.get("address"),
                "distance_m": _to_int(poi.get("distance")),
                "type": poi.get("type"),
            }
        )

    return json.dumps(
        {
            "brand": brand,
            "mall_location": mall_location,
            "radius_m": params["radius"],
            "matched": len(hits) > 0,
            "stores": hits,
        },
        ensure_ascii=False,
    )


# ========== Tool 4: 测量距离 ==========
@function_tool
def measure_distance(
    origin: Annotated[str, "起点坐标，格式 lng,lat"],
    destination: Annotated[str, "终点坐标，格式 lng,lat"],
    mode: Annotated[str, "距离类型：straight 为直线距离，driving 为驾车距离。默认 straight"] = "straight",
) -> str:
    """测量两点之间的距离，返回米数与公里数。

    所有对外给出的距离数字都必须来自本工具的返回值，不要自行估算或换算。
    当多个候选商场都满足品牌要求时，用它来比较远近并排序。
    """
    # 高德 /v3/distance：type 0=直线距离，1=驾车距离，3=步行距离
    type_code = {"straight": 0, "driving": 1}.get(str(mode).lower(), 0)

    data = _amap_get(
        "/distance",
        {"origins": origin, "destination": destination, "type": type_code},
    )
    if "error" in data:
        return json.dumps(data, ensure_ascii=False)

    results = data.get("results") or []
    if not results:
        return json.dumps({"error": "距离接口未返回结果，请检查坐标格式是否为 lng,lat"}, ensure_ascii=False)

    meters = _to_int(results[0].get("distance"))
    return json.dumps(
        {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "distance_m": meters,
            "distance_km": round(meters / 1000, 2) if meters is not None else None,
            "duration_s": _to_int(results[0].get("duration")) if type_code == 1 else None,
        },
        ensure_ascii=False,
    )
