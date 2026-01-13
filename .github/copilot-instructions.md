# StockAgent: AI Coding Instructions

## Project Overview
**StockAgent** is a multi-agent LLM-based stock trading simulator that models realistic trading behaviors in response to market factors (macroeconomics, policy changes, financial reports, random events). It implements a 4-phase workflow: **Initial Phase** → **Trading Phase** → **Post-Trading Phase** → **Special Events Phase**.

## Architecture: Key Components & Data Flow

### Core Agents: Multi-Round LLM Interactions
- **`agent.py` - Agent Class**: Each agent is an LLM-based trader with mutable state (portfolio, loans, chat history)
  - **Key Methods**: `run_api()` → dispatcher to `run_api_gpt()`, `run_api_gemini()`, `run_api_mock()`
  - **State**: `stock_a_amount`, `stock_b_amount`, `cash`, `loans[]`, `action_history[TOTAL_DATE]`, `chat_history[]`
  - **Initialization**: Random portfolio generation via `random_init()` ensures each agent has 50k-5M property
  - **LLM Pattern**: Agents maintain `chat_history` for multi-turn context; prompts use `format_prompt()` with templated blocks

### Market Infrastructure
- **`stock.py` - Stock Class**: Two tradeable assets (A, B) with session-based price tracking
  - **Price Update Pattern**: Prices update daily via matching engine (`stock.update_price(date)` reads last matched price from session)
  - **History Tracking**: `history{date: session_deals}` stores all daily transactions; cleared after daily close

- **`secretary.py` - Secretary Class**: Central LLM coordinator (budget checks, loan validation, forum generation)
  - **Loan Validation**: `check_loan()` parses JSON responses, validates against max borrowable amount
  - **API Abstraction**: Single `run_api(model, prompt, temperature)` used by secretary; agents call their own methods

### Simulation Engine: `main.py`
- **`handle_action()`**: Order matching engine—buy/sell orders match by price; transfers executed if prices align
  - Matching Logic: Iterates seller queue; closes at min(buyer_amount, seller_amount); removes fulfilled orders
  - Trades recorded immediately via `create_trade_record(date, session, stock, buyer, seller, amount, price)`
- **4-Phase Workflow Loop**:
  1. **Initial**: All agents receive initialization prompt with financial reports
  2. **Trading**: 3 sessions/day; LLM generates actions → executed → prices updated
  3. **Post-Trading**: Daily events (financial reports, loan repayments), quarterly events
  4. **Special Events**: Random disruptions (rate changes) at preset days

## Developer Workflows

### Adding a New Feature
1. **New Agent Method**: Add to `Agent` class; follow chat_history + `run_api()` pattern for LLM calls
2. **New Event Type**: Add event data to `util.py` (EVENT_X_DAY, EVENT_X_MESSAGE, EVENT_X_LOAN_RATE)
3. **Prompt Modification**: Edit templated blocks in `prompt/agent_prompt.py` (uses `procoder.prompt.NamedBlock/NamedVariable`)

### Debugging LLM Responses
- **Mock Mode**: Pass `model='mock'` to skip API calls; `Agent.run_api_mock()` returns deterministic responses
- **Response Parsing**: Use secretary's `check_loan()` pattern: extract JSON between `{}`, validate fields
- **Chat History**: Access `agent.chat_history` to inspect multi-turn context (aids debugging prompt coherence)

### Running Simulations
```bash
# Set API keys first
export OPENAI_API_KEY=your_key
export GOOGLE_API_KEY=your_key

# Run with GPT-4
python main.py --model gpt-4

# Run with Gemini
python main.py --model gemini-pro

# Run mock (no API cost)
python main.py --model mock
```

## Critical Patterns & Conventions

### Prompt Engineering
- **Template System**: `procoder.prompt.NamedBlock(name, content)` + `NamedVariable(refname, content)` for reusable blocks
  - Example: `{loan_type_prompt}` placeholder in action prompt auto-filled by procoder
  - Always use `format_prompt(template, merged_dict)` to resolve nested templates
- **Context Injection**: Prompts include agent's character (`Conservative|Aggressive|Balanced|Growth-Oriented`), portfolio state, market data, forum posts
- **Output Format**: Agent responses must be strict JSON (checked by secretary); structure: `{"action_type": "buy"|"sell", "stock": "A"|"B", "amount": int, "price": float}`

### State Management
- **Portfolio Invariants**: `total_property = stock_a*price_a + stock_b*price_b + cash - debt_amount`
  - Bankruptcy triggered when net worth < 0 (agents quit if `is_bankrupt=True`)
- **Loans Structure**: `loans = [{"loan": "yes|no", "amount": x, "loan_type": 0-2, "repayment_date": day}]`
  - Interest rates indexed by loan_type; rates change on EVENT days via `EVENT_X_LOAN_RATE`
- **Action Recording**: Every action stored in `agent.action_history[date]` for audit trail

### Financial Data
- **Quarterly Reports**: Pre-computed in `util.FINANCIAL_REPORT_A/B` (4 reports for ~264-day simulation)
  - Pulled via `Stock.gen_financial_report(index)` at report days (see `SEASON_REPORT_DAYS`)
- **Loan Terms**: 1/2/3-month terms with base rates; reset on rate change events
- **Session Mechanics**: 3 trading sessions per day; prices persist across sessions until daily close

## Key Files & Their Responsibilities
| File | Purpose |
|------|---------|
| [main.py](main.py) | Simulation loop + order matching engine |
| [agent.py](agent.py) | LLM agent logic + multi-turn chat + portfolio management |
| [stock.py](stock.py) | Asset price & transaction history tracking |
| [secretary.py](secretary.py) | Centralized LLM calls + response validation |
| [prompt/agent_prompt.py](prompt/agent_prompt.py) | Templated trading prompts (procoder blocks) |
| [util.py](util.py) | Configuration: model params, prices, financial data, events |
| [record.py](record.py) | Trade/portfolio recording (output to logs) |
| [procoder/](procoder/) | External dependency: prompt templating + functional utilities |

## Common Pitfalls
1. **Forgetting `format_prompt()`**: Placeholders like `{loan_type_prompt}` won't resolve without it
2. **JSON Parsing**: Always extract JSON between `{}` before `json.loads()`; handle newlines/spaces
3. **Price Consistency**: Stock prices only update after matched trades; no unmatched orders affect price
4. **Agent Bankruptcy**: Check `agent.is_bankrupt` before using agent state; bankrupt agents shouldn't trade
5. **API Costs**: Use `model='mock'` for testing; actual GPT/Gemini calls incur charges per token

## Testing & Validation
- **Unit Testing**: Mock LLM responses in `Agent.run_api_mock()` for deterministic behavior
- **Integration Testing**: Run full simulation with `--model mock`; validate output logs in `log/` directory
- **Prompt Validation**: Use procoder's validation before deployment (ensures all templates resolve)
