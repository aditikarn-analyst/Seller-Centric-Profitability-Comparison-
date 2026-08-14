# Profit Pulse

Build a web app called "Marketplace Profitability Analyzer" — a seller-side tool

for Indian e-commerce sellers to compare how much net profit a product leaves them

on different marketplaces (Amazon, Flipkart) after all fees, taxes, and returns.

DESIGN DIRECTION

You choose the visual theme, color palette, typography, and overall styling — pick a

clean, modern, professional look appropriate for a financial/analytics SaaS product.

Make it fully responsive (mobile + desktop) and support light/dark if convenient.

Do not ask me for theme preferences; decide and apply a cohesive design system yourself.

TECH

React (single-page app) with client-side routing. Use a charting library that

supports a WATERFALL chart (e.g. Plotly, or build an equivalent). Talk to an existing

REST backend — do NOT create your own backend or database. Put the API base URL in one

config constant defaulting to "/api/v1" (assume a dev proxy forwards /api to the server).

IMPORTANT DATA RULE

All monetary values arrive from the API as STRINGS (e.g. "264.59"), never numbers, to

preserve exact decimal precision. Display them as-is with a ₹ prefix; only parse to a

number when a chart needs it. Never round or reformat money yourself.

AUTH

JWT bearer auth. Store the token in localStorage and attach it as

"Authorization: Bearer <token>" on every request via a single axios interceptor.

Global auth state via React Context (the only global state).

- POST /auth/register  body {email, password, name} -> 201 {user_id, email, name, created_at}

- POST /auth/login     body {email, password} -> {access_token, token_type}

- GET  /auth/me        (bearer) -> {user_id, email, name, created_at}

PAGES / ROUTES

1. "/" Compare (main page) — works for both logged-in and anonymous users.

2. "/login" and "/register" — auth forms; on success redirect to "/".

3. "/history" — logged-in only; shows saved comparisons. If not logged in, prompt to log in.

Navbar: app name, links to Compare and (if logged in) History, plus Login/Register or the

user's email + Logout.

COMPARE PAGE

A product form with fields:

- name (text, optional)

- category (dropdown; options: "Home & Kitchen", "Electronics Accessories", "Books",

  "Clothing", "Beauty & Personal Care", "Toys", "Sports & Fitness",

  "Automotive Accessories", "Grocery")

- cost_price (decimal, send as string)

- selling_price (decimal, send as string)

- weight_g (integer grams)

Pre-fill sensible defaults (e.g. Home & Kitchen, cost 450.00, selling 999.00, weight 400).

On submit, POST /compare with the form body. Send with the auth header if logged in

(the server then saves it to history), or without if anonymous.

POST /compare response shape:

{

  "product": { "name", "category", "cost_price", "selling_price", "weight_g" },

  "results": [

    {

      "platform": "Flipkart",

      "rank": 1,

      "rule_id": 88,

      "breakdown": {

        "gross_revenue":"999.00","commission":"89.91","fixed_fee":"35.00",

        "shipping":"58.00","gateway":"19.98","fee_base":"202.89",

        "gst_on_fees":"36.52","rto_adjusted_cost":"45.00",

        "net_settlement":"714.59","tcs_withheld":"5.00",

        "cash_at_settlement":"709.59","effective_profit":"264.59",

        "margin_pct":"26.49","breakeven_price":"723.41"

      }

    }

    // ...one entry per platform, sorted by rank (1 = best)

  ],

  "recommendation": {

    "winner":"Flipkart",

    "margin_over_next":"34.52",

    "deciding_factor":"commission",

    "explanation":[

      {"factor":"commission","delta":"29.97"},

      {"factor":"shipping","delta":"7.00"},

      {"factor":"gst","delta":"7.55"},

      {"factor":"fixed_fee","delta":"5.00"},

      {"factor":"rto","delta":"-15.00"}

    ]

  }

}

RENDER, after a successful compare:

1) A recommendation banner: "Recommended: {winner}", "better by ₹{margin_over_next} per unit

   than the next platform", and "deciding factor: {deciding_factor}". Below it, list the

   explanation items — each factor name and its signed ₹delta. Positive deltas mean the

   winner pays less on that line (an advantage); negative deltas are offsets. Style

   positive vs negative differently (e.g. up/down or +/− with distinct emphasis). These

   deltas sum exactly to margin_over_next.

2) A WATERFALL chart for the winning platform showing how gross revenue becomes net

   settlement, one downward step per deduction:

   start at gross_revenue (absolute), then subtract commission, fixed_fee, shipping,

   gateway, gst_on_fees, rto_adjusted_cost, ending at net_settlement (total).

3) One result card per platform (sorted by rank), highlighting the rank-1 winner. Each

   card shows platform name, rank, big "₹{effective_profit}" and "{margin_pct}% margin",

   and an expandable itemised fee breakdown table listing every line in `breakdown`

   (deductions shown as subtractions; margin as a percentage; break-even price).

Show a clear message if the API returns an error (e.g. 422 "no platform can price this

product") and a loading state while comparing.

HISTORY PAGE (logged-in)

GET /comparisons (bearer) -> array of:

{ "comparison_id","product_id","platform_id","rule_id","gross_revenue",

  "effective_profit","margin_pct","breakeven_price","explanation","computed_at" }

Render as a table (newest first): computed_at, platform_id, gross_revenue, effective_profit,

margin_pct. Empty state if none.

Keep the UI simple, information-dense where it helps a seller decide, and make the

recommendation + waterfall the visual centerpiece.

This project was built with [Lovable](https://lovable.dev).

**Live app**: https://marketplace-edge.lovable.app

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/f4f86a6e-1e74-4578-a1e9-eb091b081421).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
