from field.logic import FieldLogic
from movement import Coordinates
import math
from hole import Hole
from orb import Orb
from agent import Agent
from field.logic import FieldType
from typing import List


class Field(FieldLogic):
    '''Field illustration in a console app.'''
    def run(self, game):
        print("Welcome! Press enter to start...")
        input()
        return self

    def type(self) -> FieldType:
        return FieldType.CONSOLE

    def update_ui(self, agents: List[Agent]):
        print()
        cell_width, cell_height = 4, 3
        for h in range(self.height):
            for ch in range(cell_height):
                for w in range(self.width):
                    if not w:
                        print('|', end='')
                        if not ch:
                            for _ in range(self.width):
                                print(('- ' * cell_width) + '|', end='')
                            print()
                            print('|', end='')
                    coords = Coordinates(w + 1, h + 1)
                    entities = self.get_cell(coords)
                    entity = entities[0] if entities else None
                    if not entity or math.floor(cell_height / 2) != ch:
                        if math.floor(cell_height / 2) != ch:
                            print(f"{' ':{cell_width*2}}" + '|', end='')
                        else:
                            en = ''
                            for agent in agents:
                                if agent.position == coords:
                                    en += agent.__str__()
                            print(f"{en:{cell_width*2}}" + '|', end='')

                    else:
                        en = ''
                        for agent in agents:
                            if agent.position == coords:
                                en += agent.__str__()
                        if (isinstance(entity, Hole) and entity.orbs):
                            x = entity.orbs[0]
                            en += f" {x.shortname}{entity.shortname}"
                        elif (isinstance(entity, Orb) and entity.hole):
                            x = entity.hole
                            en += f" {x.shortname}{entity.shortname}"
                        else:
                            en += f"   {entity.shortname}"
                        print(f"{en:{cell_width*2}}" + '|', end='')

                print()
        print('|', end='')
        for _ in range(self.width):
            print((' -' * cell_width) +  '|', end='')
        print()
