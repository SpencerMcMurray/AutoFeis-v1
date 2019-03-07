import os
from functions.databaseOps import get_comp_from_id, get_judges_from_comp


def cmd_judge_cols(data):
    """(dict of str:obj) -> str
    Creates the string of judge columns
    """
    ret = str()
    for judge_dancers in data['dancers']:
        ret += "c"*(len(judge_dancers[0].raw_scores) + 1)
        ret += "|"
    return ret


def cmd_judges(data):
    """(dict of str:obj) -> str
    Creates the string of judge data
    """
    ret = str()
    for judge in data['judges']:
        ret += "\\multicolumn{" + str(len(data['dancers'][judge['id']][0].raw_scores) + 1) + "}{c|}{" + judge['name']\
               + "} & "
    return ret


def cmd_round_cols(data):
    """(dict of str:obj) -> str
    Creates the string of round columns
    """
    ret = str()
    for judge in data['judges']:
        for i in range(len(data['dancers'][judge['id']][0].raw_scores)):
            ret += "R_" + str(i + 1) + " & "
        ret += "Grid & "
    return ret


def cmd_dancer(data):
    """(dict of str:obj) -> str
    Creates the string of dancer & mark data
    """
    pass


def cmd_dancer_info(data):
    """(dict of str:obj) -> str
    Creates the string of dancer info
    """
    pass


def cmd_comp_name(data):
    """(dict of str:obj) -> str
    Creates the string of comp info
    """
    return data['comp']['name']


commands = {"judgeCols": cmd_judge_cols, "judgeIter": cmd_judges, "roundCols": cmd_round_cols,
            "dancerIter": cmd_dancer, "dancerInfo": cmd_dancer_info, "compName": cmd_comp_name}


def fill_tex_file(dancers, comp_id, outline):
    """(list of Dancer, int, str) -> NoneType
    Reads the tex outline given, fills in the correct data, and generates a pdf
    """
    # Create a folder for this competition
    dir_path = "/static/results/" + str(comp_id)
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
                # Don't do any sub-commands in the initial parse
                if cmd != "sub":
                    line = commands[cmd]({"dancers": dancers, "comp": comp, "judges": judges})
