from light_bulb import LightBulb

import argparse
import sys
import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from light_bulb import LightBulb
from lightbulb_cli.executor import execute
from spacy_parser import SpacyParser
from lightbulb_cli.state import LightBulbState

EXIT_WORDS = {"quit", "exit", "q"}

def cli():
    bulb = LightBulb()
    parser = SpacyParser()
    while True:
        text = input("User: ")
        print(text)
        strippedtext = text.strip()
        if not strippedtext:
            continue
        if strippedtext.lower() in EXIT_WORDS:
            break

        state = LightBulbState(is_on=bulb.is_on, brightness=bulb.brightness)
        command = parser.parse(strippedtext, state)
        execute(bulb, command)
    
    return 0



def main():
    cli()

if __name__ == "__main__":
    main()