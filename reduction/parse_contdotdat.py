def parse_contdotdat(filepath):

    selections = []

    with open(filepath, 'r') as fh:
        for line in fh:
            if "LSRK" in line:
                selections.append(line.split()[0])


    return ";".join(selections)
