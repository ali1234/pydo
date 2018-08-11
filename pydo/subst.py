from textwrap import TextWrapper


def textwrap(string_or_list, prefix='', join=' ', width=120):
    """Generates wordwrapped lines for config files."""
    wrapper = TextWrapper(
        break_long_words=False, break_on_hyphens=False,
        initial_indent=prefix, subsequent_indent=prefix,
        width=width,
    )

    if isinstance(string_or_list, str):
        return wrapper.fill(string_or_list)
    else:
        return wrapper.fill(join.join(string_or_list))


def subst(template, output, substitutions):
    i = template.read_text()
    for k, v in substitutions.items():
        i = i.replace(k, v)

    if output.exists() and output.read_text() == i:
        return
    else:
        output.write_text(i)
