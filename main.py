import requests
from termcolor import colored, cprint
import json
import yaml
import sys
import os
import time
from time import gmtime, strftime

DEF_INTERVAL = 20
DEF_YAML_NAME = "config.yaml"
ID_REQUEST = "https://api.wotblitz.eu/wotb/account/list/?application_id=764b6c8efd0be91d12e49fbe3b65eb55&search="
STATS_REQUEST = "https://api.wotblitz.eu/wotb/account/info/?application_id=764b6c8efd0be91d12e49fbe3b65eb55&account_id="

def main():
    while 1:
        DEF_YAML_NAME = input("> Enter path for MODULE-STATS.yaml: ")
        if (os.path.isfile(DEF_YAML_NAME)):
            cprint("[1] File found!", 'white', 'on_green')
            break
        else: 
            cprint("[0] File not found!", 'white', 'on_red')

    while 1:
        name = input("> Enter player name: ")
        try: 
            id_request = json.loads(requests.get(ID_REQUEST + name).text)
        except Exception as E:
            cprint("[0] Cannot parse json response from WG API: " + str(E), 'white', 'on_red')
        if id_request["status"] == "error" or id_request["meta"]["count"] == 0:
            cprint("[0] not a valid name!", 'white', 'on_red')
        else: 
            break


    player_id = id_request["data"][0]["account_id"]
    player_ign = id_request["data"][0]["nickname"]

    try: 
        stats_request = json.loads(requests.get(STATS_REQUEST + str(player_id)).text)
    except Exception as E:
        cprint("[0] Cannot parse json response from WG API: " + str(E), 'white', 'on_red')

    # cprint("[1] Parsing json response from WG API", 'white', 'on_green')
    cprint(f"[1] Player: {player_ign}/{player_id} Found!", 'white', 'on_green')
    cprint("[1] Session tracking begins at " + strftime("%Y-%m-%d %H:%M:%S", gmtime()), 'white', 'on_yellow')

    stats_request = stats_request["data"][str(player_id)]["statistics"]["all"]
    init_battles      = stats_request["battles"]
    init_wins         = stats_request["wins"]
    init_damage_dealt = stats_request["damage_dealt"]

    # necessary data
    x = 0
    while True:
        # fetch new stats
        try:
            stats_request = json.loads(requests.get(STATS_REQUEST + str(player_id)).text)
            stats_request = stats_request["data"][str(player_id)]["statistics"]["all"]
        except Exception as E:
            cprint("[0] Cannot parse json response from WG API: " + str(E), 'white', 'on_red')

        # get the important needed data
        cur_battles      = stats_request["battles"]
        cur_wins         = stats_request["wins"]
        cur_damage_dealt = stats_request["damage_dealt"]

        # calculate it

        played_battles = cur_battles - init_battles
        wins = cur_wins - init_wins
        losses = played_battles - wins
        if (played_battles == 0):
            winrate = 0
            average = 0
        else:
            winrate = wins * 100 / played_battles
            average = (cur_damage_dealt - init_damage_dealt) / played_battles

        # import yaml file

        try: 
            with open(DEF_YAML_NAME, 'r') as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
                # print("DATA: ", data)
        except Exception as E:
            cprint("[0] Cannot parse yaml: " + str(E), 'white', 'on_red')

        data["Prototypes"][0]["children"][0]["components"]["UITextComponent"]["text"] = f"L: {losses}"
        data["Prototypes"][0]["children"][1]["components"]["UITextComponent"]["text"] = f"W: {wins}"
        data["Prototypes"][0]["children"][2]["components"]["UITextComponent"]["text"] = f"B: {played_battles}"
        data["Prototypes"][0]["children"][3]["components"]["UITextComponent"]["text"] = f"WR: {round(winrate, 2)}"

        if  (x < played_battles):
            print(colored(f"B/W/L: {played_battles}/{wins}/{losses: <3}", 'grey', 'on_white'), end='', flush=True)
            if 0 <= winrate < 50:
                print(colored(f"WR: {round(winrate,2): <5}", 'white', 'on_red'), end='', flush=True)
            elif 50 <= winrate < 60:
                print(colored(f"WR: {round(winrate,2): <5}", 'white', 'on_green'), end='', flush=True)
            elif 60 <= winrate < 70:
                print(colored(f"WR: {round(winrate,2): <5}", 'white', 'on_blue'), end='', flush=True)
            else:  # winrate >= 70
                print(colored(f"WR: {round(winrate,2): <5}", 'white', 'on_magenta'), end='', flush=True)

            if 0 <= average < 1500:
                print(colored(f"AVG: {round(average, 1): <6}", 'white', 'on_red'), end='', flush=True)
            elif 1500 <= average < 2000:
                print(colored(f"AVG: {round(average, 1): <6}", 'white', 'on_green'), end='', flush=True)
            elif 2000 <= average < 3000:
                print(colored(f"AVG: {round(average, 1): <6}", 'white', 'on_blue'), end='', flush=True)
            else:  # average >= 70
                print(colored(f"AVG: {round(average, 1): <6}", 'white', 'on_magenta'), end='', flush=True)
            x += 1
            print("")

        try: 
            with open(DEF_YAML_NAME, 'w') as file:
                file.write(str(data))
        except Exception as E:
            cprint("[0] Cannot write to yaml: " + str(E), 'white', 'on_red')

        time.sleep(DEF_INTERVAL)  # 


if __name__ == "__main__": 
    main()
