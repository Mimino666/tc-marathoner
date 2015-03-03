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
    column_width = [0] * len(tables[0][0])
    def update_column_widths(row):
        for i, data in enumerate(row):
            column_width[i] = max(column_width[i], len(str(data)))
    for table in tables:
        for row in table:
            update_column_widths(row)

    # create formatting string
    format = '| %s |' %  ' | '.join('%%%ss' % width for width in column_width)
    hline = '|-%s-|' % '-|-'.join('-' * width for width in column_width)  # horizontal line

    print_(hline)
    for table in tables:
        print_('\n'.join(format % tuple(row) for row in table))
        print_(hline)
