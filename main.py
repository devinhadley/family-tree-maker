import subprocess
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

    return worksheet.get_all_values()


def create_graph(current_family, families):
    graph = graphviz.Digraph("family-tree", comment="Family Tree")
    all_values = retrieve_data()

    id_number = 0
    name_labels = {}
    relationships = {}

    for item in all_values[1:]:

        if item[4] not in families:
            print("Invalid Family:", item[4])
            continue

        if item[4] != current_family:
            continue

        for index, name in enumerate(item):
            # If not a member of the current family then skip this person.
            if index == 1:
                # Grand Big
                if name not in name_labels and not name == "":
                    name_labels[name.strip()] = str(id_number)
                    id_number += 1

            elif index == 2:
                # Big
                if name not in name_labels and not name == "":
                    name_labels[name.strip()] = str(id_number)
                    id_number += 1

            elif index == 5:
                # Name
                if name not in name_labels and not name == "":
                    name_labels[name.strip()] = str(id_number)
                    id_number += 1

            elif index == 3:
                # Little(s)
                for sub_name in name:
                    if name == "":
                        continue
                    littles = name.split(',')
                    for little in littles:
                        cleaned_name = little.strip()
                        if cleaned_name not in name_labels:
                            name_labels[cleaned_name] = str(id_number)
                            id_number += 1

    # for key in name_labels:
    #     print(key, name_labels[key])

    # Create all the nodes.
    for key in name_labels:
        graph.node(name_labels[key], key)

    for item in enumerate(all_values[1:]):
        records = item[1]
        # Set grand big little.
        # If not a member of the current family then skip this person.
        if records[4] != current_family:
            continue
        if records[1] != "":
            a = name_labels[records[1].strip()]
            b = name_labels[records[2].strip()]
            if not a+b in relationships:
                graph.edge(a,b)
                relationships[a+b] = None
        # set name little
        if records[3] != "":
            littles = records[3].split(',')
            for little in littles:
                cleaned_name = little.strip()
                if not name_labels[records[5].strip()] + name_labels[cleaned_name] in relationships:
                    graph.edge(name_labels[records[5].strip()], name_labels[cleaned_name])
                    relationships[name_labels[records[5].strip()] + name_labels[cleaned_name]] = None

        # Set big to name.
        if not name_labels[records[2].strip()] + name_labels[records[5].strip()] in relationships:
            graph.edge(name_labels[records[2].strip()], name_labels[records[5].strip()])
            relationships[name_labels[records[2].strip()] + name_labels[records[5].strip()]] = None

    graph.render(directory='graph')

    #Write the title.
    contents = None
    with open("graph/family-tree.gv", "r") as file:
        contents = file.readlines()
        contents.insert(2, "\tlabelloc=\"t\"\n")
        contents.insert(3, f"\tlabel=\"{current_family} Family\"\n")

    with open("graph/family-tree.gv", "w") as file:
        contents = "".join(contents)
        file.write(contents)

    subprocess.run(["dot", '-Tpng','graph/family-tree.gv', '-o', 'graph/family-tree.png'])

    



if __name__ == "__main__":
    families = ['White', 'Toon', 'Big Mack', 'Borracho', 'Keystone']
    create_graph('White', families)
