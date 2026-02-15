
class Avatar:
    '''Avatar used for showing entities in GUI version of the app'''
    def __init__(self, image_path: str, size: int) -> None:
        self.path: str = image_path
        self.size: int = size
        self.canvas_id: int = None