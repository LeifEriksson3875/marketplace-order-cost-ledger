from src.marketplace_cost import BuyerUpdate, FakeChatClient, MarketplaceService, SellerAsset


def test_handoff_records_one_model_call_and_cost() -> None:
    chat = FakeChatClient(note="Send the dark variant.", cost=0.025)
    service = MarketplaceService(chat)
    order = service.place_order(
        "ord-1",
        SellerAsset("seller-1", "Landing page", "HTML and CSS"),
        BuyerUpdate("buyer-1", "Use the dark palette."),
    )

    handed_off = service.handoff("ord-1")

    assert handed_off.status == "handed_off"
    assert handed_off.handoff_note == "Send the dark variant."
    assert handed_off.calls == 1
    assert handed_off.model_cost_usd == 0.025
    assert len(chat.prompts) == 1

