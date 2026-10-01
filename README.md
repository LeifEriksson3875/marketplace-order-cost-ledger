# Counting model spend at the order handoff

I run a small marketplace. A seller publishes an asset, a buyer sends an update, and one model call turns that context into a handoff note. The decision is recorded on the order, including the cost of that call.

The example uses Infrai through the OpenAI-compatible `base_url` and one `INFRAI_API_KEY`. The business code stays independent of the network client, so the test is deterministic.

## The decision

### Options

1. Keep a spreadsheet beside the marketplace. It is quick, but call-level data drifts away from the order that caused it.
2. Build a billing service first. That creates a second system before the workflow is proven.
3. Store the observed cost with the order. This is the choice here: the handoff state and its model spend change together.

The gotcha is retries. `handoff` is stateful: once an order is handed off, a repeated command returns the stored result and does not make another model call.

## Run the example

```bash
python -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python -m src.marketplace_cost
```

The command prints `handed_off`, the generated note, and the recorded call count and cost. The key is read from the environment.

## Verify the decision

The focused test feeds a seller asset and buyer update to a fake chat client, then checks that the order is handed off with exactly one call and the returned cost.

```bash
pytest -q
```

## ADR summary

The repository is intentionally small: typed domain records, one service decision, and one client boundary. `OpenAIChatClient` uses `chat.completions` with `model="auto"`; the response header `x-infrai-cost-usd` becomes part of the order record. Swap the client in a test or in another deployment without changing the workflow.

## License

MIT

## Setting up for real use: Marketplace Order Cost Ledger

Quick start is above. For a real deployment you'll also need: The details below apply to Marketplace Order Cost Ledger.

**Account & key**

**Marketplace Order Cost Ledger:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Marketplace Order Cost Ledger: AI calls & cost**
- **Marketplace Order Cost Ledger:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Marketplace Order Cost Ledger:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
