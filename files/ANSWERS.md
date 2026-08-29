# HW 0 — Answers

Name:
USC email:

Six short questions. One or two sentences each is enough; nobody is looking for
an essay. These matter more than they look: the code shows you can use Pydantic,
and this file shows you know why you used it.

---

### Q1 (Part 1)

Run `part1_before.py` **before** you write TODO 1 and TODO 2.

Two replies are marked `ESCAPED`. A third reply is marked `ACCEPTED` even though
it should not have been. Which one is it, and why did the `ESCAPED` counter not
notice it?

> *your answer here*

---

### Q2 (Parts 1 and 2)

Part 1 accepted `{"quantity": "3"}` and quietly ordered 3 tacos, because
`int("3")` succeeds. Part 2 rejected the same reply, because of `strict=True`.

Which behaviour do you want in an agent, and why? Either answer is acceptable if
you defend it.

> *your answer here*

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

> *your answer here*

---

### Q5 (Part 4)

The injected `refund_everything` call was stopped by the allowlist, not by
Pydantic. No schema was involved in that decision.

State the general rule this illustrates: what does validation decide, and what
does it not decide?

> *your answer here*

---

### Q6 (Part 5, bonus)

Run `python part5_codex.py --live` once and paste the output below.

Your schema says `quantity` may not exceed 20. Look at what the model did with
the request for a hundred burritos. Did it come back with something that was
**valid but wrong** — that is, something that passed every check you wrote and
was still not what the customer asked for?

What check, outside Pydantic, would catch that?

```
paste your --live output here
```

> *your answer here*

---

### Verification and reproducibility note

Three bullets, as required by the course AI policy. You do not need to list
prompts or coding assistants.

1. Model(s) used by the submitted code:
2. How you tested this submission:
3. One known failure or limitation, or "none found":
