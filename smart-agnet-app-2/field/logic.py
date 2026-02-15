from typing import List, Dict
from orb import Orb
from hole import Hole
from movement import Coordinates
from entity import Entity
from random import randint
from agent import Direction, Agent
from enum import Enum

class FieldType(Enum):
    CONSOLE = 1
    GUI = 2

class FieldLogic:
    def __init__(self, width: int = 7, height: int = 7) -> None:
        if width < 2 or height < 2:
            raise ValueError("Field dimention cant be that small.")
        self.height: int = height
        self.width: int = width
        self.orbs: List[Orb] = []
        self.holes: List[Hole] = []
        self.cells: List[List[List[Entity]]] = []
        self.init_cells()
        self.final_stats: str | None = None

    def init_cells(self):
        self.cells = [[None for _ in range(self.width)] for _ in range(self.height)]

        for i in range(self.width):
            for j in range(self.height):
                self.cells[i][j] = []


    def update_cells(self):
        self.init_cells()
        for h in self.holes:
            self.place_in_cell(h)
        for o in self.orbs:
            self.place_in_cell(o)

    def place_in_cell(self, entity: Entity|None):
        if not entity:
            return
        cell = self.get_cell(entity.position)
        if entity not in cell:
            cell.append(entity)

    def get_cell(self, coord: Coordinates):
        x, y = coord.convert_to_indices()
        return self.cells[y][x]

    def add_random_holes(self, number_of_holes: int):
        if number_of_holes <= 0:
            raise ValueError('Number of holes must be a positive number.')
        last_id = Hole.GetNextId(self.holes)
        for _ in range(1, number_of_holes + 1):
            hole = Hole(id=last_id)
            self.holes.append(hole)
            self.place_in_cell(hole)
            last_id += 1

    def add_hole(self, position: Coordinates):
        hole = Hole(id=Hole.GetNextId(self.holes), position=position)
        self.holes.append(hole)
        self.place_in_cell(hole)

    def add_random_orbs(self, number_of_orbs: int):
        if number_of_orbs <= 0:
            raise ValueError('Number of orbs must be a positive number.')
        last_id = Orb.GetNextId(self.orbs)
        for _ in range(1, number_of_orbs + 1):
            orb = Orb(id=last_id)
            self.orbs.append(orb)
            self.place_in_cell(orb)
            last_id += 1

    def add_orb(self, position: Coordinates):
        self.orbs.append(Orb(id=Orb.GetNextId(self.orbs), position=position))

    def get_remaining_orbs(self):
        out_orbs = list(filter(lambda o: not o.hole, self.orbs))
        return len(out_orbs)

    def update_ui(self, agent: Agent):
        pass

    def is_cell_available(self, position: Coordinates):
        '''check if the cell can contain a new orb or not'''
        x, y = position.convert_to_indices()
        cell = self.cells[y][x]
        for item in cell:
            if isinstance(item, Orb):
                return False
            elif isinstance(item, Hole) and not item.has_room():
                return False
        return True

    def shake(self, agents: List[Agent]):
        orbs: List[Orb] = []
        for row in self.cells:
            for cell in row:
                if cell:
                    for item in cell:
                        if isinstance(item, Orb) and item.hole is None:
                            orbs.append(item)

        for orb in orbs:
            rnd = randint(0, 100)
            if rnd < 10:
                # 10% of moving the orb
                for _ in range(4): # try 4 times to shake the orb
                    # because the taget cell may be full. if after 4 times it didnt success go to next orb
                    rnd_direction = Direction.Random()
                    new_position = Coordinates(orb.position.x, orb.position.y)

                    match rnd_direction:
                        case Direction.RIGHT:
                            if new_position.x < self.width:
                                new_position.x += 1
                            else:
                                new_position.x -= 1
                        case Direction.LEFT:
                            if new_position.x > 1:
                                new_position.x -= 1
                            else:
                                new_position.x += 1
                        case Direction.UP:
                            if new_position.y > 1:
                                new_position.y -= 1
                            else:
                                new_position.y += 1
                        case Direction.DOWN:
                            if new_position.y < self.height:
                                new_position.y += 1
                            else:
                                new_position.y -= 1

                    if self.is_cell_available(new_position):
                        orb.position = new_position
                        for agent in agents:
                            agent.forget(orb)
                        # TODO: check what happens if orb falls into a hole
                        break

    def throw_orb(self, from_cell: List[Entity], orb: Orb, thrower: Agent):
        from_cell.remove(orb)
        if orb.hole:
            if orb in orb.hole.orbs:  # just for caution, this is always true
                orb.hole.orbs.remove(orb)

        orb.hole = None
        orb.drop_by = None
        orb.position.Randomize()
        while not self.is_cell_available(orb.position):
            orb.position.Randomize()
        # check if the orb is not thrown into a hole
        self.place_in_cell(orb)
        cell = self.get_cell(orb.position)
        for item in cell:
            if isinstance(item, Hole):
                orb.hole = item
                orb.drop_by = thrower.id
                item.orbs.append(orb)

    @property
    def statistics(self):
        filled_holes = len(list(filter(lambda h: not h.has_room(), self.holes)))
        empty_holes =  len(self.holes) - filled_holes  # for npow the capacity of holes is 1, so this formula works
        orbs_inside = 0
        dropped_by_each: Dict[int, int] = {}

        for orb in self.orbs:
            if orb.hole:
                orbs_inside += 1
                if orb.drop_by not in dropped_by_each:
                    dropped_by_each[orb.drop_by] = 0
                dropped_by_each[orb.drop_by] += 1

        orbs_outside = len(self.orbs) - orbs_inside
        return {
            'Filled Holes': filled_holes,
            'Empty Holes': empty_holes,
            'Orbs Inside': orbs_inside,
            'Orbs Outside': orbs_outside,
            'Dropped By Each': dropped_by_each
        }

    def set_final_stats(self, agents: List[Agent]):
        stats = self.statistics
        dropped_by_each = stats['Dropped By Each']
        for agent in agents:
            if agent.id in dropped_by_each:
                stats[f'Dropped By {agent.name}'] = dropped_by_each[agent.id]
            stats[f'Number of Throws By {agent.name}'] = agent.throws_count
            stats[f'Number of {agent.name} Moves'] = agent.moves
        del stats['Dropped By Each']

        self.final_stats = ''
        for tag in stats:
            self.final_stats += f'{tag}: {stats[tag]}\n'
        return self.final_stats
