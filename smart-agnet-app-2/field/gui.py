import tkinter as tk
from PIL import ImageTk, Image
from field.logic import FieldLogic
from agent import Agent
from typing import List
from entity import Entity
from field.logic import FieldType
from tkinter import messagebox

class FieldGUI(tk.Tk):
    def __init__(self, width: int = 5, height: int = 5):
        super().__init__()
        self.height: int = height
        self.width: int = width
        self.title("Smart Agent Game")
        self.cell_size: int = 125
        self.canvas: tk.Canvas = tk.Canvas(self, width=self.cell_size*self.width, height=self.cell_size*self.height)
        self.canvas.pack()
        self.cells: List[List[int]] = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.images: List[List[List[int]]] = [[[] for _ in range(self.width)] for _ in range(self.height)]
        self.create_field()

    def create_field(self):
        for i in range(self.height):
            for j in range(self.width):
                x0, y0 = i * self.cell_size, j * self.cell_size
                x1, y1 = x0 + self.cell_size, y0 + self.cell_size
                self.cells[i][j] = self.canvas.create_rectangle(x0, y0, x1, y1, fill="white", outline="black")
                self.canvas.tag_bind(self.cells[i][j], "<Button-1>")

    def load_entity(self, entity: Entity):
        avatar = entity.avatar
        x, y = entity.position.convert_to_indices()
        image = Image.open(avatar.path)
        image = image.resize((avatar.size, avatar.size), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        distance_between_images = self.cell_size / 3
        offset_x = len(self.images[x][y]) % 2 * distance_between_images
        offset_y = len(self.images[x][y]) // 2 * distance_between_images
        offset_delta = self.cell_size / 3
        canvas_id = self.canvas.create_image(x*self.cell_size + offset_delta + offset_x, y*self.cell_size + offset_delta + offset_y, image=photo)
        self.images[x][y].append({'id': canvas_id, 'photo': photo})

        return canvas_id

    def update_ui(self, cells_data: List[List[List[Entity]]],  agents: List[Agent]):
        '''Show the graphical user interface for illustration of the simulation; TODO: agent field is temprory'''
        for row in cells_data:
            for cell in row:
                if not cell:
                    continue
                for entity in cell:
                    if not entity:
                        continue
                    entity.avatar.canvas_id = self.load_entity(entity)
        for agent in agents:
            agent.avatar.canvas_id = self.load_entity(agent)


class Field(FieldLogic):

    def __init__(self, width: int = 5, height: int = 5) -> None:
        super().__init__(width, height)
        self.gui = FieldGUI(self.width, self.height)
        self.game_ended = False

    def clear_field(self):
        for row in self.gui.images:
            for col in row:
                for item in col:
                    self.gui.canvas.delete(item['id'])
                col.clear()

    def update_ui(self, agents: List[Agent]):
        self.clear_field()
        self.gui.update_ui(self.cells, agents)

    def go_for_next_move(self, game):
        if self.game_ended:
            return
        self.update_ui(game.agents)
        self.game_ended = game.do_next_move()
        if self.game_ended:
            messagebox.showinfo("Game Over", "All orbs are placed in holes." if game.agents_has_won() else "Agents are out of moves.")
            messagebox.showinfo("Game Statistics", self.final_stats)

    def run(self, game):
        self.check_for_events(game)
        self.gui.mainloop()
        return self

    def check_for_events(self, game):
        self.gui.update()  # Process events
        self.go_for_next_move(game)
        self.gui.after(1000, self.check_for_events, game)  # Check again after 100ms

    def type(self) -> FieldType:
        return FieldType.GUI

if __name__ == "__main__":
    size = 5  # Change the size of the board here
    app = FieldGUI()
    app.run().show()
