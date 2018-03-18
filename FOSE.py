#!/usr/bin/python3

__author__ = 'John'
__version__ = "2.0"
__status__ = "Production"
__credits__ = ["Visual Studio"]


"""
fos.py - THE ORIGINAL Fallout Shelter Editor - v2.0
Visual Studio @ https://www.se7ensins.com/members/visual-studio.91007/

Notes:
    - This has been personally tested on Fallout Shelter v1.11.1 for Steam
    - This script requires pycryptodomex >= 3.4.5 (pycrypto for python 3) for AES
"""

#internal libraries
import json
import base64
from hashlib import sha1
from enum import IntEnum
from shutil import copyfile
from binascii import unhexlify
from traceback import print_exc
from argparse import ArgumentParser
from time import strftime, localtime
from os import mkdir, getenv, listdir
from os.path import isfile, isdir, join

#external libraries
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad

SAVE_KEY_HASH = "5fae417442dc605aedfdca305d3cdbb4c21e658b"
SAVE_IV_HASH = "eaf6c9a66fdfc044dbed4cbc66efcd7c594864a6"

BACKUP_DIR = "backups"

class Item(IntEnum):
    LUNCHBOX = 0
    HANDYMAN = 1
    CARRIER = 2

    def __int__(self):
        return self.value

#looks like they implemented another way to generate a key, however, they don't use it :/
def gen_passphrase(file_name: str) -> str:
    if len(file_name) < 8:
        file_name += file_name
    return base64.b64encode(file_name)[:8]#, SALT, 32)

def decrypt_save_data(data: str) -> str:
    global SAVE_KEY
    global SAVE_IV
    return str(unpad(AES.new(SAVE_KEY, AES.MODE_CBC, iv=SAVE_IV).decrypt(base64.b64decode(data)), AES.block_size), "utf8")

def encrypt_save_data(data: str) -> str:
    global SAVE_KEY
    global SAVE_IV
    return str(base64.b64encode(AES.new(SAVE_KEY, AES.MODE_CBC, iv=SAVE_IV).encrypt(pad(bytes(data, "utf8"), AES.block_size))), "utf8")

"""
def add_item(data, amount, item_id = Item.LUNCHBOX):
    for x in range(0, amount):
        if item_id == Item.LUNCHBOX:
            data["vault"]["LunchBoxesByType"].append(int(item_id))
            data["vault"]["LunchBoxesCount"] += 1
        elif item_id == Item.CARRIER or item_id == Item.HANDYMAN:
            data["vault"]["LunchBoxesByType"].append(item_id)
    return data
"""

def json_path_get(data: dict, path: str) -> str:
    temp_loc = data
    for single in path.split("/"):
        if single in temp_loc:
            temp_loc = temp_loc[single]
    return temp_loc

class utils(object):
    @staticmethod
    def parse_base64(s: str) -> bool:
        try:
            base64.b64decode(s)
            return True
        except:
            return False

    @staticmethod
    def parse_json(s: str) -> bool:
        try:
            json.loads(s)
            return True
        except:
            return False

    @staticmethod
    def minify_json(s: str) -> str:
        return json.dumps(s, separators=(",", ":"))

#start the script
if __name__ == "__main__":
    parser = ArgumentParser(description="A script to edit Fallout Shelter saves on PC (Steam, Bethesda, and Windows Store), Android, and iOS")
    parser.add_argument("-i", "--in-file", type=str, help="The .sav file you want to read from")
    parser.add_argument("-o", "--out-file", type=str, help="The .sav file you want to write to")
    parser.add_argument("-l", "--list", action="store_true", help="List available save games (Steam & Bethesda launchers only)")
    parser.add_argument("-j", "--in-json", type=str, help="A .json file that you want to encrypt")
    parser.add_argument("-d", "--dump", action="store_true", help="Dump to a .json file")
    parser.add_argument("-nb", "--no-backup", action="store_true", help="Don't backup the save")

    #modifications
    #integers
    parser.add_argument("--lunchboxes", type=int, help="The amount of lunchboxes you want to add to your save")
    parser.add_argument("--handymen", type=int, help="The amount of Mr. Handymen you want to add to your save")
    parser.add_argument("--carriers", type=int, help="The amount of pet carriers you want to add to your save")
    parser.add_argument("--caps", type=int, help="The amount of caps you want")
    parser.add_argument("--quantum", type=int, help="The amount of nuka-quantum you want")
    parser.add_argument("--food", type=int, help="The amount of food you want")
    parser.add_argument("--energy", type=int, help="The amount of energy you want")
    parser.add_argument("--water", type=int, help="The amount of water you want")
    parser.add_argument("--stim-packs", type=int, help="The amount of stimpacks you want")
    parser.add_argument("--rad-aways", type=int, help="The amount of rad away's you want")

    #booleans
    parser.add_argument("--max-dwellers", action="store_true", help="Max all dweller stats")
    parser.add_argument("--remove-rocks", action="store_true", help="Remove all rocks")
    parser.add_argument("--remove-lunchboxes", action="store_true", help="Removes all lunchboxes")
    parser.add_argument("--remove-handymen", action="store_true", help="Removes all Mr. Handymen")
    parser.add_argument("--remove-carriers", action="store_true", help="Remove all pet carriers")
    parser.add_argument("--remove-elevator", action="store_true", help="Remove the elevator that it starts you with")

    #strings
    parser.add_argument("--vault-name", type=str, help="The name you want to change your vault to")

    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument("--save-key", type=str, required=True, help="The key used to encrypt/decrypt saves as hex")
    required_args.add_argument("--save-iv", type=str, required=True, help="The IV used to encrypt/decrypt saves as hex")

    args = parser.parse_args()

    try:
        #test the key and IV, for legal reasons I'm not going to give these out
        assert args.save_key is not None and len(args.save_key) == 64 and sha1(unhexlify(args.save_key)).hexdigest() == SAVE_KEY_HASH, "Invalid save key" #32 bytes
        assert args.save_iv is not None and len(args.save_iv) == 32 and sha1(unhexlify(args.save_iv)).hexdigest() == SAVE_IV_HASH, "Invalid save IV"  #16 bytes

        #load the key and IV
        global SAVE_KEY
        global SAVE_IV
        SAVE_KEY = unhexlify(args.save_key)
        SAVE_IV = unhexlify(args.save_iv)

        #create the backup directory
        if not isdir(BACKUP_DIR):
            mkdir(BACKUP_DIR)

        if args.in_file:  #handle modifying a save file
            if isfile(args.in_file):
                #decrypt the save and parse it
                save_data = open(args.in_file, "r").read()
                dec_data = decrypt_save_data(save_data)
                modded_json = json.loads(dec_data)

                #checked info
                app_ver = modded_json["appVersion"].strip()

                #backups
                if args.no_backup:
                    print("Backup skipped!")
                else:
                    backup_name = join(BACKUP_DIR, strftime("%m-%d-%Y_%I-%M-%S", localtime()) + ".sav")
                    copyfile(args.in_file, backup_name)
                    print("Save backed-up to \"{}\"".format(backup_name))

                #dump to json file
                if args.dump:
                    json_file = args.in_file.replace(".sav", "").split("/")[-1] + "_dumped.json"
                    open(json_file, "w").write(json.dumps(modded_json, indent=4))
                    print("Save file successfully dumped!")

                #begin modifications
                #lunchboxes
                if args.lunchboxes and args.lunchboxes > 0:
                    for x in range(0, args.lunchboxes):
                        modded_json["vault"]["LunchBoxesByType"].append(int(Item.LUNCHBOX))
                        modded_json["vault"]["LunchBoxesCount"] += 1
                    print("Added {} lunchboxes".format(args.lunchboxes))
                #Mr. Handyman
                if args.handymen and args.handymen > 0:
                    for x in range(0, args.handymen):
                        modded_json["vault"]["LunchBoxesByType"].append(int(Item.HANDYMAN))
                    print("Added {} handymen".format(args.handymen))
                #animal carriers
                if args.carriers and args.carriers > 0:
                    for x in range(0, args.carriers):
                        modded_json["vault"]["LunchBoxesByType"].append(int(Item.CARRIER))
                    print("Added {} animal carriers".format(args.carriers))
                #caps
                if args.caps and args.caps > 0:
                    modded_json["vault"]["storage"]["resources"]["Nuka"] = args.caps
                    print("Set vault caps to {}".format(args.caps))
                #nuka quantum
                if args.quantum and args.quantum > 0:
                    modded_json["vault"]["storage"]["resources"]["NukaColaQuantum"] = args.quantum
                    print("Set vault quantum to {}".format(args.quantum))
                #food
                if args.food and args.food > 0:
                    modded_json["vault"]["storage"]["resources"]["Food"] = args.food
                    print("Set vault food to {}".format(args.food))
                #energy
                if args.energy and args.energy > 0:
                    modded_json["vault"]["storage"]["resources"]["Energy"] = args.energy
                    print("Set vault energy to {}".format(args.energy))
                #water
                if args.water and args.water > 0:
                    modded_json["vault"]["storage"]["resources"]["Water"] = args.water
                    print("Set vault water to {}".format(args.water))
                #stimpacks
                if args.stim_packs and args.stim_packs > 0:
                    modded_json["vault"]["storage"]["resources"]["StimPack"] = args.stim_packs
                    print("Set vault stimpacks to {}".format(args.stim_packs))
                #rad away's
                if args.rad_aways and args.rad_aways > 0:
                    modded_json["vault"]["storage"]["resources"]["RadAway"] = args.rad_aways
                    print("Set vault rad away's to {}".format(args.rad_aways))
                #remove rocks
                if args.remove_rocks:
                    rock_count = len(modded_json["vault"]["rocks"])
                    if rock_count > 0:
                        modded_json["vault"]["rocks"] = []
                        print("Removed {} rock(s) from the vault".format(rock_count))
                    else:
                        print("No need to remove rocks, they're already gone")
                #max dweller level, happiness, armor, weapon, and stats
                if args.max_dwellers:
                    dweller_count = len(modded_json["dwellers"]["dwellers"])
                    for x in range(0, dweller_count):
                        #current max level
                        modded_json["dwellers"]["dwellers"][x]["experience"]["currentLevel"] = 50
                        #max happiness
                        modded_json["dwellers"]["dwellers"][x]["happiness"]["happinessValue"] = 100.0
                        #best armor
                        modded_json["dwellers"]["dwellers"][x]["equipedOutfit"] = {
                            "id": "PowerArmor_MkVI",
                            "type": "Outfit",
                            "hasBeenAssigned": False,
                            "hasRandonWeaponBeenAssigned": False
                        }
                        #best weapon
                        modded_json["dwellers"]["dwellers"][x]["equipedWeapon"] = {
                            "id": "GatlingLaser_Vengeance",
                            "type": "Weapon",
                            "hasBeenAssigned": False,
                            "hasRandonWeaponBeenAssigned": False
                        }
                        #best pet
                        modded_json["dwellers"]["dwellers"][x]["equippedPet"] = {
                            "id": "germanshepherd_l",
                            "type": "Pet",
                            "hasBeenAssigned": False,
                            "hasRandonWeaponBeenAssigned": False,
                            "extraData": {
                                "uniqueName": "Dogmeat",
                                "bonus": "HappinessBoost",  #should be ObjectiveMultiplier @ 3.0
                                "bonusValue": 100.0
                            }
                        }
                        #max stats
                        for y in range(0, 8):
                            modded_json["dwellers"]["dwellers"][x]["stats"]["stats"][y]["value"] = 10
                            modded_json["dwellers"]["dwellers"][x]["stats"]["stats"][y]["mod"] = 10
                            modded_json["dwellers"]["dwellers"][x]["stats"]["stats"][y]["exp"] = 600000
                    print("Maxed {} dweller(s)".format(dweller_count))
                #remove all lunchboxes
                if args.remove_lunchboxes:
                    lunchbox_count = modded_json["vault"]["LunchBoxesByType"].count(int(Item.LUNCHBOX))
                    if lunchbox_count > 0:
                        modded_json["vault"]["LunchBoxesByType"] = list(filter((int(Item.LUNCHBOX)).__ne__, modded_json["vault"]["LunchBoxesByType"]))
                        print("Removed {} lunchbox(es)".format(lunchbox_count))
                    else:
                        print("No lunchboxes removed, there weren't any")
                #remove all mr. handymen
                if args.remove_handymen:
                    handyman_count = modded_json["vault"]["LunchBoxesByType"].count(int(Item.HANDYMAN))
                    if handyman_count > 0:
                        modded_json["vault"]["LunchBoxesByType"] = list(filter((int(Item.HANDYMAN)).__ne__, modded_json["vault"]["LunchBoxesByType"]))
                        print("Removed {} Mr. Handyman".format(handyman_count))
                    else:
                        print("No Mr. Handymen removed, there weren't any")
                #remove all pet carriers
                if args.remove_carriers:
                    carrier_count = modded_json["vault"]["LunchBoxesByType"].count(int(Item.CARRIER))
                    if carrier_count > 0:
                        modded_json["vault"]["LunchBoxesByType"] = list(filter((int(Item.CARRIER)).__ne__, modded_json["vault"]["LunchBoxesByType"]))
                        print("Removed {} pet carrier(s)".format(carrier_count))
                    else:
                        print("No pet carriers removed, there weren't any")
                #remove starting elevator from row 1 and 2, column 9
                if args.remove_elevator:
                    vault_rooms = modded_json["vault"]["rooms"]
                    for x in range(0, len(vault_rooms)):
                        room = vault_rooms[x]
                        if "row" in room and "col" in room and "type" in room:
                            if ((room["row"] == 0 and room["col"] == 9) or (room["row"] == 1 and room["col"] == 9)) and room["type"] == "Elevator":
                                del modded_json["vault"]["rooms"][x]
                    print("Removed starting elevator(s)")
                #vault name
                if args.vault_name:
                    modded_json["vault"]["VaultName"] = args.vault_name
                    print("Set vault name to {}".format(args.vault_name))

                #write the output
                if args.out_file:
                    modded_json = utils.minify_json(modded_json)
                    open(args.out_file, "w").write(encrypt_save_data(modded_json))
                    print("Save successfully modified!")
                else:
                    print("No output file specified so save wasn't modified.")
            else:
                print("The specified input file doesn't exist")
        elif args.in_json:  #encrypt a json file (good for experimentation)
            if isfile(args.in_json):
                open(args.in_json.replace(".json", ".sav").replace("_dumped", "_modded"), "w").write(encrypt_save_data(open(args.in_json, "r").read()))
        elif args.list:  #list saves
            steam_save_dir = join(getenv("APPDATA").replace("Roaming", "Local"), "FalloutShelter")
            if isdir(steam_save_dir):
                save_files = [x for x in listdir(steam_save_dir) if x.endswith(".sav")]
                print("There are {} Steam/Windows Store save files:".format(len(save_files)))
                for single in save_files:
                    if single.endswith(".sav"):
                        print(join(steam_save_dir, single))
        else:
            parser.print_help()
    except:
        print_exc()
        print("An error has occurred!")