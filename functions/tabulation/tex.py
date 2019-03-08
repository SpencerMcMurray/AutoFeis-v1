import os
from functions.databaseOps import get_comp_from_id, get_judges_from_comp
from latex import build_pdf


def cmd_judge_cols(data):
    """(dict of str:obj) -> str
    Creates the string of judge columns
    """
    ret = str()
    for i in range(len(data['dancers'][0].scores[data['judges'][0]['id']]['raw'])):
        ret += "c"*(len(data['dancers'][i].scores) + 1)
        ret += "|"
    return ret


def cmd_judges(data):
    """(dict of str:obj) -> str
    Creates the string of judge data
    """
    ret = str()
    for judge in data['judges']:
        ret += "\\multicolumn{" + str(len(data['dancers'][0].scores[judge['id']]['raw']) + 1) + "}{c|}{"
        ret += judge['name'] + "} & "
    return ret


def cmd_round_cols(data):
    """(dict of str:obj) -> str
    Creates the string of round columns
    """
    ret = str()
    for judge in data['judges']:
        for i in range(len(data['dancers'][0].scores[judge['id']]['raw'])):
            ret += "$R_" + str(i + 1) + "$ & "
        ret += "Grid & "
    return ret


def cmd_dancer(data):
    """(dict of str:obj) -> str
    Creates the string of dancer & mark data
    """
    ret = str()
    for dancer in data['dancers']:
        ret += str(dancer.place) + "&" + str(dancer.number) + "&" + "\\specialcell{" + dancer.name + "\\\\\\tiny{" +\
               dancer.school + "}" + "}"
        for judge in data['judges']:
            for score in dancer.scores[judge['id']]['raw']:
                ret += "&" + str(score)
            ret += "&" + str(dancer.scores[judge['id']]['grid'])
        ret += "&" + str(dancer.total_grid) + "\\\\\\hline"
    return ret


def cmd_comp_name(data):
    """(dict of str:obj) -> str
    Creates the string of comp info
    """
    return data['comp']['name']


commands = {"judgeCols": cmd_judge_cols, "judgeIter": cmd_judges, "roundCols": cmd_round_cols,
            "dancerIter": cmd_dancer, "compName": cmd_comp_name}


def generate_pdf(dancers, comp_id, outline):
    """(list of Dancer, int, str) -> NoneType
    Reads the tex outline given, fills in the correct data, and generates a pdf
    """
    # Create a folder for this competition
    dir_path = os.path.join("D:/Users/Spencer/Desktop/CS Projects/AutoFeis/static/storage/results", str(comp_id))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    comp = get_comp_from_id(comp_id)
    judges = get_judges_from_comp(comp_id)
    filled_tex = str()
    with open(outline, 'r') as tex:
        for line in tex:
            line = line.strip()
            # The % symbol indicates a place to insert data
            if line.startswith("%"):
                cmd = line[1:].split(" ")[0]
                line = commands[cmd]({"dancers": dancers, "comp": comp, "judges": judges})
            filled_tex += line + "\n"
    pdf = build_pdf(filled_tex)
    pdf.save_to(os.path.join(dir_path, "overall.pdf"))
