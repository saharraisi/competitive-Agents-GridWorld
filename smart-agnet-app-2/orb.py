from movement import Coordinates
from entity import Entity, EntityType
from hole import Hole
from resources.avatar import Avatar


class Orb(Entity):
    @staticmethod
    def DefaultAvatar() -> Avatar:
        return Avatar('resources/orb.png', 50)

    def __init__(self, id: int, position: Coordinates | None = None, avatar: Avatar = None) -> None:
        '''Orbs: orbs are sphere entities which would fill the holes inside the field.
            Params note: Not specifying coordinates will make it randomise its position, not specifying image will make the app use default image.'''
        avatar = avatar if avatar else Orb.DefaultAvatar()
        super().__init__(name="Orb", id=id, avatar=avatar, entityType=EntityType.ORB, position=position)
        self.targeted: int = 0

        self.hole: Hole|None = None  # The hole which this orb is dropped to. If orb.hole is None it means this orb is still outside in the field
        self.drop_by: int|None = None

    @property
    def is_available(self) -> bool:
        '''All the conditions that must be met for a orb, so it can be picked by an agent'''
        return not self.hole #and not self.targeted
