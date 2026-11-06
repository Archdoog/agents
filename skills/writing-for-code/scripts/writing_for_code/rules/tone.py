"""Rules for the tone of one surface: error messages and review comments."""

from __future__ import annotations

from ..model import WARNING
from . import rule
from ._match import find_phrases

ERROR_FILLER = [
    "oops", "whoops", "uh oh", "uh-oh", "something went wrong",
    "an error occurred", "an unknown error", "sorry", "we apologize",
    "please try again later",
]

REVIEW_FILLER = [
    "great work", "great job", "nice work", "nice job", "awesome work",
    "lgtm", "looks good to me", "looks great", "overall looks good",
    "just a few nits", "keep up the good work",
]


@rule("ERR001", "vague-error",
      "Apology or vague text in an error. Name what failed and the next action.",
      strict=WARNING, surfaces=("error",))
def vague_error(text, ctx):
    for offset, phrase in find_phrases(text, ERROR_FILLER):
        yield offset, (f"{phrase!r} tells the reader nothing. Name what failed "
                       f"and what to do next.")


@rule("REVIEW001", "review-filler",
      "Praise or sign-off in a review comment. Post the finding only.",
      strict=WARNING, surfaces=("review",))
def review_filler(text, ctx):
    for offset, phrase in find_phrases(text, REVIEW_FILLER):
        yield offset, f"{phrase!r} is not a finding. Delete it."
