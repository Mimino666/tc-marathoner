from six import print_


def print_table(header, table, footer=None):
    '''Print tabular data in format:
        ----------|---------|-----|
        | header1 | header2 | ... |
        | headerx | headery | ... |
        |---------|---------|-----|
        |   data1 |   data2 | ... |
        |   datax |   datay | ... |
        |---------|---------|-----|
        | footer1 | footer2 | ... |
        | footerx | footery | ... |
        |---------|---------|-----|

    '''
    num_rows, num_cols = len(table), len(table[0])
    # calculate length for each column
    col_len = [0] * num_cols
    def chlen(values):
        for i, c in enumerate(values):
            col_len[i] = max(col_len[i], len(str(c)))
    if header:
        for v in header:
            chlen(v)
    for v in table:
        chlen(v)
    if footer:
        for v in footer:
            chlen(v)

    # create formatting string
    format = '| %s |' %  ' | '.join('%%%ss' % l for l in col_len)
    hl = '|-%s-|' % '-|-'.join('-' * l for l in col_len)  # horizontal line

    if header:
        print_(hl)
        print_('\n'.join(format % tuple(row) for row in header))
    print_(hl)
    print_('\n'.join(format % tuple(row) for row in table))
    print_(hl)
    if footer:
        print_('\n'.join(format % tuple(row) for row in footer))
        print_(hl)
