import graphviz
import gspread


def retrieve_data():
    """
    :return: dict
    """
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1KERZ3EAbzhzQWfyZWe6VGRE-UcP-GGRJu_6k1p51u7I/edit#gid=1765020200"
    gc = gspread.oauth()
    sheet = gc.open_by_url(SHEET_URL)
    worksheet = sheet.worksheet("Form Responses 1")

    grand_bigs = worksheet.col_values(2)[1:]
    bigs = worksheet.col_values(3)[1:]
    littles = worksheet.col_values(4)[1:]
    families = worksheet.col_values(5)[1:]
    names = worksheet.col_values(6)[1:]

    return {"GB": grand_bigs, "B": bigs, "L": littles, "F": families, "N": names}, worksheet.get_all_values()


def main():
    graph = graphviz.Digraph("family-tree", comment="Family Tree")
    data, all_values = retrieve_data()

    id_number = 0
    name_labels = {}
    relationships = {}

    for name in data["GB"]:
        if name not in name_labels and not name == "":
            name_labels[name] = str(id_number)
            id_number += 1

    for name in data["B"]:
        if name not in name_labels and not name == "":
            name_labels[name] = str(id_number)
            id_number += 1

    for name in data["N"]:
        if name not in name_labels and not name == "":
            name_labels[name] = str(id_number)
            id_number += 1

    for name in data["L"]:
        if name == "":
            continue
        littles = name.split(',')
        for little in littles:
            cleaned_name = little.strip()
            print(cleaned_name)
            if cleaned_name not in name_labels:
                name_labels[cleaned_name] = str(id_number)
                id_number += 1

    for key in name_labels:
        print(key, name_labels[key])

    # Create all the nodes.
    for key in name_labels:
        graph.node(name_labels[key], key)

    for item in enumerate(all_values[1:]):
        records = item[1]
        # Set grand big little.
        if records[1] != "":
            a = name_labels[records[1]]
            b = name_labels[records[2]]
            if not a+b in relationships:
                graph.edge(a,b)
                relationships[a+b] = None
        # set name little
        if records[3] != "":
            littles = records[3].split(',')
            for little in littles:
                cleaned_name = little.strip()
                if not name_labels[records[5]] + name_labels[cleaned_name] in relationships:
                    graph.edge(name_labels[records[5]], name_labels[cleaned_name])
                    relationships[name_labels[records[5]] + name_labels[cleaned_name]] = None

        # Set big to name.
        if not name_labels[records[2]] + name_labels[records[5]] in relationships:
            graph.edge(name_labels[records[2]], name_labels[records[5]])
            relationships[name_labels[records[2]] + name_labels[records[5]]] = None

    graph.render(directory='doctest-output', view=True)


if __name__ == "__main__":
    main()
