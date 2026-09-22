"""Local expense demo with explicit faults for testing the same acceptance plan.

Browser localStorage is the demo's persistence boundary; this is not a backend
database or a production expense application.
"""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PAGE = """<!doctype html>
<html lang="en"><meta charset="utf-8"><title>Expense entry</title>
<body>
<h1>Expenses</h1>
<label>Description <input id="description"></label>
<label>Amount <input id="amount" type="number" min="0.01" step="0.01"></label>
<button id="save">Save</button>
<p id="error" role="alert" hidden>Description and positive amount required</p>
<p id="status" role="status"></p>
<ul id="expenses"></ul><p>Total: <span id="total">0.00</span></p>
<script>
const fault = "__FAULT__";
let expenses = JSON.parse(localStorage.getItem('expenses') || '[]');
function render() {
  const list = document.querySelector('#expenses');
  list.replaceChildren();
  for (const entry of expenses) {
    const row = document.createElement('li');
    row.textContent = `${entry.description}: ${(entry.cents / 100).toFixed(2)}`;
    list.append(row);
  }
  const cents = expenses.reduce((sum, entry) => sum + entry.cents, 0);
  document.querySelector('#total').textContent =
    ((cents + (fault === 'wrong-total' && expenses.length ? 100 : 0)) / 100).toFixed(2);
}
document.querySelector('#save').addEventListener('click', () => {
  const description = document.querySelector('#description');
  const amount = document.querySelector('#amount');
  const cents = Math.round(Number(amount.value) * 100);
  const invalid = !description.value.trim() || !Number.isFinite(cents) || cents <= 0;
  document.querySelector('#error').hidden = !invalid;
  if (invalid) return;
  expenses.push({description: description.value.trim(), cents});
  if (fault !== 'fake-save') localStorage.setItem('expenses', JSON.stringify(expenses));
  description.value = '';
  amount.value = '';
  render();
  document.querySelector('#status').textContent = 'Saved';
});
render();
</script></body></html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--fault", choices=("none", "wrong-total", "fake-save"), default="none")
    args = parser.parse_args()
    page = PAGE.replace("__FAULT__", args.fault).encode("utf-8")

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)

        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Expense demo listening on {args.host}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
