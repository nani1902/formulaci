# formulaci as an MCP server

`formulaci-mcp` exposes the formulaci checker to any MCP client (Claude Desktop, Claude Code,
other agents). A model can check an identity, series, integral or closed form before it shows it
to a user. The checker reads the LaTeX into SymPy, infers variable domains from the surrounding
text, and then checks the identity symbolically and numerically under the precision-first
FAIL policy in [SPEC.md](../SPEC.md).

The server uses the stdio transport. stdout carries the protocol, and logs go to stderr.

## Install

```bash
uv sync --extra mcp
```

The `mcp` extra pulls in the MCP Python SDK (`mcp>=1.2`). The server works with both SDK lines:
1.x (`FastMCP`) and 2.x (`MCPServer`). Install `gmpy2` (already a dependency) for speed. Without it,
integrals and series hit the time budget much more often.

To run the server by hand (it waits for a client on stdin):

```bash
uv run --directory /path/to/formulaci formulaci-mcp
```

Set `FORMULACI_MCP_LOG=INFO` or `DEBUG` for more logging on stderr. The default is `WARNING`.

## What it exposes

| Name | Kind | Use |
|---|---|---|
| `verify_formula(latex, context="", timeout=20)` | tool | Check one identity. Returns a compact JSON object with `verdict`, `reason` and `advice`. |
| `verify_text(text, max_formulas=50, timeout=20)` | tool | Extract every formula from a draft (`$...$`, `$$...$$`, `\(...\)`, `\[...\]`, `<math>`, `equation`/`align` blocks), check each in parallel, and return per-formula results, a summary and the list of formulas to fix. |
| `explain_verdict(latex, context="", timeout=20)` | tool | The same check, returned as readable text: how the LaTeX was read, domains, regimes and the counterexample. |
| `formulaci://policy` | resource | Short text on what the verdicts mean, the FAIL policy and the limits. |

The tool descriptions tell the model when to call them: before presenting any non-trivial
identity, series, integral or closed form. The server's `instructions` say the same.

Fields returned by `verify_formula` (each item in `verify_text.results` has the same shape):

- `verdict`: `PASS`, `FAIL`, `INCONCLUSIVE` or `SKIP`.
- `reason`: one sentence from the checker.
- `advice`: one sentence addressed to the calling model.
  - FAIL: "Do not present this formula; the identity fails at …"
  - PASS: "Verified numerically and symbolically …"
  - INCONCLUSIVE or SKIP: "Could not verify; say so or rephrase as a checkable identity."
- `counterexample` (FAIL only): `assignments`, `lhs`, `rhs`, `abs_diff`, `rel_diff`, at 40 significant digits.
- `translation`: how each piece was read. Fields: `lhs`, `relation`, `rhs` and `status`, plus `unsupported` or `error` when present.
- `assumptions`: inferred `domains`, `constants`, `constraints` and the rules that produced them.
- `symbolic`: `equal` or `not_equal`, when SymPy decided.
- `skip_reason`: when the formula was skipped.
- `elapsed_s`: time taken for the check.

Errors never reach the client as exceptions. An exception or a timeout becomes
`{"verdict": "INCONCLUSIVE", "reason": "<error>", "advice": "Could not verify; ..."}`.
For `explain_verdict` it becomes the text `INCONCLUSIVE: <error>`.

## Configure a client

### Claude Desktop

Add the server to `claude_desktop_config.json`:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Restart Claude Desktop after editing.

```json
{
  "mcpServers": {
    "formulaci": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/formulaci", "--extra", "mcp", "formulaci-mcp"]
    }
  }
}
```

If Claude Desktop cannot find `uv`, use its absolute path (`which uv`), for example `/Users/you/.local/bin/uv`.

### Claude Code

```bash
claude mcp add formulaci -- uv run --directory /path/to/formulaci --extra mcp formulaci-mcp
```

Everything after `--` is the server command. Add `--scope user` to make the server available in
every project, or `--scope project` to write it to a shared `.mcp.json`. Check it with
`claude mcp list`. (This syntax follows the Claude Code docs. It was not re-checked against
`claude mcp add --help` here because no Claude Code CLI was installed on the machine that wrote this page.)

### Any stdio client

Launch the command `uv run --directory /path/to/formulaci --extra mcp formulaci-mcp` and speak
MCP over its stdin and stdout. Here is an example with the Python SDK (2.x):

```python
import anyio
from mcp import Client, StdioServerParameters

async def main():
    server = StdioServerParameters(
        command="uv",
        args=["run", "--directory", "/path/to/formulaci", "--extra", "mcp", "formulaci-mcp"],
    )
    async with Client(server) as client:
        result = await client.call_tool("verify_formula", {"latex": r"\sin^2 x + \cos^2 x = 2"})
        print(result.content[0].text)

anyio.run(main)
```

With SDK 1.x, use `mcp.client.stdio.stdio_client(server)` and `ClientSession` instead of `Client`.
The calls are the same.

## Example

A model drafts "the sum of the first n squares is n(n+1)(2n+1)/3". Before answering, it calls:

```json
{
  "name": "verify_formula",
  "arguments": {
    "latex": "\\sum_{k=1}^{n} k^2 = \\frac{n(n+1)(2n+1)}{3}",
    "context": "for every positive integer n"
  }
}
```

and gets back (real output):

```json
{
  "latex": "\\sum_{k=1}^{n} k^2 = \\frac{n(n+1)(2n+1)}{3}",
  "verdict": "FAIL",
  "reason": "The identity fails at 46 of 46 evaluable points, a clear majority in every regime (small_positive, integers_small, mixed_sign, large) (e.g. at n=1: lhs=1.000000000000, rhs=2.000000000000).",
  "advice": "Do not present this formula; the identity fails at n = 1, where the left side is 1.0 and the right side is 2.0.",
  "counterexample": {
    "assignments": {"n": "1"},
    "lhs": "1.000000000000000000000000000000000000000",
    "rhs": "2.000000000000000000000000000000000000000",
    "abs_diff": "1.000000000000000000000000000000000000000",
    "rel_diff": "0.5000000000000000000000000000000000000000"
  },
  "translation": [
    {"lhs": "Sum(k**2, (k, 1, n))", "relation": "=", "rhs": "n*(n + 1)*(2*n + 1)/3", "status": "ok"}
  ],
  "assumptions": {
    "domains": {"n": "positive_integer"},
    "constants": {},
    "constraints": [],
    "assumptions_source": ["D.letter_integer:n", "P.type_phrase:n"]
  },
  "elapsed_s": 1.81
}
```

The model then corrects the denominator to 6, checks again and gets `PASS`.

For a whole draft, `verify_text` returns
`{"summary": {"total": 2, "PASS": 1, "FAIL": 1, "INCONCLUSIVE": 0, "SKIP": 0}, "results": [...], "advice": "Fix 1 formula before presenting the text: #2 ... "}`.

## Limits

- **Identities only.** The checker tests relations that should hold for every admissible value.
  These come back `SKIP` or `INCONCLUSIVE` and are not checked:
  - equations to solve (`x^2 - 2 = 0`);
  - physical laws between measured quantities (`F = ma`);
  - definitions;
  - approximations (`\approx`).
- **Precision-first FAIL.** A FAIL needs a stable mismatch at 50 and 65+ digits in at least two
  sampling regimes, and no symbolic proof of equality. Anything less is `INCONCLUSIVE`, so
  INCONCLUSIVE is not evidence either way.
- **The verdict is about the LaTeX as read.** Always look at `translation` and `assumptions`.
  Common misreadings: `e` or `i` read as a variable, a superscript that is a label, or `\log` with
  another base. On real Wikipedia pages, roughly one in ten raw FAIL flags was a true error before
  human review. Most of the rest were statements or notation that is not an identity. Formulas a
  model writes deliberately as identities fail far more often for real, but read the counterexample.
- **Time.** Each formula has a budget of `timeout` seconds (default 20, capped at 60). Hard
  integrals and slowly converging series can time out and come back INCONCLUSIVE.
  - `verify_text` checks at most `max_formulas` formulas (capped at 200) and reports `truncated` when it drops some.
  - The server stops waiting after the budget plus a 15 s grace period. A check still running in a
    worker thread at that point is abandoned.
- **Context matters.** Domains such as "n a positive integer" or "|x| < 1" come from `context`.
  Without it, letters default to their usual roles (`n`, `k` integers; `x`, `y` real).
