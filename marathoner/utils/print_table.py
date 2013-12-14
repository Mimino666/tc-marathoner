from six import print_


def print_table(*tables):
    '''Print tabular data in format:

    If `tables` is: [header, data, footer], then print:
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
    # calculate length for each column
    col_len = [0] * len(tables[0][0])
    def chlen(values):
        for i, c in enumerate(values):
            col_len[i] = max(col_len[i], len(str(c)))
    for table in tables:
        for row in table:
            chlen(row)

    # create formatting string
    format = '| %s |' %  ' | '.join('%%%ss' % l for l in col_len)
    hl = '|-%s-|' % '-|-'.join('-' * l for l in col_len)  # horizontal line

    print_(hl)
    for table in tables:
        print_('\n'.join(format % tuple(row) for row in table))
        print_(hl)
