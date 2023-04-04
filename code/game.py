class Game:
    def __init__(self, current_map, map_list, surface):

        # general setup
        self.world_shift_x = 0
        self.world_shift_y = 0
        self.display_surface = surface
        self.current_map = current_map
        self.map_list = map_list

    def run(self):
        self.map_list[self.current_map].run()
