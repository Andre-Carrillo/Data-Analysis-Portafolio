from pdfinterpreter import pdf_to_vote_list
import re

#We are going to make a dictionary that contains the id of the congressman and then make the name 


def name_to_id(name, congressnames):
    names_wo_spaces = dict(enumerate([re.sub(r"[\s*]", "",i.strip()).lower() for i in congressnames]))
    #First we account for brothers in Congress
    if "Héctor" in name:
        id = 1
    elif "María" in name and "Acuña" in name:
        id = 0
    elif name == "CorderoJonTay":
        id = 32
    elif name == "MaríaCorderoJonTay":
        id = 33
    elif name == "LuisCorderoJonTay":
        id = 32
    elif name == "AlcarrazAgüero":
        id = 4
    elif name == "FloresRuiz":
        id = 49
    elif name == "JeríOré":
        id = 61
    elif name == "RuizRodríguez":
        id = 111
    elif name == "VenturaÁngel":
        id = 128
    else:
        for key, value in names_wo_spaces.items():
            if name.lower() in value:
                id = key
                break
        else:
            print(name)
            id = -1
    return id

def 

for votacion in VOTACIONES.copy():
    if "A FAVOR" in votacion:
        votacion["A FAVOR"] = [name_to_id(re.sub(r"[\s]*?", "", i),list(Congress["Congresista"])) for i in votacion["A FAVOR"]]
    # Check if 'EN CONTRA' key exists before accessing it
    if "EN CONTRA" in votacion:
        votacion["EN CONTRA"] = [name_to_id(re.sub(r"[\s]*?", "", i),list(Congress["Congresista"])) for i in votacion["EN CONTRA"]]
    # Check if 'ABSTENCION' key exists before accessing it
    if "ABSTENCION" in votacion:
        votacion["ABSTENCION"] = [name_to_id(re.sub(r"[\s]*?", "", i),list(Congress["Congresista"])) for i in votacion["ABSTENCION"]]