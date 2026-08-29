# HW 0 — Taco Bot 3000

## EE 599: Designing and Building Autonomous AI Agents

### University of Southern California — Instructor: Arash Saifhashemi

**A warm-up, not a graded assignment. One hour, in class. No prior experience
with Pydantic is assumed.**

---

## The situation

Last Tuesday, Taco Bot 3000 spent **\$124,489.00** on burritos in a single lunch
rush.

Taco Bot is an AI model connected to the campus taqueria's ordering system. A
customer types a request in plain English, the model turns it into JSON, and a
program reads that JSON and places the order.

Nothing was hacked. The model was not jailbroken. It produced text that looked
exactly like the text it produces on a good day, and the program on the other
end believed all of it.

You are going to fix that twice. Once by hand, the way people wrote this kind of
code before validation libraries existed, and once with Pydantic, in about a
quarter of the lines. Then you will build the thing every tool call in this
course sits behind, and watch a real AI model try to get through it.

---

## Why this assignment exists

Assignments 1 through 4 all have the same shape: an AI model proposes an action,
and your code decides whether to run it. Pydantic is how that decision gets
written, in this course and in the OpenAI Agents SDK, LangGraph, and MCP. This
warm-up gets the library out of the way now, so that the graded assignments can
be about agents instead of about syntax.

By the end you will be able to:

- write a Pydantic model as a **contract**, using `Literal`, `Field`
  constraints, `extra="forbid"`, and strict mode — and say which of those four
  catches which kind of problem
- explain the difference between `model_validate` and `model_validate_json`, and
  why confusing them is the most common Pydantic bug in this course
- use `@field_validator` and `@model_validator` for rules a type cannot express
- turn a `ValidationError` into a short, safe, structured failure that is
  suitable to send back to an AI model
- use one Pydantic model for two jobs at once: the JSON Schema you hand to a
  model, and the runtime check on what it sends back
- state precisely what validation does **not** tell you

---

## Setup (5 minutes)

Python 3.11 or newer. Everything runs offline except the Part 5 bonus.

```bash
cd files
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
```

You should see about **31 failures**. That is correct. The failing tests are the
assignment, and they turn green one TODO at a time.

## What is in `files/`

You do all your work in `files/`. There are ten numbered TODOs across five
Python files.

| file | TODOs | what it is |
|---|---|---|
| `taqueria.py` | — | The menu, the cash register, and the model's replies. Read it first. Do not edit it. |
| `part1_before.py` | 1–2 | Checking data by hand |
| `part2_after.py` | 3–4 | The same job with Pydantic |
| `part3_errors.py` | 5–7 | Rules types cannot express, and failure as data |
| `part4_tool_boundary.py` | 8–9 | The gate |
| `part5_codex.py` | 10 | A real AI model on the other end (bonus) |
| `test_hw0.py` | — | The specification, as tests. Read it. Do not edit it. |
| `ANSWERS.md` | — | Six short questions |

`grep -n TODO *.py` lists every one of them.

Each spot where you write code is marked with either `raise NotImplementedError`
or `...`. Every TODO comment tells you exactly what to write, including which
Pydantic feature to use.

**Do the parts in order.** Each one imports the one before it, on purpose: you
are refining a single contract across five files rather than doing five
unrelated exercises. If Part 3 fails with a confusing error, the usual cause is
that Part 2 is not finished.

---

## The parts

### Part 1 — Checking data by hand (10 min, TODO 1–2)

```bash
python part1_before.py
```

**Run it before you write anything**, and read the output. Some replies are
marked `ESCAPED`: those are bad orders that got through, were cooked, and were
charged to a card. Look at the total at the bottom.

Then read `validate_order_by_hand`. It is not bad code. It is what a careful
programmer writes with only the standard library: about thirty lines of
`isinstance` checks, in which the business rules are hard to find among the
shape checks. And it still allowed a \$124,987 order.

Your job is to add the two missing rules by hand. Notice that the function gets
longer and the rules get *harder* to see, not easier.

Answer Q1 and Q2 in `ANSWERS.md` while this part is still fresh. Q1 asks about a
reply that was accepted, is wrong, and that nothing flagged — find it before you
write TODO 2.

### Part 2 — The same job with Pydantic (15 min, TODO 3–4)

```bash
python part2_after.py
```

Write the `BurritoOrder` model and the `parse_order` function. Same eight
replies, same rules. The reference solution is **9 lines against Part 1's 33**,
and it catches two problems Part 1 never noticed at all.

Three settings do three different jobs. Blurring them together is the
misconception this part exists to prevent:

| setting | the question it answers | what it rejects |
|---|---|---|
| `strict=True` | May this value be *converted* to the declared type? | `"3"` where an `int` was declared |
| `Field(ge=1, le=20)` | Is this value in the allowed *range*? | `0`, `9999` |
| `extra="forbid"` | Is this field name one we asked for *at all*? | `price_override` |

The last thing this part prints is `BurritoOrder.model_json_schema()`. Look at
it. You wrote your rules once, as a Python class, and got two things: code that
checks data at runtime, and a standard, machine-readable description you can
hand to another system. Part 5 hands that exact description to an AI model.

That combination is most of the reason agent frameworks are built on Pydantic.

### Part 3 — Rules types cannot express, and failure as data (15 min, TODO 5–7)

```bash
python part3_errors.py
```

`"Eve Hall"` and `"the Moon"` are both strings; only one is a place this
taqueria delivers to. No type annotation can tell them apart, so that rule goes
in a `@field_validator`. The rule "a delivery order needs an address" compares
two fields at once, so it goes in a `@model_validator(mode="after")`.

Then `to_tool_error`. In an ordinary program a rejection might raise an
exception and stop. In an agent that is usually wrong: the run has not failed,
the model simply made a bad suggestion, and the sensible next step is to tell it
what was wrong so it can try again.

That means **the failure gets sent back to the model**. So it needs a
predictable shape your code can branch on, and its text has to be safe to show —
no file paths, no stack traces, no library versions, and no unbounded growth.
The script ends by printing the safe version next to the unsafe one.

### Part 4 — The gate (15 min, TODO 8–9)

```bash
python part4_tool_boundary.py
```

This is the part everything else in the course is built on.

An AI model cannot run your code. It produces text saying which function it
would like called, with what arguments. The program that reads that text and
decides whether anything runs is called the **host**, and it is ordinary Python
that you control:

```
model produces text
        |
        v
+-----------------------------------------------------+
|  HOST (your code, the only part you control)         |
|    1. is this tool allowed?     -> no: stop here     |
|    2. are the arguments valid?  -> no: stop here     |
|    3. run the tool                                   |
|    4. shape the result                               |
+-----------------------------------------------------+
        |
        v
outcome is appended to the conversation and sent back to the model
```

Implement `handle_tool_call` so that it **returns a value on every path and
raises on none**. Four things can happen — the tool is not allowed, the
arguments are invalid, the tool itself fails, or everything works — and all four
have to come back as something the loop can append and carry on from. A loop
that crashes on turn three has lost the whole run.

One of the six turns is a **prompt injection**: text planted in a customer
review, written to look like an instruction, which the model read and is now
relaying. From the host's side it arrives as a polite request for a tool called
`refund_everything`, indistinguishable from any other tool call. Notice which
mechanism stops it, because it is not Pydantic.

The script then replays the same lunch rush with no gate at all. Those two
totals are the whole assignment in two numbers.

### Part 5 — A real AI model on the other end (bonus, 10 min, TODO 10)

```bash
python part5_codex.py           # offline canned replies: free, no network
python part5_codex.py --live    # real calls through the codex CLI
```

`codex exec` sends a prompt to a real model and prints the answer. Its
`--output-schema` option takes a JSON Schema file and constrains the model's
reply to that shape — and you already have a schema:
`BurritoOrder.model_json_schema()`.

Implement the ask-validate-repair loop: ask, validate, and on failure send your
`ToolError.message` back so the model can correct itself. **Once.** Do not loop
until it works. Every attempt costs money and time, and a model that is wrong
twice in the same way is usually not one attempt away from being right.

Run `--live` at least once and paste the output into `ANSWERS.md`. Watch for a
reply that is **valid but wrong**. The schema constrains shape; it says nothing
about truth. Pydantic answers exactly one question — *does this data fit the
shape I described?* — and knowing where that answer stops is most of what
separates an agent that works from one that merely runs.

---

## Submitting

```bash
pytest -q          # 34 passed
```

Push your `files/` folder: the five Python files you edited and your completed
`ANSWERS.md`. Do not edit `test_hw0.py` or `taqueria.py`.

This assignment is not graded. It is checked for completion, and Assignment 1
assumes you have done it.

## Where this goes next

| what you build here | where it comes back |
|---|---|
| `BurritoOrder` | typed tool arguments; `output_type` in the Agents SDK (Week 2) |
| `handle_tool_call` | your first agent loop (Week 1), then MCP servers (Week 3) |
| `ToolError` | recovery and retry policy (Weeks 6 and 11) |
| the allowlist | permissions and threat modelling (Weeks 6 and 14) |
| "valid but wrong" | evaluation and test tasks (Week 6) |

## Reference

You do not need to read these to finish the assignment; each TODO explains what
it needs. They are here for when you want more detail.

- [Pydantic — Models](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic — Fields and constraints](https://docs.pydantic.dev/latest/concepts/fields/)
- [Pydantic — Validators](https://docs.pydantic.dev/latest/concepts/validators/)
- [Pydantic — Strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/)
- [Pydantic — JSON Schema](https://docs.pydantic.dev/latest/concepts/json_schema/)
- [Pydantic — Validation errors](https://docs.pydantic.dev/latest/errors/validation_errors/)
