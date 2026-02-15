from movement import Coordinates, Direction
from entity import Entity, EntityType
from typing import Union, List, Dict
from hole import Hole
from orb import Orb
from resources.avatar import Avatar



class Candidate:
    def __init__(self, orb: Orb, hole: Hole) -> None:
        self.orb = orb
        self.hole = hole

    @property
    def distance(self):
        return self.orb - self.hole

    def drop(self, dropper_id: int):
        if not self.hole.has_room():
            raise Exception('Hole is full')
        self.orb.hole = self.hole
        self.hole.orbs.append(self.orb)
        self.orb.drop_by = dropper_id

    def __str__(self) -> str:
        return f"Candidate: Orb@{self.orb.position} -> Hole@{self.hole.position if self.hole else 'Nowhere'}"

    def fulfilled(self):
        return self.orb and self.hole and self.orb.position == self.hole.position

class Agent(Entity):
    NumberOfAgents = 0
    NO_MOVE_REP_MAX = 4

    @staticmethod
    def DefaultAvatar(id: int) -> Dict[Direction, Avatar]:
        return {
            Direction.UP: Avatar(f'resources/agent{id}/up.png', 60),
            Direction.DOWN: Avatar(f'resources/agent{id}/down.png', 60),
            Direction.RIGHT: Avatar(f'resources/agent{id}/right.png', 60),
            Direction.LEFT: Avatar(f'resources/agent{id}/left.png', 60),
        }

    def __init__(self, position: Coordinates | None = None, avatars: Dict[Direction, Avatar] = None, name: str | None = None) -> None:
        Agent.NumberOfAgents += 1
        super().__init__(id=Agent.NumberOfAgents, name="Smart Agent", avatar=avatars, entityType=EntityType.AGENT, position=position)
        self.direction: Direction = Direction.Random()
        self.moves = 0
        self.actions = 0
        self.__avatars = avatars if avatars else Agent.DefaultAvatar(self.id)
        self.reach_to_candidate: Candidate = None
        self.candidate: Candidate = None
        self.no_point_moving_orb = None  # for when there's no candidate, this could be useful by moving orb, so it isnt required to move back to it just for moving it again.
        self.one_directional_moves = 0
        self.discoveries: List[Orb|Hole] = []
        self.no_move_rep = 0
        self.hang_on = 0
        self.name: str = name if not None else f'Agent {self.id}'
        self.throws_count = 0

    @property
    def avatar(self):
        '''return the avatar of the agent base of the direction'''
        return self.__avatars[self.direction]

    def __str__(self) -> str:
        return f"A{self.id}{self.direction}" if self.direction != Direction.LEFT else f"{self.direction}A{self.id}"

    def extract_cooordinates(self) -> Union[int, int]:
        return self.position.x, self.position.y

    def look_around(self, field):
        '''Look around in 8 directions and find som holes and orbs'''
        x, y = self.extract_cooordinates()
        steps = [-1, 0, 1]
        new_founds = 0
        for i in steps:
            for j in steps:
                if x + i >= 1 and y + j >= 1 and x + i <= field.width and y + j <= field.height:
                    cell = Coordinates(x + i, y + j)
                    entities = field.get_cell(cell)
                    for entity in entities:
                        if entity is not None and entity not in self.discoveries:
                            if (isinstance(entity, Hole) and entity.has_room()) or (isinstance(entity, Orb) and not entity.hole):
                                # identified
                                self.discoveries.append(entity)
                                new_founds += 1

        return new_founds

    def find_next_best_displacement(self):
        orbs: List[Orb] = list(filter(lambda item: isinstance(item, Orb) and item.is_available, self.discoveries))
        holes: List[Hole] = list(filter(lambda item: isinstance(item, Hole) and item.is_available, self.discoveries))

        if not holes or not orbs:
            return None

        candidate: Candidate = Candidate(orbs[0], holes[0])
        for orb in orbs:
            for hole in holes:
                if (hole.has_room()) and (not orb.hole) and (candidate.distance > orb - hole or candidate.hole is None):
                    candidate = Candidate(orb, hole)
                    orb.targeted = hole.targeted = self.id
        return candidate

    def check_for_less_distant_hole(self):
        if not self.candidate:
            return
        holes: List[Hole] = list(filter(lambda item: isinstance(item, Hole) and item != self.candidate.hole and item.is_available, self.discoveries))

        if not holes:
            return

        for hole in holes:
            if (hole.has_room()) and (self.candidate.distance > self.candidate.orb - hole):
                self.candidate.hole.targeted = None
                self.candidate.hole = hole
                hole.targeted = self.id

    def direct_into(self, target: Candidate):
        if not target or not target.orb or not target.hole:
            return
        self.check_for_less_distant_hole()

        if target.hole:
            if target.orb.position.x < target.hole.position.x:
                self.direction = Direction.RIGHT
            elif target.orb.position.x > target.hole.position.x:
                self.direction = Direction.LEFT
            elif target.orb.position.y < target.hole.position.y:
                self.direction = Direction.DOWN
            elif target.orb.position.y > target.hole.position.y:
                self.direction = Direction.UP
            else:
                return True

        return False

    def check_one_directional_moves(self, previous_direction: Direction, x_max: int, y_max: int) -> bool:
        '''This is for getting the agen out of one directional move loop; if its taking so long moving in one didrection, this method chanes it for the better'''
        if not self.candidate and previous_direction == self.direction:
            self.one_directional_moves += 1
            # this means random movement has been taking to long in the same direciotn
            if self.direction.is_horizontal() and self.one_directional_moves >= int(x_max / 2):
                if self.position.y <= 0.3 * y_max:
                    self.direction = Direction.DOWN
                elif self.position.y >= 0.8 * y_max:
                    self.direction = Direction.UP
                elif self.one_directional_moves >= 2 + int(x_max / 2):
                    # if the agent is in the middle of the field, it needs a larger threshold
                    self.direction = Direction.Random(axis='v')
            elif self.direction.is_vertical() and self.one_directional_moves >= int(y_max / 2):
                if self.position.x <= 0.3 * x_max:
                    self.direction = Direction.RIGHT
                elif self.position.x >= 0.8 * x_max:
                    self.direction = Direction.LEFT
                elif self.one_directional_moves >= 2 + int(y_max / 2):
                    # if the agent is in the middle of the field, it needs a larger threshold
                    self.direction = Direction.Random(axis='h')
            return True

        self.one_directional_moves = 0
        return False

    def move(self, field, candidate: Candidate|None, agents: List[Entity]) -> None|int:
        prev_pos = Coordinates(self.position.x, self.position.y)
        prev_dir = self.direction
        self.check_one_directional_moves(prev_dir, field.width, field.height)
        self.check_agent_position(field)
        match self.direction:
            case Direction.RIGHT:
                self.position.x += 1
            case Direction.LEFT:
                self.position.x -= 1
            case Direction.UP:
                self.position.y -= 1
            case Direction.DOWN:
                self.position.y += 1
        if candidate:
            candidate.orb.position.x = self.position.x
            candidate.orb.position.y = self.position.y
            field.update_cells()

        other = agents[0] if agents[0] != self else agents[-1]

        if other.position == self.position:
            self.return_to_position(prev_pos)
            return -1
        self.moves += 1
        return None

    def move_forward_to(self, target: Entity, agents: List[Entity]):
        prev_pos = Coordinates(self.position.x, self.position.y)
        other = agents[0] if agents[0] != self else agents[-1]

        if self.position.x < target.position.x:
            self.direction = Direction.RIGHT
            self.position.x += 1
            if other.position == self.position:
                self.return_to_position(prev_pos)
                return -1
            else:
                self.moves += 1
            return int(self.position == target.position)

        if self.position.x > target.position.x:
            self.direction = Direction.LEFT
            self.position.x -= 1
            if other.position == self.position:
                self.return_to_position(prev_pos)
                return -1
            else:
                self.moves += 1
            return int(self.position == target.position)

        if self.position.y < target.position.y:
            self.direction = Direction.DOWN
            self.position.y += 1
            if other.position == self.position:
                self.return_to_position(prev_pos)
                return -1
            else:
                self.moves += 1
            return int(self.position == target.position)

        if self.position.y > target.position.y:
            self.direction = Direction.UP
            self.position.y -= 1
            if other.position == self.position:
                self.return_to_position(prev_pos)
                return -1
            else:
                self.moves += 1
            return int(self.position == target.position)
        return -1

    def return_to_position(self, position: Coordinates):
        self.position = Coordinates(position.x, position.y)
        if self.candidate:
            self.candidate.orb.position = Coordinates(position.x, position.y)  # preventing position of reference copy

    def check_agent_position(self, field):
        '''Prevent egant from going out of the field'''
        while not self.direction \
            or (self.direction == Direction.RIGHT and self.position.x == field.width) \
            or (self.direction == Direction.LEFT and self.position.x == 1) \
            or (self.direction == Direction.UP and self.position.y == 1) \
            or (self.direction == Direction.DOWN and self.position.y == field.height):
                self.direction = Direction.Random()

    def force_move(self, field: any, all_agents: List[Entity]):
        '''This is for when both agents are stock next to each other and cant move'''
        self.direction = Direction.Random()
        while self.move(field, self.candidate, all_agents) == -1:
            self.direction = Direction.Random()

    def forget(self, entity: Orb|Hole, just_entity_itself: bool = False):
        if entity in self.discoveries:
            self.discoveries.remove(entity)
            if just_entity_itself:
                return
            if isinstance(entity, Orb):
                if entity.hole is not None and not entity.hole.has_room():
                    self.forget(entity.hole)
            elif isinstance(entity, Hole) and entity.orbs:
                for orb in entity.orbs:
                    if orb in self.discoveries:
                        self.discoveries.remove(orb)

    def try_to_sabotage(self, field) -> Orb | None:
        cell: List[Entity] = field.get_cell(self.position)
        try:  # skip this function if the cell is not array of entities
            if not len(cell):
                return
        except:
            return

        for entity in cell:
            if isinstance(entity, Orb) and entity.hole is not None and entity.drop_by != self.id:
                # throw the orb to nowhere
                field.throw_orb(cell, entity, self)
                self.throws_count += 1
                return entity
        return None
