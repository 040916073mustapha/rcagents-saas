"""CRUD operations with explicit type casting & store_id scoping — no silent failures."""

import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from app.database.models import Tenant, Order, Customer, Product, Conversation, StorePrompt, SaasMessage


# ── Tenants ──────────────────────────────────────────────────

def get_tenant_by_slug(db: Session, slug: str) -> Optional[Tenant]:
    return db.query(Tenant).filter(Tenant.slug == str(slug)).first()


def get_tenant_by_id(db: Session, store_id: int) -> Optional[Tenant]:
    return db.query(Tenant).filter(Tenant.id == store_id).first()


def list_active_tenants(db: Session) -> List[Tenant]:
    return db.query(Tenant).filter(Tenant.is_active == True).all()


def create_tenant(db: Session, slug: str, store_name: str, **kwargs) -> Tenant:
    tenant = Tenant(slug=str(slug), store_name=str(store_name), **kwargs)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


# ── Orders ─────────────────────────────────────────────────────

def get_order(db: Session, store_id: int, order_id: int) -> Optional[Order]:
    return db.query(Order).filter(
        Order.store_id == store_id, Order.id == order_id
    ).first()


def get_order_by_shopify_id(db: Session, store_id: int, shopify_order_id: str) -> Optional[Order]:
    return db.query(Order).filter(
        Order.store_id == store_id,
        Order.shopify_order_id == str(shopify_order_id)
    ).first()


def upsert_order(db: Session, store_id: int, shopify_order_id: str, data: dict) -> Order:
    order = get_order_by_shopify_id(db, store_id, shopify_order_id)
    if order:
        for key, value in data.items():
            if hasattr(order, key):
                setattr(order, key, value)
        order.updated_at = datetime.datetime.utcnow()
    else:
        order = Order(store_id=store_id, shopify_order_id=str(shopify_order_id), **data)
        db.add(order)
    db.commit()
    db.refresh(order)
    return order


def list_recent_orders(db: Session, store_id: int, limit: int = 20) -> List[Order]:
    return db.query(Order).filter(Order.store_id == store_id).order_by(
        Order.created_at.desc()
    ).limit(limit).all()


# ── Customers ───────────────────────────────────────────────────

def get_customer_by_platform_id(
    db: Session, store_id: int, platform: str, platform_user_id: str
) -> Optional[Customer]:
    return db.query(Customer).filter(
        Customer.store_id == store_id,
        Customer.platform == str(platform),
        Customer.platform_user_id == str(platform_user_id)
    ).first()


def upsert_customer(
    db: Session, store_id: int, platform: str, platform_user_id: str, data: dict
) -> Customer:
    customer = get_customer_by_platform_id(db, store_id, platform, platform_user_id)
    if customer:
        for key, value in data.items():
            if hasattr(customer, key):
                setattr(customer, key, value)
        customer.updated_at = datetime.datetime.utcnow()
    else:
        customer = Customer(
            store_id=store_id, platform=str(platform),
            platform_user_id=str(platform_user_id), **data
        )
        db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


# ── Products ────────────────────────────────────────────────────

def get_product_by_shopify_id(db: Session, store_id: int, shopify_product_id: str) -> Optional[Product]:
    return db.query(Product).filter(
        Product.store_id == store_id,
        Product.shopify_product_id == str(shopify_product_id)
    ).first()


def upsert_product(db: Session, store_id: int, shopify_product_id: str, data: dict) -> Product:
    product = get_product_by_shopify_id(db, store_id, shopify_product_id)
    if product:
        for key, value in data.items():
            if hasattr(product, key):
                setattr(product, key, value)
        product.updated_at = datetime.datetime.utcnow()
    else:
        product = Product(store_id=store_id, shopify_product_id=str(shopify_product_id), **data)
        db.add(product)
    db.commit()
    db.refresh(product)
    return product


def list_active_products(db: Session, store_id: int, limit: int = 50) -> List[Product]:
    return db.query(Product).filter(
        Product.store_id == store_id, Product.is_active == True
    ).limit(limit).all()


# ── Conversations ───────────────────────────────────────────────

def get_conversation(
    db: Session, store_id: int, platform: str, platform_conversation_id: str
) -> Optional[Conversation]:
    return db.query(Conversation).filter(
        Conversation.store_id == store_id,
        Conversation.platform == str(platform),
        Conversation.platform_conversation_id == str(platform_conversation_id)
    ).first()


def upsert_conversation(
    db: Session, store_id: int, platform: str, platform_conversation_id: str, data: dict
) -> Conversation:
    conv = get_conversation(db, store_id, platform, platform_conversation_id)
    if conv:
        for key, value in data.items():
            if hasattr(conv, key):
                setattr(conv, key, value)
        conv.last_activity = datetime.datetime.utcnow()
    else:
        conv = Conversation(
            store_id=store_id, platform=str(platform),
            platform_conversation_id=str(platform_conversation_id), **data
        )
        db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


def list_active_conversations(db: Session, store_id: int, limit: int = 50) -> List[Conversation]:
    return db.query(Conversation).filter(
        Conversation.store_id == store_id, Conversation.is_active == True
    ).order_by(Conversation.last_activity.desc()).limit(limit).all()


# ── Store Prompts (AI Agent System Prompts) ────────────

def get_store_prompt(db: Session, store_id: int, agent_type: str) -> Optional[str]:
    """Get the system prompt for a specific agent type."""
    row = db.query(StorePrompt).filter(
        StorePrompt.store_id == store_id,
        StorePrompt.agent_type == str(agent_type)
    ).first()
    return row.prompt_text if row else None


def set_store_prompt(db: Session, store_id: int, agent_type: str, prompt_text: str) -> StorePrompt:
    """Create or update system prompt for a specific agent type."""
    row = db.query(StorePrompt).filter(
        StorePrompt.store_id == store_id,
        StorePrompt.agent_type == str(agent_type)
    ).first()
    if row:
        row.prompt_text = prompt_text
        row.updated_at = datetime.datetime.utcnow()
    else:
        row = StorePrompt(
            store_id=store_id,
            agent_type=str(agent_type),
            prompt_text=prompt_text,
        )
        db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_all_store_prompts(db: Session, store_id: int) -> dict:
    """Get all agent prompts as {agent_type: prompt_text} dict."""
    rows = db.query(StorePrompt).filter(StorePrompt.store_id == store_id).all()
    return {r.agent_type: r.prompt_text for r in rows}


# ── SaasMessages (Live Chat) ────────────────────────────

def save_saas_message(db: Session, store_id: int, platform: str, sender_id: str,
                      message: str = None, reply: str = None, direction: str = None,
                      sender_name: str = None, mid: str = None) -> SaasMessage:
    """Save a chat message (inbound or outbound)."""
    msg = SaasMessage(
        store_id=store_id,
        platform=str(platform),
        sender_id=str(sender_id),
        sender_name=sender_name,
        message=message,
        reply=reply,
        direction=direction or ("inbound" if message else "outbound"),
        mid=mid,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def list_saas_messages(db: Session, store_id: int, limit: int = 200, offset: int = 0) -> List[SaasMessage]:
    """List messages ordered by most recent first."""
    return db.query(SaasMessage).filter(
        SaasMessage.store_id == store_id
    ).order_by(SaasMessage.created_at.desc()).offset(offset).limit(limit).all()
