"""
Shared setup for HW 0: the menu, the cash register, and the model's replies.

You do not write any code in this file. Read it once before you start, because
the rest of the assignment depends on two things in here.

First: `send_to_kitchen` is the "tool". In this course, a tool is an ordinary
Python function that an AI model can ask your program to run. Notice that
`send_to_kitchen` does not check its arguments at all. It multiplies a price by
a quantity and charges a credit card. That is normal. Most real functions trust
whoever calls them, because normally the caller is your own code.

Second: `RAW_MODEL_REPLIES` is a list of things an AI model actually sent back.
An AI model does not call your functions. It produces text. Something in your
program has to read that text and decide whether to call a function with it.
That decision is what this assignment is about.
"""

from __future__ import annotations

# --- The menu ---------------------------------------------------------------

# What the taqueria sells, and what each item costs in dollars.
MENU = {
    "burrito": 12.50,
    "taco": 4.25,
    "bowl": 13.75,
}

# The only three spice levels the kitchen knows how to make.
SPICE_LEVELS = ("mild", "medium", "hot")

# The only places the taqueria will deliver to. Stored in lowercase so that
# comparisons do not depend on how the customer capitalized the name.
DELIVERY_ZONE = (
    "eve hall",
    "salvatori",
    "leavey library",
    "the lawn",
    "olin hall",
)

# --- The cash register ------------------------------------------------------

# Every dollar amount charged so far, so the scripts can print a running total.
# Real money is not involved, but treat it as if it were: charging a card is an
# action you cannot undo by catching an exception afterward.
LEDGER: list[float] = []


def send_to_kitchen(item: str, quantity: int, spice: str, notes: str = "") -> str:
    """Cook the food and charge the customer's card.

    This function is deliberately not defensive. It does not check that `item`
    is on the menu, that `quantity` is a sensible number, or that `spice` is
    something the kitchen can make. It just multiplies and charges.

    Writing tools this way is normal and usually correct. The problem is not
    this function. The problem is what happens when the argument values were
    suggested by an AI model instead of written by a programmer. Some code
    between the model and this function has to be careful. Deciding where that
    code goes is the point of Part 4.
    """
    # If `item` is not a key in MENU, this line raises KeyError. The error
    # happens deep inside the tool, far from where the bad value came from.
    total = MENU[item] * quantity

    if "extra crispy" in notes.lower():
        # Tools also fail for reasons that have nothing to do with their
        # arguments: a machine is broken, a network call times out, a disk is
        # full. Pay attention to what this error message contains. In Part 4
        # you have to decide whether it is safe to show to an AI model.
        raise RuntimeError(
            "FRYER-503: fryer offline at /dev/fryer0; page ops@taqueria.internal"
        )

    LEDGER.append(total)
    note_text = f" ({notes})" if notes else ""
    return (
        f"KITCHEN: cooking {quantity} x {spice} {item}{note_text} "
        f"-- card charged ${total:,.2f}"
    )


def reset_ledger() -> None:
    """Forget every charge so far. The scripts call this before each demo."""
    LEDGER.clear()


def total_charged() -> float:
    """Add up every charge since the last reset."""
    return sum(LEDGER)


# --- What the AI model actually sent us --------------------------------------
#
# Eight replies collected from "Taco Bot 3000" during one lunch rush. Each entry
# is a (label, raw_text) pair. The label is only there to make the output
# readable; your code never gets to see it. The raw text is exactly what came
# back over the network: a string that is supposed to contain JSON.
#
# Exactly one of these eight is a correct, harmless order. The other seven are
# each wrong in a different way, and each one is a mistake that real models
# really make.

RAW_MODEL_REPLIES: list[tuple[str, str]] = [
    (
        "the one good order",
        '{"item": "burrito", "quantity": 2, "spice": "mild", "notes": "no onions"}',
    ),
    (
        # The number is written as text: "3" instead of 3. Whether this should
        # be accepted is a real decision, and Part 2 asks you to make it.
        "quantity as a string",
        '{"item": "taco", "quantity": "3", "spice": "hot", "notes": ""}',
    ),
    (
        # Correct JSON, correct types, correct field names. Only the value is
        # insane. No amount of type checking will catch this one.
        "the $124,987 lunch",
        '{"item": "burrito", "quantity": 9999, "spice": "mild", "notes": "for the department"}',
    ),
    (
        # A negative quantity means a negative price, which means the taqueria
        # pays the customer.
        "negative quantity (free money?)",
        '{"item": "bowl", "quantity": -40, "spice": "mild", "notes": "refund plz"}',
    ),
    (
        # Nachos are not on the menu. This reaches `MENU[item]` and raises
        # KeyError inside the kitchen.
        "not on the menu",
        '{"item": "nachos", "quantity": 1, "spice": "hot", "notes": ""}',
    ),
    (
        "spice level that does not exist",
        '{"item": "taco", "quantity": 2, "spice": "nuclear", "notes": "surprise me"}',
    ),
    (
        # An extra field nobody asked for. It is harmless here only because no
        # code reads it. If any code anywhere later did `data.get("price_override")`,
        # this order would cost nothing.
        "smuggled-in extra field",
        '{"item": "bowl", "quantity": 1, "spice": "mild", "notes": "", "price_override": 0.0}',
    ),
    (
        # Valid JSON is buried inside a friendly sentence. Models do this
        # constantly. `json.loads` fails on the very first character.
        "helpful preamble ruins the JSON",
        'Sure! Here is the order:\n{"item": "taco", "quantity": 1, "spice": "mild", "notes": ""}',
    ),
]


# --- Measuring helper --------------------------------------------------------


def count_code_lines(*objects) -> int:
    """Count the real lines of code in the given functions or classes.

    Blank lines, comments, and the docstring are not counted, so Part 1 and
    Part 2 can be compared fairly. This is only used for the printed scoreboard.
    """
    import ast
    import inspect
    import textwrap

    total = 0
    for obj in objects:
        source = inspect.getsource(obj)
        lines = source.splitlines()
        node = ast.parse(textwrap.dedent(source)).body[0]
        body = node.body
        # Skip a leading docstring, if there is one.
        if (
            isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            body = body[1:]
        if not body:
            continue
        for line in lines[body[0].lineno - 1 :]:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                total += 1
    return total


# --- Printing helpers --------------------------------------------------------
#
# These only make the terminal output easier to read. Nothing here is graded.

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
DIM = "\033[2m"
BOLD = "\033[1m"
OFF = "\033[0m"


def banner(text: str) -> None:
    """Print a section heading."""
    print(f"\n{BOLD}{'=' * 78}{OFF}")
    print(f"{BOLD}{text}{OFF}")
    print(f"{BOLD}{'=' * 78}{OFF}")


def accepted(label: str, detail: str = "") -> None:
    """The order passed our checks and was sent to the kitchen."""
    print(f"  {GREEN}ACCEPTED{OFF}  {label:<34} {DIM}{detail}{OFF}")


def rejected(label: str, detail: str = "") -> None:
    """The order was refused before it reached the kitchen."""
    print(f"  {RED}REJECTED{OFF}  {label:<34} {DIM}{detail}{OFF}")


def escaped(label: str, detail: str = "") -> None:
    """The order was accepted, but it should not have been.

    This is the column to watch. Every yellow line is a bad order that our
    checks let through and the kitchen then cooked.
    """
    print(f"  {YELLOW}ESCAPED {OFF}  {label:<34} {DIM}{detail}{OFF}")
