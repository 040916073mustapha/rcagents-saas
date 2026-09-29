"""Dashboard API — powers the Dark Theme analytics dashboard."""

import logging
from typing import Optional

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse

from app.database.models import SessionLocal, SaasMessage
from app.database import crud

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["dashboard"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# 🧠 AI Agents Prompts API
# ============================================================

AGENTS_META = [
    {"type": "customer_support", "name": "Customer Support", "emoji": "🤝", "icon": "fa-solid fa-headset", "color": "blue"},
    {"type": "shipping_tracking", "name": "Shipping Tracking", "emoji": "🚚", "icon": "fa-solid fa-truck-fast", "color": "amber"},
    {"type": "sales_agent", "name": "Sales Agent", "emoji": "💰", "icon": "fa-solid fa-cart-shopping", "color": "purple"},
    {"type": "inventory_agent", "name": "Inventory Agent", "emoji": "📦", "icon": "fa-solid fa-warehouse", "color": "emerald"},
    {"type": "campaign_agent", "name": "Campaign Agent", "emoji": "🎯", "icon": "fa-solid fa-bullhorn", "color": "pink"},
    {"type": "analytics_agent", "name": "Analytics Agent", "emoji": "📊", "icon": "fa-solid fa-chart-line", "color": "cyan"},
    {"type": "engagement_agent", "name": "Engagement Agent", "emoji": "💕", "icon": "fa-solid fa-heart", "color": "rose"},
]


@router.get("/agents/prompts")
async def api_agents_prompts(store_id: int = Query(1)):
    """GET: جميع Prompts الـ AI Agents مع البيانات الوصفية"""
    db = next(get_db())
    try:
        prompts = crud.get_all_store_prompts(db, store_id)
        result = []
        for agent in AGENTS_META:
            result.append({
                **agent,
                "prompt": prompts.get(agent["type"], ""),
            })
        return {"success": True, "agents": result, "store_id": store_id}
    except Exception as e:
        logger.exception(f"[AGENTS API] GET error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/agents/prompts/{agent_type}")
async def api_agent_prompt_by_type(agent_type: str, store_id: int = Query(1)):
    """GET: جلب Prompt لـ Agent معين"""
    db = next(get_db())
    try:
        prompt = crud.get_store_prompt(db, store_id, agent_type)
        return {"success": True, "agent_type": agent_type, "prompt": prompt or "", "store_id": store_id}
    except Exception as e:
        logger.exception(f"[AGENTS API] GET {agent_type} error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/agents/promptssave")
async def api_agents_promptssave(store_id: int = Query(1), agent_type: str = Query(""), prompt_text: str = Query("")):
    """GET: حفظ Prompt (نسخة GET للـ Dashboard الأمامي)"""
    db = next(get_db())
    try:
        if not agent_type:
            return {"success": False, "error": "agent_type is required"}
        crud.set_store_prompt(db, store_id, agent_type, prompt_text)
        logger.info(f"[AGENTS API] Saved prompt for {agent_type} (store_id={store_id})")
        return {"success": True, "agent_type": agent_type, "store_id": store_id}
    except Exception as e:
        logger.exception(f"[AGENTS API] SAVE error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


# ============================================================
# 💬 SaasMessages API (Live Chat)
# ============================================================

@router.get("/messages")
async def api_messages(store_id: int = Query(1), limit: int = Query(200), offset: int = Query(0)):
    """GET: جلب جميع الرسائل للمحادثات الحية"""
    db = next(get_db())
    try:
        msgs = crud.list_saas_messages(db, store_id, limit=limit, offset=offset)
        return {
            "success": True,
            "messages": [
                {
                    "id": m.id,
                    "platform": m.platform,
                    "sender_id": m.sender_id,
                    "sender_name": m.sender_name or "",
                    "message": m.message,
                    "reply": m.reply,
                    "direction": m.direction,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in msgs
            ],
            "store_id": store_id,
            "count": len(msgs),
        }
    except Exception as e:
        logger.exception(f"[MESSAGES API] GET error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/messages")
async def api_save_message(data: dict):
    """POST: حفظ رسالة جديدة"""
    db = next(get_db())
    try:
        store_id = data.get("store_id", 1)
        platform = data.get("platform", "")
        sender_id = data.get("sender_id", "")
        message = data.get("message")
        reply = data.get("reply")
        direction = data.get("direction")
        sender_name = data.get("sender_name")
        mid = data.get("mid")
        msg = crud.save_saas_message(
            db, store_id, platform, sender_id,
            message=message, reply=reply,
            direction=direction, sender_name=sender_name, mid=mid
        )
        return {
            "success": True,
            "message": {
                "id": msg.id,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            }
        }
    except Exception as e:
        logger.exception(f"[MESSAGES API] POST error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/dashboard/stats")
async def dashboard_stats(store_id: int = Query(1, description="Tenant store ID")):
    """Return dashboard aggregate stats for a store."""
    db = next(get_db())
    try:
        orders = crud.list_recent_orders(db, store_id, limit=1000)
        total_revenue = sum(o.total_price or 0 for o in orders)
        total_orders = len(orders)
        fulfilled = sum(1 for o in orders if o.fulfillment_status == "fulfilled")
        
        return {
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders,
            "fulfilled_orders": fulfilled,
            "pending_orders": total_orders - fulfilled,
            "currency": "DZD",
        }
    except Exception as e:
        logger.exception(f"[Dashboard] Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/dashboard/recent-orders")
async def recent_orders(store_id: int = Query(1), limit: int = Query(10)):
    """Return recent orders for the dashboard table."""
    db = next(get_db())
    try:
        orders = crud.list_recent_orders(db, store_id, limit=limit)
        return [
            {
                "id": o.id,
                "shopify_order_id": o.shopify_order_id,
                "customer_name": o.customer_name,
                "total_price": o.total_price,
                "financial_status": o.financial_status,
                "fulfillment_status": o.fulfillment_status,
                "created_at": o.created_at.isoformat() if o.created_at else None,
            }
            for o in orders
        ]
    except Exception as e:
        logger.exception(f"[Dashboard] Recent orders error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/dashboard/conversations")
async def active_conversations(store_id: int = Query(1), limit: int = Query(20)):
    """Return active conversations for the live chat inbox."""
    db = next(get_db())
    try:
        convs = crud.list_active_conversations(db, store_id, limit=limit)
        return [
            {
                "id": c.id,
                "platform": c.platform,
                "last_message": c.last_message,
                "last_activity": c.last_activity.isoformat() if c.last_activity else None,
                "agent_handled": c.agent_handled,
            }
            for c in convs
        ]
    except Exception as e:
        logger.exception(f"[Dashboard] Conversations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
