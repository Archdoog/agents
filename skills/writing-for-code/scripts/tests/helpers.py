from writing_for_code.lint import lint


def codes(text, surface="doc", mode=None):
    return sorted(f.code for f in lint(text, surface, mode))


def first(text, code, surface="doc", mode=None):
    for f in lint(text, surface, mode):
        if f.code == code:
            return f
    return None
