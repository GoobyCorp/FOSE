### FOSE - Fallout Shelter Editor

This is an editor for Fallout Shelter on PC (Steam, Bethesda, and Windows
Store), Android, and iOS.

#### This script verifies the encryption/decryption key/IV, I will not be sharing it!

Usage is as follows:
```
usage: FOSE.py [-h] -i IN_FILE -o OUT_FILE [-l] [-j IN_JSON] [-d] [-nb]
               [--lunchboxes LUNCHBOXES] [--handymen HANDYMEN]
               [--carriers CARRIERS] [--caps CAPS] [--quantum QUANTUM]
               [--food FOOD] [--energy ENERGY] [--water WATER]
               [--stim-packs STIM_PACKS] [--rad-aways RAD_AWAYS]
               [--max-dwellers] [--remove-rocks] [--remove-lunchboxes]
               [--remove-handymen] [--remove-carriers] [--remove-elevator]
               [--vault-name VAULT_NAME] --save-key SAVE_KEY --save-iv SAVE_IV

A script to edit Fallout Shelter saves on PC (Steam, Bethesda, and Windows
Store), Android, and iOS

optional arguments:
  -h, --help            show this help message and exit
  -i IN_FILE, --in-file IN_FILE
                        The .sav file you want to read from
  -o OUT_FILE, --out-file OUT_FILE
                        The .sav file you want to write to
  -l, --list            List available save games (Steam & Bethesda launchers
                        only)
  -j IN_JSON, --in-json IN_JSON
                        A .json file that you want to encrypt
  -d, --dump            Dump to a .json file
  -nb, --no-backup      Don't backup the save
  --lunchboxes LUNCHBOXES
                        The amount of lunchboxes you want to add to your save
  --handymen HANDYMEN   The amount of Mr. Handymen you want to add to your
                        save
  --carriers CARRIERS   The amount of pet carriers you want to add to your
                        save
  --caps CAPS           The amount of caps you want
  --quantum QUANTUM     The amount of nuka-quantum you want
  --food FOOD           The amount of food you want
  --energy ENERGY       The amount of energy you want
  --water WATER         The amount of water you want
  --stim-packs STIM_PACKS
                        The amount of stimpacks you want
  --rad-aways RAD_AWAYS
                        The amount of rad away's you want
  --max-dwellers        Max all dweller stats
  --remove-rocks        Remove all rocks
  --remove-lunchboxes   Removes all lunchboxes
  --remove-handymen     Removes all Mr. Handymen
  --remove-carriers     Remove all pet carriers
  --remove-elevator     Remove the elevator that it starts you with
  --vault-name VAULT_NAME
                        The name you want to change your vault to

required arguments:
  --save-key SAVE_KEY   The key used to encrypt/decrypt saves as hex
  --save-iv SAVE_IV     The IV used to encrypt/decrypt saves as hex
```