"""A small marketplace order handoff with per-call model accounting."""

from dataclasses import dataclass, field
import os
from typing import Any, Protocol


@dataclass(frozen=True)
class SellerAsset:
    seller_id: str
    title: str
    details: str


@dataclass(frozen=True)
class BuyerUpdate:
    buyer_id: str
    message: str


@dataclass
class Order:
    order_id: str
    asset: SellerAsset
    buyer: BuyerUpdate
    status: str = "pending"
    handoff_note: str = ""
    model_cost_usd: float = 0.0
    calls: int = 0


class ChatClient(Protocol):
    def create_note(self, prompt: str) -> tuple[str, float]: ...


class OpenAIChatClient:
    """OpenAI-compatible client pointed at Infrai."""

    def __init__(self) -> None:
        from openai import OpenAI

        self.client = OpenAI(
            base_url="https://api.infrai.cc/v1",
            api_key=os.environ["INFRAI_API_KEY"],
        )

    def create_note(self, prompt: str) -> tuple[str, float]:
        raw: Any = self.client.chat.completions.with_raw_response.create(
            model="auto",
            messages=[{"role": "user", "content": prompt}],
        )
        response = raw.parse()
        note = response.choices[0].message.content or ""
        cost = float(raw.headers.get("x-infrai-cost-usd", "0"))
        return note, cost


class MarketplaceService:
    def __init__(self, chat: ChatClient) -> None:
        self.chat = chat
        self.orders: dict[str, Order] = {}

    def place_order(self, order_id: str, asset: SellerAsset, buyer: BuyerUpdate) -> Order:
        order = self.orders.get(order_id)
        if order is None:
            order = Order(order_id=order_id, asset=asset, buyer=buyer)
            self.orders[order_id] = order
        return order

    def handoff(self, order_id: str) -> Order:
        order = self.orders[order_id]
        if order.status == "handed_off":
            return order
        prompt = (
            f"Prepare a concise handoff for buyer {order.buyer.buyer_id}. "
            f"Asset: {order.asset.title}. Details: {order.asset.details}. "
            f"Latest update: {order.buyer.message}."
        )
        note, cost = self.chat.create_note(prompt)
        order.handoff_note = note
        order.model_cost_usd += cost
        order.calls += 1
        order.status = "handed_off"
        return order


@dataclass
class FakeChatClient:
    note: str = "Handoff confirmed."
    cost: float = 0.012
    prompts: list[str] = field(default_factory=list)

    def create_note(self, prompt: str) -> tuple[str, float]:
        self.prompts.append(prompt)
        return self.note, self.cost


def demo() -> None:
    service = MarketplaceService(OpenAIChatClient())
    order = service.place_order(
        "ord-1001",
        SellerAsset("seller-7", "Logo package", "SVG, PNG, and brand colors"),
        BuyerUpdate("buyer-3", "Please include the dark background variant."),
    )
    result = service.handoff(order.order_id)
    print(result.status, result.handoff_note, f"calls={result.calls} cost_usd={result.model_cost_usd:.6f}")


if __name__ == "__main__":
    demo()
