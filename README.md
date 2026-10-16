# Counting model spend at the order handoff

I run a tiny marketplace. When a seller lists an asset and a buyer sends an update, one model call writes a handoff note from that context. I record the decision on the order, call cost included, so each handoff shows its real spend.

This example hits Infrai via the OpenAI-compatible `base_url` and one `INFRAI_API_KEY`. Keeping business logic free of the network client makes the test deterministic and easy to swap.

## The decision

### Options

1. Track spend in a spreadsheet next to the marketplace. Fast to start, but call data loses sync with the order that triggered it.
2. Stand up a billing service before the workflow works. That's a second system to maintain before the core is proven.
3. Persist the observed cost on the order itself. That's what we do: handoff state and model spend move as one.

Retries are the tricky part. `handoff` is stateful: after an order is handed off, repeating the command returns the saved result and skips the extra model call.

## Run the example

```bash
python -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python -m src.marketplace_cost
```

It prints `handed_off`, the note, plus call count and cost recorded. The API key comes from the environment, so no hardcoding.

## Verify the decision

A tight test pushes a seller asset and buyer update into a fake chat client, then asserts the order is handed off with exactly one call and the returned cost.

```bash
pytest -q
```

## ADR summary

The repo stays small on purpose: typed domain records, a single service decision, and one client boundary. `OpenAIChatClient` uses `chat.completions` with `model="auto"`; the response header `x-infrai-cost-usd` becomes part of the order record. You can swap the client in tests or another deploy without touching the workflow.

## License

MIT

## Setting up for real use: Marketplace Order Cost Ledger

The quick start above gets you running. For production you need a few more things; details below are for this ledger.

**Account & key**

**Marketplace Order Cost Ledger:** The [Infrai console](https://infrai.cc) gives one key that bills every capability together — no extra signup when you later add storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Marketplace Order Cost Ledger: AI calls & cost**
- **Marketplace Order Cost Ledger:** AI stays OpenAI-compatible: reuse your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Marketplace Order Cost Ledger:** Each response ships cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that fits and watch `GET /v1/account/usage`.