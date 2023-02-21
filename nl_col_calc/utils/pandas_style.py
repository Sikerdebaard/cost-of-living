def stylize(df, allow_decimals=False):
    df = df.copy()

    style = df.style.format(
        formatter=lambda x: getformatter(x),
        subset=None,
        na_rep=' ',
        precision=None,
        decimal='.',
        thousands=None,
        escape=None,
        hyperlinks=None
    )

    return style


def getformatter(x):
    if isinstance(x, (int, float)):
        return f'{x:.00f}'

    return str(x)
