# HW 0 — Answers

Name: Zhenglong Liu
USC email: zhenglon@usc.edu

Six short questions. One or two sentences each is enough; nobody is looking for
an essay. These matter more than they look: the code shows you can use Pydantic,
and this file shows you know why you used it.

---

### Q1 (Part 1)

Run `part1_before.py` **before** you write TODO 1 and TODO 2.

Two replies are marked `ESCAPED`. A third reply is marked `ACCEPTED` even though
it should not have been. Which one is it, and why did the `ESCAPED` counter not
notice it?

> *The 7th reply should not be accepted. The esacaped counter only counts replies whose quantity is out of the range from 0~20. But the problem is that it has an extra parameter.*

---

### Q2 (Parts 1 and 2)

Part 1 accepted `{"quantity": "3"}` and quietly ordered 3 tacos, because
`int("3")` succeeds. Part 2 rejected the same reply, because of `strict=True`.

Which behaviour do you want in an agent, and why? Either answer is acceptable if
you defend it.

> *Part 2 is better. Because this is a problem that agent should fix. We need to make it observed instead of fixing it for agent. Otherwise, we may never know this problem since it was silently solved by our code.*

---

### Q3 (Part 2)

Three settings do three different jobs: `strict=True`, `Field(ge=..., le=...)`,
and `extra="forbid"`.

For each reply below, say which one rejects it, and whether either of the other
two would also have caught it.

| reply | rejected by | would the others catch it? |
|---|---|---|
| `{"item":"taco","quantity":"3","spice":"hot"}` | | |
| `{"item":"taco","quantity":0,"spice":"hot"}` | | |
| `{"item":"taco","quantity":1,"spice":"hot","price_override":0}` | | |

---

### Q4 (Part 3)

`to_tool_error` builds its message out of the `loc` and `msg` values from
`exc.errors()`, rather than just using `str(exc)`.

Name one concrete thing that could go wrong in a real system if you sent
`str(exc)` back to an AI model instead. Run `part3_errors.py` and compare the
two printed versions if you need a reminder.

> *In a real system, str(exc) may contain users' input, program's path, or the name of a class. Things which are not necessary will waste tokens. If user's input is bad. It will go into the context and make trouble.*

---

### Q5 (Part 4)

The injected `refund_everything` call was stopped by the allowlist, not by
Pydantic. No schema was involved in that decision.

State the general rule this illustrates: what does validation decide, and what
does it not decide?

> *Validation decides whether the arguments have the expected fields, types, and values. It does not decide whether the requested tool is authorized; that requires a separate allowlist or permission check.*

---

### Q6 (Part 5, bonus)

Run `python part5_codex.py --live` once and paste the output below.

Your schema says `quantity` may not exceed 20. Look at what the model did with
the request for a hundred burritos. Did it come back with something that was
**valid but wrong** — that is, something that passed every check you wrote and
was still not what the customer asked for?

What check, outside Pydantic, would catch that?

```
==============================================================================
PART 5 -- live codex exec
==============================================================================
  customer: "3 hot tacos please"
  ACCEPTED  validated after 1 attempt(s)       {"item":"taco","spice":"hot","quantity":3,"notes":""}

  customer: "gimme like a hundred burritos for the club, mild"
  ACCEPTED  validated after 1 attempt(s)       {"item":"burrito","spice":"mild","quantity":1,"notes":"Customer requested approximately 100 burritos; quantity reduced to 1 because orders are limited to 1–10 items."}

  customer: "two medium bowls, no beans"
  ACCEPTED  validated after 1 attempt(s)       {"item":"bowl","spice":"medium","quantity":2,"notes":"no beans"}

  The schema shaped the reply. Validation decided whether to trust it.

  Now notice what neither of them did: check whether the order is what
  the customer actually wanted. When you run --live, look closely at
  the hundred-burrito request. A reply can satisfy every rule you
  wrote and still be the wrong order.

  Pydantic answers exactly one question: does this data fit the shape
  I described? It has nothing to say about whether the data is true or
  useful. Knowing that boundary is most of what separates an agent
  that works from one that merely runs.
```

> *Yes. The model changed the requested quantity from about 100 to 1, which passed every Pydantic check but did not preserve the customer's intent. A semantic check comparing the structured order with the original request, followed by explicit customer confirmation when a requested value must be changed, would catch this.*

---

### Verification and reproducibility note

Three bullets, as required by the course AI policy. You do not need to list
prompts or coding assistants.

1. Model(s) used by the submitted code:
2. How you tested this submission:
3. One known failure or limitation, or "none found":
