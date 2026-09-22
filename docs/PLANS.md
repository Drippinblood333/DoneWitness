# Plans and assertions

`donewitness validate --plan PATH` reports the schema, criteria count, and canonical
SHA-256 digest without starting an app or importing Playwright. Exit 0 means
**format valid**, not application PASS. Invalid files exit 2. Plan v1 is
criteria-only; execution requires v2 or v3.

Plan v3 retains v2's explicit procedures and adds four assertions:

| Step | Required fields besides `type` | Meaning |
| --- | --- | --- |
| `navigate` | `path` | Navigate within the supplied origin |
| `fill` | `selector`, `value` | Fill an input |
| `click` | `selector` | Click the matching element |
| `assert_visible` | `selector` | Element is visible |
| `assert_text` | `selector`, `text` | Full text matches, normalizing whitespace |
| `assert_value` | `selector`, `value` | Exact input value matches |
| `assert_count` | `selector`, `count` | Exact number of matches, including zero |
| `assert_hidden` | `selector` | Element is hidden **or absent** |

Text, value, and selector fields are strings, with nonblank selectors. Count is a
nonnegative integer; booleans, numeric strings, and fractions are rejected. Text/value
may be empty. Text compares `textContent`, including descendants, normalizing
whitespace; it does not imply visibility. Add `assert_visible` when visibility
matters. Hidden/absent does not prove backend authorization.

```json
{
  "schema_version": 3,
  "task": "Show the correct total",
  "criteria": [{
    "id": "AC-TOTAL",
    "description": "The total is 20.00",
    "procedure": {
      "type": "browser",
      "timeout_ms": 2000,
      "steps": [
        {"type": "navigate", "path": "/"},
        {"type": "assert_text", "selector": "#total", "text": "20.00"}
      ]
    }
  }]
}
```

Each procedure must start with navigation and contain an assertion. `timeout_ms`
retains v2's **per-step** 100–30,000 ms bound (default 5,000), not a whole-plan
deadline. Assertions auto-retry. Contradictions are FAIL; selector/execution errors
are UNKNOWN. Unsupported syntax is rejected before application startup.

On a failed v3 assertion, the executor checks locator usability through public
Playwright APIs: invalid selectors, ambiguous single-element matches, and value
checks on non-input elements are UNKNOWN. A value diagnostic can use one additional
operation bounded by the same timeout; the setting is not a wall-clock step budget.
Successful assertions incur no extra diagnostic reads. Legacy v2 behavior is retained.

Each criterion gets a fresh browser context. Persistence checks must remain within
one criterion. See the [expense plan](../examples/expenses.plan.json).

Default failure diagnostics include type, step position, and selector, not actual
page contents, expected text/value, or raw Playwright exceptions. Do not put secrets
in selectors, task titles, or criterion descriptions: those are review metadata.
Plans themselves may contain supplied inputs and must be handled accordingly.

## Compatibility

Plan v1/v2 formats, digests, and validation remain unchanged. New assertions require
`schema_version: 3`; adding them to v2 is invalid. Version 0.1 clients reject v3.
Receipts remain v4, manifests v1, and machine summaries v1. Old receipts remain
inspectable. Plan v3 does not add a cryptographic attestation or a coverage guarantee.

Semantics follow the [Playwright Python assertion API](https://playwright.dev/python/docs/api/class-locatorassertions).
