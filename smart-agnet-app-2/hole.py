from movement import Coordinates
from entity import Entity, EntityType
from typing import List
from resources.avatar import Avatar


class Hole(Entity):
    CAPACITY = 1  # how many orbs can be contained by a single hole
    def DefaultAvatar() -> Avatar:
        return Avatar('resources/hole.png', 100)

    def __init__(self, id: int, position: Coordinates | None = None, avatar: Avatar = None) -> None:
        '''Holes; Holes are empty places inside field which can be filled with orbs.
            Param Notes: Not specifying coordinates will make it randomise its position, not specifying image will make the app use default image.'''
        avatar = avatar if avatar else Hole.DefaultAvatar()
        super().__init__(name="Hole", id=id, avatar=avatar, entityType=EntityType.HOLE, position=position)
        self.targeted: int = 0
        self.orbs: List[Entity] = []  # Demonestrates the orbs that are fropped inside this hole. If the list is empty it means its ready to contain upcomming orbs

    def has_room(self) -> bool:
        return len(self.orbs) < self.CAPACITY

    @property
    def is_available(self) -> bool:
        '''All the conditions that must be met for a hole, so an agent could select to move towards it for dropping an orb'''
        return self.has_room() #and not self.targeted
