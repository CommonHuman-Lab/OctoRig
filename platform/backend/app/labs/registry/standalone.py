# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from ._types import ChallengeDef

STANDALONE_CHALLENGES: list[ChallengeDef] = [  # type: ignore[assignment]
    {
        "slug": "py-reverse-gear",
        "title": "Reverse Gear",
        "description": "Something got flipped. Can you read it the right way?",
        "challenge_type": "short_answer",
        "difficulty": "easy",
        "category": "python",
        "tags": ["python", "strings"],
        "skills": [],
        "points": 50,
        "content": {
            "code_snippet": 'text = "OctoRig"',
            "language": "python",
        },
        "flags": [{"value": "giRotoO", "flag_type": "static", "case_sensitive": True}],
        "hints": [
            {"order_num": 1, "content": "Run it in a Python interpreter to verify.", "cost": 0},
        ],
    },
    {
        "slug": "py-sum-squares",
        "title": "Sum of Squares",
        "description": "Three integers, squared and summed. What's the total?",
        "challenge_type": "short_answer",
        "difficulty": "easy",
        "category": "python",
        "tags": ["python", "math"],
        "skills": [],
        "points": 50,
        "content": {
            "code_snippet": "result = sum(x**2 for x in range(1, 4))",
            "language": "python",
        },
        "flags": [{"value": "14", "flag_type": "static", "case_sensitive": False}],
        "hints": [
            {
                "order_num": 1,
                "content": "range(1, 4) produces the integers 1, 2, and 3.",
                "cost": 0,
            },
        ],
    },
    {
        "slug": "py-bit-mask",
        "title": "Bit Mask",
        "description": "Two binary patterns overlap. What remains after the filter is applied?",
        "challenge_type": "short_answer",
        "difficulty": "easy",
        "category": "python",
        "tags": ["python", "bitwise"],
        "skills": [],
        "points": 75,
        "content": {
            "code_snippet": "x = 0b1010\ny = 0b1100",
            "language": "python",
        },
        "flags": [{"value": "8", "flag_type": "static", "case_sensitive": False}],
        "hints": [
            {
                "order_num": 1,
                "content": "The & operator keeps only bits that are 1 in both operands.",
                "cost": 0,
            },
            {"order_num": 2, "content": "0b1000 in decimal is 8.", "cost": 25},
        ],
    },
    {
        "slug": "py-last-in-line",
        "title": "Last in Line",
        "description": "The sequence is generated. Only the final element matters.",
        "challenge_type": "short_answer",
        "difficulty": "easy",
        "category": "python",
        "tags": ["python", "lists"],
        "skills": [],
        "points": 50,
        "content": {
            "code_snippet": "nums = [i * 3 for i in range(1, 6)]",
            "language": "python",
        },
        "flags": [{"value": "15", "flag_type": "static", "case_sensitive": False}],
        "hints": [
            {
                "order_num": 1,
                "content": "range(1, 6) produces five values. nums[-1] is the last one.",
                "cost": 0,
            },
        ],
    },
    {
        "slug": "py-stripped",
        "title": "Stripped",
        "description": "Whitespace hides the truth. Remove it, then replace the gaps.",
        "challenge_type": "short_answer",
        "difficulty": "easy",
        "category": "python",
        "tags": ["python", "strings"],
        "skills": [],
        "points": 50,
        "content": {
            "code_snippet": 's = "  hello world  "',
            "language": "python",
        },
        "flags": [{"value": "hello_world", "flag_type": "static", "case_sensitive": True}],
        "hints": [
            {
                "order_num": 1,
                "content": "strip() removes leading/trailing whitespace. replace() handles the rest.",
                "cost": 0,
            },
        ],
    },
    {
        "slug": "py-letter-count",
        "title": "Letter Count",
        "description": "A letter repeats through the swamp. How many times?",
        "challenge_type": "short_answer",
        "difficulty": "easy",
        "category": "python",
        "tags": ["python", "strings"],
        "skills": [],
        "points": 50,
        "content": {
            "code_snippet": 'word = "mississippi"',
            "language": "python",
        },
        "flags": [{"value": "4", "flag_type": "static", "case_sensitive": False}],
        "hints": [
            {"order_num": 1, "content": "Trace through: m-i-s-s-i-s-s-i-p-p-i", "cost": 0},
        ],
    },
    {
        "slug": "py-sorted-unique",
        "title": "Sorted Unique",
        "description": "Duplicates removed, sorted ascending. What sits at index 2?",
        "challenge_type": "short_answer",
        "difficulty": "easy",
        "category": "python",
        "tags": ["python", "lists", "sets"],
        "skills": [],
        "points": 75,
        "content": {
            "code_snippet": "nums = [3, 1, 4, 1, 5, 9, 2, 6]",
            "language": "python",
        },
        "flags": [{"value": "3", "flag_type": "static", "case_sensitive": False}],
        "hints": [
            {
                "order_num": 1,
                "content": "set() removes duplicates. sorted() returns them in ascending order. Indexing is zero-based.",
                "cost": 0,
            },
            {
                "order_num": 2,
                "content": "After dedup and sort: [1, 2, 3, 4, 5, 6, 9]. Index 2 is the third element.",
                "cost": 25,
            },
        ],
    },
    {
        "slug": "py-chained-keys",
        "title": "Chained Keys",
        "description": "Three pairs, zipped into a map. Retrieve what was stored at the middle key.",
        "challenge_type": "short_answer",
        "difficulty": "easy",
        "category": "python",
        "tags": ["python", "dictionaries"],
        "skills": [],
        "points": 50,
        "content": {
            "code_snippet": 'keys = ["alpha", "beta", "gamma"]\nvals = [10, 20, 30]\nd = dict(zip(keys, vals))',
            "language": "python",
        },
        "flags": [{"value": "20", "flag_type": "static", "case_sensitive": False}],
        "hints": [
            {
                "order_num": 1,
                "content": "zip() pairs each key with the value at the same position.",
                "cost": 0,
            },
        ],
    },
    {
        "slug": "py-b64-decode",
        "title": "Encoded Cargo",
        "description": (
            "A familiar encoding scheme wraps the contents — no encryption, no key, "
            "just a different way of writing the same bytes. What does it say?"
        ),
        "challenge_type": "short_answer",
        "difficulty": "easy",
        "category": "python",
        "tags": ["python", "encoding"],
        "skills": [],
        "points": 75,
        "content": {
            "code_snippet": "import base64\ndata = b'T2N0b1JpZw=='",
            "language": "python",
        },
        "flags": [{"value": "OctoRig", "flag_type": "static", "case_sensitive": True}],
        "hints": [
            {
                "order_num": 1,
                "content": "The standard library has a module built for exactly this encoding scheme.",
                "cost": 0,
            },
            {
                "order_num": 2,
                "content": "The result is a bytes object — decode it to a plain string.",
                "cost": 25,
            },
        ],
    },
    {
        "slug": "py-hex-parse",
        "title": "Hex Dump",
        "description": (
            "The message arrived as a string of hex digits. Each pair is one byte. Reassemble it."
        ),
        "challenge_type": "short_answer",
        "difficulty": "easy",
        "category": "python",
        "tags": ["python", "encoding", "bytes"],
        "skills": [],
        "points": 75,
        "content": {
            "code_snippet": "raw = '4f637461'",
            "language": "python",
        },
        "flags": [{"value": "Octa", "flag_type": "static", "case_sensitive": True}],
        "hints": [
            {"order_num": 1, "content": "Two hex digits map to one ASCII character.", "cost": 0},
            {
                "order_num": 2,
                "content": "bytes has a class method that parses hex strings directly.",
                "cost": 25,
            },
        ],
    },
    {
        "slug": "py-caesar-crack",
        "title": "Rotary Dial",
        "description": (
            "Every letter has been shifted by the same fixed amount. "
            "The shift is somewhere between 1 and 25 — only one produces "
            "a recognisable word. What is the plaintext?"
        ),
        "challenge_type": "short_answer",
        "difficulty": "medium",
        "category": "python",
        "tags": ["python", "crypto", "brute-force"],
        "skills": [],
        "points": 100,
        "content": {
            "code_snippet": "ciphertext = 'Clguba'",
            "language": "python",
        },
        "flags": [{"value": "Python", "flag_type": "static", "case_sensitive": False}],
        "hints": [
            {
                "order_num": 1,
                "content": "Try every shift value in a loop and print each candidate.",
                "cost": 0,
            },
            {
                "order_num": 2,
                "content": "chr() and ord() let you shift individual characters; preserve case.",
                "cost": 25,
            },
            {
                "order_num": 3,
                "content": "There are 25 possible shifts. One of them is particularly well-known.",
                "cost": 50,
            },
        ],
    },
    {
        "slug": "py-regex-hunt",
        "title": "Pattern Match",
        "description": (
            "A blob of noisy text hides tokens that follow a specific structure. "
            "Something in the code isolates them — run it and report what surfaces."
        ),
        "challenge_type": "short_answer",
        "difficulty": "medium",
        "category": "python",
        "tags": ["python", "regex"],
        "skills": [],
        "points": 100,
        "content": {
            "code_snippet": (
                "import re\n"
                "text = 'err [ALPHA] ok [BRAVO] skip abc [CHARLIE] end'\n"
                "matches = re.findall(r'\\[[A-Z]{5,7}\\]', text)"
            ),
            "language": "python",
        },
        "flags": [
            {
                "value": "['[ALPHA]', '[BRAVO]', '[CHARLIE]']",
                "flag_type": "static",
                "case_sensitive": True,
            }
        ],
        "hints": [
            {
                "order_num": 1,
                "content": "re.findall returns all non-overlapping matches as a list.",
                "cost": 0,
            },
            {
                "order_num": 2,
                "content": "The pattern requires uppercase only; {5,7} sets the length range.",
                "cost": 25,
            },
        ],
    },
    {
        "slug": "py-exception-flow",
        "title": "Caught in the Act",
        "description": (
            "Control flow through error handlers can be tricky. "
            "Trace what gets printed when this snippet runs — "
            "every branch matters."
        ),
        "challenge_type": "short_answer",
        "difficulty": "medium",
        "category": "python",
        "tags": ["python", "exceptions"],
        "skills": [],
        "points": 125,
        "content": {
            "code_snippet": (
                "try:\n"
                "    x = int('abc')\n"
                "except ValueError:\n"
                "    print('caught')\n"
                "else:\n"
                "    print('clean')\n"
                "finally:\n"
                "    print('done')"
            ),
            "language": "python",
        },
        "flags": [{"value": "caught\ndone", "flag_type": "static", "case_sensitive": True}],
        "hints": [
            {
                "order_num": 1,
                "content": "The else branch only runs when no exception was raised.",
                "cost": 0,
            },
            {
                "order_num": 2,
                "content": "finally always runs — whether or not an exception occurred.",
                "cost": 25,
            },
        ],
    },
    {
        "slug": "py-generator-sum",
        "title": "Lazy Accumulator",
        "description": (
            "A generator filters and transforms a range before summing it. What is the total?"
        ),
        "challenge_type": "short_answer",
        "difficulty": "medium",
        "category": "python",
        "tags": ["python", "generators", "comprehensions"],
        "skills": [],
        "points": 125,
        "content": {
            "code_snippet": "result = sum(x * 2 for x in range(10) if x % 3 == 0)",
            "language": "python",
        },
        "flags": [{"value": "36", "flag_type": "static", "case_sensitive": False}],
        "hints": [
            {
                "order_num": 1,
                "content": "Identify which values in range(10) satisfy the condition first.",
                "cost": 0,
            },
            {
                "order_num": 2,
                "content": "The qualifying values are 0, 3, 6, 9 — each doubled before summing.",
                "cost": 25,
            },
        ],
    },
    {
        "slug": "py-class-mro",
        "title": "Method Order",
        "description": (
            "Python resolves method calls through a specific linearisation of the "
            "class hierarchy. Follow it and determine what this prints."
        ),
        "challenge_type": "short_answer",
        "difficulty": "hard",
        "category": "python",
        "tags": ["python", "oop", "mro"],
        "skills": [],
        "points": 150,
        "content": {
            "code_snippet": (
                "class A:\n"
                "    def greet(self):\n"
                "        print('A')\n\n"
                "class B(A):\n"
                "    def greet(self):\n"
                "        super().greet()\n"
                "        print('B')\n\n"
                "class C(B):\n"
                "    def greet(self):\n"
                "        super().greet()\n"
                "        print('C')\n\n"
                "C().greet()"
            ),
            "language": "python",
        },
        "flags": [{"value": "A\nB\nC", "flag_type": "static", "case_sensitive": True}],
        "hints": [
            {
                "order_num": 1,
                "content": "super() follows the MRO — C → B → A. Each call completes before the print below it runs.",
                "cost": 0,
            },
            {
                "order_num": 2,
                "content": "Think of it as a call stack: C's super() enters B, B's super() enters A, then A prints, then B prints, then C prints.",
                "cost": 25,
            },
        ],
    },
]
