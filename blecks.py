import random
import sys
import time as tm
import numpy as np


def Reverse(lst): 
    return [ele for ele in reversed(lst)]

def distance_between(a_xy, b_xy):
    distance = abs(a_xy[0] - b_xy[0]) + abs(a_xy[1] - b_xy[1]) - 1
    return distance

class Game:
    def __init__(self):
        self.npc_locations = {}
        self.existing_items = []
        self.messages = []
        self.existing_doodads = []
        self.map_array = np.zeros((50, 50))
        self.day = 0
        self.time = 0
        self.g = MapGrid(15, 10)
        self.walls = []

    def npc_interactions(self, target):
        if target.is_stunned == True:
                    self.messages.append(target.name + ': "zzZ"')
                    self.npc_turn()
        elif target.name == 'the guard':
            self.messages.append(f"{target.name}: keep movin")
            self.npc_turn()
        elif target.name == 'tamel':
            if self.blecks not in target.enemies and target.is_stunned == False:
                self.messages.append(target.name + ': "welcome to town, blecks"')
                target.emoji = '😀'
                self.npc_turn()
            
            else:
                if target.subtype == 'civilian' and target.is_stunned == False:
                    if target.is_aggressive:
                        self.messages.append(target.name + ': I\'ll frick you right up!')
                        target.emoji = '🤬'
                    else:
                        self.messages.append(target.name + ': "get the heck right away from me!"')
                        target.emoji = '😰'
                elif target.is_stunned == True:
                    self.messages.append(target.name + ': "zzZ"')

                self.npc_turn()
        else:
            if target.subtype == 'civilian':
                self.messages.append(target.name + ': "excuse me"')
                target.emoji = '🤨'
            self.npc_turn()

    def doodad_line(self, origin_xy, dir_length, axis, is_obstructive, emoji, name):
        if axis == 'x':
            i = origin_xy[0]
            if dir_length > 0:
                while i < dir_length + origin_xy[0]:
                    name = Doodad(i, origin_xy[1], emoji, name, is_obstructive, game)
                    i += 1
            elif dir_length < 0:
                while i > dir_length + origin_xy[0]:
                    self.walls.append((i, origin_xy[1]))
                    i -= 1
        elif axis == 'y':
            i = origin_xy[1]
            if dir_length > 0:
                while i < dir_length + origin_xy[1]:
                    self.walls.append((origin_xy[0], i))
                    i += 1
            elif dir_length < 0:
                while i > dir_length + origin_xy[1]:
                    self.walls.append((origin_xy[0], i))
                    i -= 1

    def build_wall(self, origin_xy, dir_length, axis):
        if axis == 'x':
            i = origin_xy[0]
            if dir_length > 0:
                while i < dir_length + origin_xy[0]:
                    self.walls.append((i, origin_xy[1]))
                    i += 1
            elif dir_length < 0:
                while i > dir_length + origin_xy[0]:
                    self.walls.append((i, origin_xy[1]))
                    i -= 1
        elif axis == 'y':
            i = origin_xy[1]
            if dir_length > 0:
                while i < dir_length + origin_xy[1]:
                    self.walls.append((origin_xy[0], i))
                    i += 1
            elif dir_length < 0:
                while i > dir_length + origin_xy[1]:
                    self.walls.append((origin_xy[0], i))
                    i -= 1

    def place_objects(self):
        paper = Item(-1, -1, 'paper', self)
        self.watch = Item(-1, -1, 'watch', self, 0, '⌚️')
        pen = Item(-1, -1, 'pen', self, 1, '🖋')
        notepad = Item(-1, -1, 'notepad', self, 0, '🗒')
        knife = Item(-1, -1, 'knife', self, 3, '🔪')
        taser = Item(-1, -1, 'taser', self, 1, '🔫')
        taser2 = Item(-1, -1, 'taser', self, 1, '🔫')
        key1 = Item(-1, -1, 'key', self, 1, '🗝')
        amphora = Item(3, 1, 'amphora', self, 0, '🏺', inventory=[pen, notepad, knife])

        self.blecks = Person('blecks', self,
            subtype='player', x=1, y=1, hp=10,
            speed=20, emoji="🙎",
            inventory=[self.watch, key1], vision=4)
        tamel = Person('tamel', self, subtype='civilian', x=2, y=5, hp=10, speed=15)
        jimben = Person('jimben', self, subtype='civilian', x=7, y=7, hp=10, speed=25, is_aggressive=True, inventory=[knife])

        guard1 = Person('the guard', self, subtype='guard', x=1, y=8, hp=10, speed=25, is_aggressive=True, inventory=[taser, knife], emoji='💂🏼‍♀️', vision = 8)

        ##blecks house 
        bed = Item(1, 1, 'bed', self, 0, '🛏')
        self.build_wall((4, 0), 4, 'y')
        self.build_wall((2, 3), 2, 'x')
        door1 = Item(1, 3, 'door', self, 0, '🚪')

        self.build_wall((14, 0), 10, 'y')
        self.build_wall((0, 0), 50, 'x')
        self.build_wall((0, 0), 15, 'y')
        self.build_wall((0, 9), 50, 'x')

    def print_toolbar(self):
        if self.time >= 0 and self.time < 200:
            time_emoji = '🌄'
        if self.time < 1200 and self.time >= 200:
            time_emoji = '☀️'
        if self.time >= 1200 and self.time < 1400:
            time_emoji = '🌅'
        if self.time >= 1400:
            time_emoji = '🌙'
        if self.watch in self.blecks.inventory:
            contents = f"{time_emoji} Time: {int(self.time)}; Day: {self.day}; HP: {self.blecks.hp}; Energy: {int(self.blecks.energy_modifier * 100)}%; Gold: {self.blecks.gold};"
        else:
            contents = f"{time_emoji} Day: {self.day}; HP: {self.blecks.hp}; Gold: {self.blecks.gold};"
        print(contents)

    def npc_turn(self):
        self.time += self.blecks.speed / self.blecks.energy_modifier
        
        if self.time > 2400:
            self.time -= 2400
            self.day += 1
        for x in Person._registry:
            if x.is_alive and x.name != 'blecks':
                for i in range(int(self.blecks.speed / self.blecks.energy_modifier)):
                    if x.turn_clock == x.speed:
                        x.turn_clock = 0
                        self.npc_take_turn(x)
                    else:
                        x.turn_clock += 1
        self.player_turn(self.messages)

    def npc_take_turn(self, npc):
        if npc.is_stunned == True:
            if npc.stun_timer > 0:
                npc.stun_timer -=1
                if npc.subtype == 'civilian' and npc.emoji != '⛓':
                    npc.emoji = '😵'
            else:
                npc.is_stunned = False
        
        elif len(npc.guard_targets) > 0:
            if self.blecks in npc.guard_targets:
                i = self.blecks
            else:
                i = Reverse(npc.guard_targets)[0]
                
            i_xy = (i.x, i.y)
            npc_xy = (npc.x, npc.y)
            distance = distance_between(i_xy, npc_xy)
            if distance < 1.0 and (i.is_stunned == True or 'taser' not in [item.name for item in npc.inventory]):
                self.messages = []
                i.emoji = '⛓'
                i.is_stunned = True
                i.stun_timer = 100
                
                draw_grid(g)
                if i.name == 'blecks':
                    input(f"{npc.name}: you're under arrest!\n you spend thr rest of your life in prison..")
                npc.guard_targets.remove(i)
                
            elif i.y == npc.y and i.is_stunned == False:
                if (i.x - npc.x) >= 1 and (i.x - npc.x) <= 3:
                    dir = 'd'
                    npc.tase(dir)
                elif (i.x - npc.x) <= -1 and (i.x - npc.x) >= -3:
                    dir = 'a'
                    npc.tase(dir)
                    
            elif i.x == npc.x and i.is_stunned == False:
                if i.y - npc.y >= 1 and i.y - npc.y <= 3:
                    dir = 's'
                    npc.tase(dir)
                elif i.y - npc.y <= -1 and i.y - npc.y >= -3:
                    dir = 'w'
                    npc.tase(dir)
                
            else:
                npc.move_toward((i.x, i.y))
                                    
        elif len(npc.enemies) > 0:
            for i in reversed(npc.enemies):
                distance = distance_between((i.x, i.y), (npc.x, npc.y))
                if distance <= npc.vision:
                    if npc.is_aggressive:
                        if distance >= 1.0:
                            self.messages.append(f"{npc.name} moves toward you!")
                            if npc.subtype == 'civilian':
                                npc.emoji = '😠'
                            npc.move_toward((i.x, i.y))
                            break
                        else:
                            weapon_list = []
                            for object in npc.inventory:
                                weapon_list.append((object, object.base_damage))
        
                            for (key, value) in weapon_list:
                                if value == max([g[1] for g in weapon_list]):
                                    weapon = key
        
                                    npc.hit(i, weapon)
                                    break
                    else:
                        if i.name == 'blecks':
                            message = f"{npc.name} runs from you"
                        else:
                            message = f"{npc.name} runs from {i.name}"
                        if message not in self.messages:
                            
                                self.messages.append(message)
                        if npc.subtype == 'civilian':
                            npc.emoji = '😰'
                            npc.run_from((i.x, i.y))
                else:
                    npc.wander()
        else:
            if npc in self.npc_locations.keys():
                npc.wander()

    def player_turn(self, message=''):
        self.draw_grid(self.g)
        print(str(message) + '\n')
        self.messages = []
        player_choice = input('?')
        self.draw_grid(self.g)
        if self.blecks.is_stunned == True:
            if self.blecks.stun_timer > 0:
                self.messages.append('you are stunned..')
                self.blecks.stun_timer -=1
                self.npc_turn()
            else:
                self.blecks.is_stunned = False
                self.messages.append('you feel in control again')
                self.npc_turn()
             
        elif player_choice == '?':
            print('wasd = move; e = inv; q = pick up')
            self.player_turn()
        elif player_choice == 'a':
            self.blecks.move(player_choice)
        elif player_choice == 'd':
            self.blecks.move(player_choice)
        elif player_choice == 'w':
            self.blecks.move(player_choice)
        elif player_choice == 's':
            self.blecks.move(player_choice)
        elif player_choice == 'e':
            self.blecks.inventory_actions()
        elif player_choice == 'q':
            i = 0
            for x in self.existing_items:
                if (self.blecks.x, self.blecks.y) == x[1]:
                    if x[0].name == 'amphora':
                        options = []
                        i = 1
                        for t in x[0].inventory:
                            print(f"{str(i)}. {t.name} {t.emoji}")
                            i += 1
                        player_choice = input('x. back')
                        if player_choice.isnumeric() == True and int(player_choice) <= len(x[0].inventory): 
                            chosen_item = x[0].inventory[(int(player_choice) - 1)]
                            self.blecks.inventory.append(chosen_item)
                            x[0].inventory.remove(chosen_item)
                            self.messages.append(f"you take the {chosen_item.name}")
                            npc_turn()
                        elif player_choice == 'x':
                            self.player_turn()
                        else:
                            self.player_turn('invalid command')
                        
                            
                            
                    elif x[0].name != 'door' and x[0].name != 'bed':
                        grabbed_item = x[0].name
                        self.blecks.inventory.append(x[0])
                        i += 1
                        self.existing_items.remove(x)
                        if i > 0:
                            self.messages.append(f"{grabbed_item} grabbed")
                            self.npc_turn()
                            break
                        else:
                            self.player_turn('nothing to pick up here ')
                            break
                    else:
                        self.messages.append('can\'t pick that up')
                        self.player_turn(self.messages)
        elif player_choice == 'dt':
            target = input('distance to what?')
            for x, y in self.npc_locations.items():
                if target == x.name:
                    distance = distance_between((self.blecks.x, self.blecks.y), y)
                    self.player_turn(f"{distance} away.")
                    break
        else:
            self.player_turn('invalid command')


    def draw_grid(self, graph, width=1):
        clear() 
        self.print_toolbar()
        
        y_vision = range((self.blecks.y - self.blecks.vision), (self.blecks.y + self.blecks.vision))
        
        for y in y_vision:
            for x in range((self.blecks.x - 8), (self.blecks.x + 8)):
                if (x, y) in self.walls:
                    print("%%-%ds" % width % '▪️', end="")
                elif (x, y) == (self.blecks.x, self.blecks.y):
                    print("%%-%ds" % width % self.blecks.emoji, end="")
                elif (x, y) in self.npc_locations.values():
                    for p, loc in self.npc_locations.items():
                        if loc == (x, y):
                            print("%%-%ds" % width % p.emoji, end="")
                elif (x, y) in (self.get_item_locations()):
                    for (item, loc) in self.existing_items:
                        if (x, y) == loc:
                            print("%%-%ds" % width % item.emoji, end="")
                            break

                else:
                    print("%%-%ds" % width % '◾️', end="")

            print()

    def get_item_locations(self):
        locations = []
        for x in self.existing_items:
            locations.append(x[1])
        return locations

    def npc_receive_item(self, target, item):
        if target.name == 'tamel':
            if (str(item)) == 'dildo':
                self.messages.append(f"{target.name}: oh I been needin one of those ;)")
            else:
                self.messages.append(f"{target.name}: useless")        
        
        elif target.subtype == 'guard':
            message = input(f"{target.name}: sick a bribe! who should i arrest?")
            for x in self.npc_locations.keys():
                if x.name == message:
                    target.guard_targets.append(x)
                    self.messages.append(f"{target.name}: on it.")
        else:
            self.messages.append(f"{target.name}: a {item.name}, wow. thanks for it")
        self.npc_turn()

class Thing:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class MapGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height

class Doodad(Thing):
    def __init__(self, x, y, emoji, name, game, is_obstructive=False):
        super().__init__(x,y)
        self.name = name
        self.is_obstructive = is_obstructive
        self.emoji = emoji
        game.existing_doodads.append((self, (self.x, self.y)))


class Item(Thing):
    instances = []

    def __init__(self, x, y, name, game, base_damage=1, emoji='ℹ️', is_locked=False, inventory=[]):
        super().__init__(x,y)
        self.name = str(name)
        self.emoji = emoji
        self.inventory = inventory
        self.is_locked = is_locked
        self.base_damage = base_damage
        self.in_possession = False
        self.game = game
        self.game.existing_items.append((self, (self.x, self.y)))
        self.__class__.instances.append(self)


g = MapGrid(15, 10)
walls = []
day = 0
time = 0


def draw_grid(graph, width=1):
    global time
    clear() 
    print_toolbar()
    
    y_vision = range((blecks.y - blecks.vision), (blecks.y + blecks.vision))
    
    for y in y_vision:
        for x in range((blecks.x - 8), (blecks.x + 8)):
            if (x, y) in walls:
                print("%%-%ds" % width % '▪️', end="")
            elif (x, y) == (blecks.x, blecks.y):
                print("%%-%ds" % width % blecks.emoji, end="")
            elif (x, y) in npc_locations.values():
                for p, loc in npc_locations.items():
                    if loc == (x, y):
                        print("%%-%ds" % width % p.emoji, end="")
            elif (x, y) in (get_item_locations()):
                for (item, loc) in existing_items:
                    if (x, y) == loc:
                        print("%%-%ds" % width % item.emoji, end="")
                        break

            else:
                print("%%-%ds" % width % '◾️', end="")

        print()


def build_wall(origin_xy, dir_length, axis):
    global walls
    if axis == 'x':
        i = origin_xy[0]
        if dir_length > 0:
            while i < dir_length + origin_xy[0]:
                walls.append((i, origin_xy[1]))
                i += 1
        elif dir_length < 0:
            while i > dir_length + origin_xy[0]:
                walls.append((i, origin_xy[1]))
                i -= 1
    elif axis == 'y':
        i = origin_xy[1]
        if dir_length > 0:
            while i < dir_length + origin_xy[1]:
                walls.append((origin_xy[0], i))
                i += 1
        elif dir_length < 0:
            while i > dir_length + origin_xy[1]:
                walls.append((origin_xy[0], i))
                i -= 1

def doodad_line(origin_xy, dir_length, axis, is_obstructive, emoji, name):
    if axis == 'x':
        i = origin_xy[0]
        if dir_length > 0:
            while i < dir_length + origin_xy[0]:
                name = Doodad(i, origin_xy[1], emoji, name, is_obstructive)
                i += 1
        elif dir_length < 0:
            while i > dir_length + origin_xy[0]:
                walls.append((i, origin_xy[1]))
                i -= 1
    elif axis == 'y':
        i = origin_xy[1]
        if dir_length > 0:
            while i < dir_length + origin_xy[1]:
                walls.append((origin_xy[0], i))
                i += 1
        elif dir_length < 0:
            while i > dir_length + origin_xy[1]:
                walls.append((origin_xy[0], i))
                i -= 1


def clear():
    print('\n')


def message(content):
    draw_grid(g)
    print(str(content))


def input_message(content):
    draw_grid(g)
    input(str(content))


class Person(Thing):
    _registry = []

    def __init__(self, name, game, subtype='civilian',
                 x=1, y=1, hp=10, speed=10, emoji='😐', is_aggressive=False, inventory=[], vision=5):
        super().__init__(x,y)
        self.name = str(name)
        self.game = game
        self.emoji = emoji
        self.subtype = subtype
        self._registry.append(self)
        self.is_alive = True
        self.race = 'human'
        self.hp = hp
        self.speed = speed
        self.is_aggressive = is_aggressive
        self.combat_skill = 1.0
        self.gold = 100
        self.inventory = inventory
        self.move_probability = 70
        self.enemies = []
        self.guard_targets = []
        self.vision = vision
        self.turn_clock = 0
        self.energy_modifier = 1.0
        self.is_stunned = False
        self.stun_timer = 0
        if self.name != 'blecks':
            self.game.npc_locations[self] = (self.x, self.y)

    def move(self, direction):
        if direction == 'd':
            destination = (self.x + 1, self.y)
        elif direction == 'a':
            destination = (self.x - 1, self.y)
        elif direction == 'w':
            destination = (self.x, self.y - 1)
        elif direction == 's':
            destination = (self.x, self.y + 1)
        if destination in self.game.walls:
            if self.name == 'blecks':
                self.game.messages.append('ouch')
                self.game.npc_turn()
        elif destination in self.game.npc_locations.values():
            if self.name == 'blecks':
                for x, y in self.game.npc_locations.items():
                    if y == destination:
                        target = x
                        self.game.npc_interactions(target)
                        break
        
        elif destination == (self.game.blecks.x, self.game.blecks.y):
            if self.name != 'blecks':
                roll = random.randint(1, 2)
                if roll == 1:
                    self.game.messages.append(f"{self.name} almost bumps right into you")
                if roll == 2:
                    self.game.messages.append(f"{self.name}: beg your pardon mister")
        elif destination in [x[1] for x in self.game.existing_items if x[0].name == 'door' and x[0].is_locked]:
            if self.name == 'blecks':
                self.game.messages.append('that door is locked')
                self.game.player_turn(self.game.messages)
        else:
            self.x = destination[0]
            self.y = destination[1]
            self.game.npc_locations[self] = (self.x, self.y)
            if self.name == 'blecks':
                items_here = []
                for x in self.game.existing_items:
                        if x[0].name == 'bed' and x[1] == (self.game.blecks.x, self.game.blecks.y):
                            if self.game.time >= 1400:
                                sleep_choice = input('sleep? (y/n)')
                                self.game.draw_grid(self.game.g)
                                if sleep_choice == 'y':
                            
                                    sleep_amount = 2400 - self.game.time
                                    self.game.time += (sleep_amount)
                                    self.game.blecks.energy_modifier = 1 - (800 - sleep_amount) / 1600
                                    npc_turn()
                                    break
                            else:
                                self.game.player_turn('you can only sleep at night (1400-2400)')
                                break
                        elif (self.game.blecks.x, self.game.blecks.y) == x[1]:
                            items_here.append(x[0])
                if len(items_here) > 0:
                    i = 1
                    for ih in items_here:
                        self.game.messages.append(ih.emoji + ' ' + str(ih.name))
                        i += 1
                self.game.npc_turn()

    def hit(self, target, weapon):
        damage_dealt = weapon.base_damage * self.combat_skill * self.energy_modifier
        target.take_damage(self, damage_dealt, weapon)
    
    def tase(self, direction):
        if direction == 'w':
            dest = (self.x, self.y-1)
            dest2 = (self.x, self.y-2)
            dest3 = (self.x, self.y-3)
        elif direction == 's':
            dest = (self.x, self.y+1)
            dest2 = (self.x, self.y+2)
            dest3 = (self.x, self.y+3)
        elif direction == 'a':
            dest = (self.x-1, self.y)
            dest2 = (self.x-2, self.y)
            dest3 = (self.x-3, self.y)
        elif direction == 'd':
            dest = (self.x+1, self.y)
            dest2 = (self.x+2, self.y)
            dest3 = (self.x+3, self.y)
            
        bolt1 = Item(dest[0], dest[1], 'bolt', self, 0, '⚡️')
        draw_grid(g)
        tm.sleep(0.15)
        bolt2 = Item(dest2[0], dest2[1], 'bolt', self, 0, '⚡️')
        draw_grid(g)
        tm.sleep(0.15)
        bolt3 = Item(dest3[0], dest3[1], 'bolt', self, 0, '⚡️')
        draw_grid(g)
        tm.sleep(0.15)
        existing_items.remove((bolt1, (dest[0], dest[1])))
        existing_items.remove((bolt2, (dest2[0], dest2[1])))
        existing_items.remove((bolt3, (dest3[0], dest3[1])))
        bolt1.x = -1
        bolt1.y = -1
        bolt2.x = -1
        bolt2.y = -1
        bolt3.x = -1
        bolt3.y = -1
        bolt1.emoji = ''
        bolt2.emoji = ''
        bolt3.emoji = ''
        draw_grid(g)
        for (key, value) in self.game.npc_locations.items():
            if key.name != 'blecks':
                if (dest[0], dest[1]) == value or (dest2[0], dest2[1]) == value or (dest3[0], dest3[1]) == value:
                    self.game.messages.append(f"{key.name} gets zapped!")
                    key.is_stunned = True
                    key.stun_timer = 4
                    if key.subtype == 'civilian':
                        if key.emoji != '⛓':
                            key.emoji = '😵'
                    if self not in key.enemies:
                            key.enemies.append(self)
                    key.take_damage(self, 1, taser)
        if (dest[0], dest[1]) == (self.game.blecks.x, self.game.blecks.y) or (dest2[0], dest2[1]) == (self.game.blecks.x, self.game.blecks.y) or (dest3[0], dest3[1]) == (self.game.blecks.x, self.game.blecks.y):
            self.game.messages.append(f"you get zapped!")
            self.game.blecks.is_stunned = True
            self.game.blecks.stun_timer = 4
            self.game.blecks.take_damage(self, 1, taser)
                
        npc_turn()
            
        
    def item_actions(self, item):
        actions = ['drop', 'place/give']
        if item.base_damage > 0:
            actions.append('hit with')
        if item.name == 'taser':
            actions.append('tase')
        if item.name == 'pen':
            actions.append('write')
        if item.name == 'key':
            actions.append('lock/unlock')
        i = 1
        for x in actions:
            print(str(i) + '. ' + x + ' ' + item.emoji)
            i += 1
        player_choice = input('x = back\n')
        self.game.draw_grid(self.game.g)
        if player_choice.isnumeric() == True:
            if actions[(int(player_choice) - 1)] == 'drop':
                self.game.existing_items.append((item, (self.game.blecks.x, self.game.blecks.y)))
                self.inventory.remove(item)
                self.game.messages.append(f"you drop the {item.name}")
                self.game.npc_turn()
            if actions[(int(player_choice) - 1)] == 'place/give':
                dir = input('what direction? ')
                self.game.draw_grid(g)
                if dir == 'd':
                    destination = (self.game.blecks.x + 1, self.game.blecks.y)
                elif dir == 'a':
                    destination = (self.game.blecks.x - 1, self.game.blecks.y)
                elif dir == 'w':
                    destination = (self.game.blecks.x, self.game.blecks.y - 1)
                elif dir == 's':
                    destination = (self.game.blecks.x, self.game.blecks.y + 1)
                else:
                    print('invalid command\n')
                    self.item_actions(item)
                for p in existing_items:
                    if p[0].name == 'amphora' and p[1] == destination:
                        p[0].inventory.append(item)
                        self.game.blecks.inventory.remove(item)
                        self.game.messages.append(f"you put the {item.name} in the amphora")
                        self.game.npc_turn()
                        break
                if destination in self.game.npc_locations.values():
                    for key, value in self.game.npc_locations.items():
                        if value == destination:
                            target = key
                    self.inventory.remove(item)
                    game.npc_receive_item(target, item)
                elif destination in self.game.walls:
                    print('impossible!\n')
                    self.item_actions(item)
                
                else:
                    existing_items.append((item, destination))
                    self.inventory.remove(item)
                    self.game.messages.append(f"you place the {item.name}")
                    self.game.npc_turn()
            if actions[(int(player_choice) - 1)] == 'hit with':
                dir = input('in what direction? ')
                if dir == 'd':
                    destination = (self.game.blecks.x + 1, self.game.blecks.y)
                elif dir == 'a':
                    destination = (self.game.blecks.x - 1, self.game.blecks.y)
                elif dir == 'w':
                    destination = (self.game.blecks.x, self.game.blecks.y - 1)
                elif dir == 's':
                    destination = (self.game.blecks.x, self.game.blecks.y + 1)
                else:
                    print('invalid command\n')
                    self.item_actions(item)
                if destination in self.game.npc_locations.values():
                    for key, value in self.game.npc_locations.items():
                        if value == destination:
                            target = key
                    if self not in target.enemies:
                        target.enemies.append(self)

                    self.hit(target, item)

                else:
                    self.game.messages.append(f"you swing the {item.name} through the air..")
                    self.game.npc_turn()
            if actions[(int(player_choice) - 1)] == 'tase':
                dir = input('in what direction? ')
                self.tase(dir)
            if actions[(int(player_choice) - 1)] == 'lock/unlock':
                dir = input('in what direction? ')
                if dir == 'w':
                    dest = (self.x, self.y - 1)
                if dir == 's':
                    dest = (self.x, self.y + 1)
                if dir == 'a':
                    dest = (self.x - 1, self.y)
                if dir == 'd':
                    dest = (self.x + 1, self.y)
                for (i, loc) in existing_items:
                    if i.name == 'door' and loc == dest:
                        if i.is_locked == True:
                            i.is_locked = False
                            self.game.messages.append('you unlock the door')
                            
                        else:
                            i.is_locked = True
                            self.game.messages.append('you lock the door')
                        self.game.npc_turn()
                        break
                self.game.npc_turn()
            if actions[(int(player_choice) - 1)] == 'write':
                i = 1
                for p in self.inventory:
                    if p.name == 'notepad':
                        promi # TODO fix this!!
                    
        elif player_choice == 'x':
            self.game.player_turn()

    def move_toward(self, destination):
        x_dist = destination[0] - self.x
        y_dist = destination[1] - self.y
        if abs(x_dist) > abs(y_dist):
            if x_dist > 0:
                if ((self.x + 1), self.y) not in self.game.walls:
                    direction = 'd'
                else:
                    if y_dist > 0:
                        direction = 's'
                    else:
                        direction = 'w'

            if x_dist < 0:
                if ((self.x - 1), self.y) not in self.game.walls:
                    direction = 'a'
                else:
                    if y_dist > 0:
                        direction = 's'
                    else:
                        direction = 'w'

        elif abs(y_dist) > abs(x_dist):
            if y_dist > 0:
                if ((self.x), self.y + 1) not in self.game.walls:
                    direction = 's'
                else:
                    if x_dist > 0:
                        direction = 'd'
                    else:
                        direction = 'a'

            if y_dist < 0:
                if ((self.x), self.y - 1) not in self.game.walls:
                    direction = 'w'
                else:
                    if x_dist > 0:
                        direction = 'd'
                    else:
                        direction = 'a'

        elif abs(y_dist) == abs(x_dist):
            coinflip = random.randint(0, 1)
            if coinflip == 0:
                if y_dist > 0:
                    direction = 's'
                elif y_dist < 0:
                    direction = 'w'
            elif coinflip == 1:
                if x_dist > 0:
                    direction = 'd'
                elif x_dist < 0:
                    direction = 'a'

        self.move(direction)
    
    
    def run_from(self, destination):
        x_dist = destination[0] - self.x
        y_dist = destination[1] - self.y
        if abs(x_dist) > abs(y_dist):
            if x_dist > 0:
                if ((self.x + 1), self.y) not in self.game.walls:
                    direction = 'a'
                else:
                    if y_dist > 0:
                        direction = 's'
                    else:
                        direction = 'w'

            if x_dist < 0:
                if ((self.x - 1), self.y) not in self.game.walls:
                    direction = 'd'
                else:
                    if y_dist > 0:
                        direction = 's'
                    else:
                        direction = 'w'

        elif abs(y_dist) > abs(x_dist):
            if y_dist > 0:
                if ((self.x), self.y + 1) not in self.game.walls:
                    direction = 'w'
                else:
                    if x_dist > 0:
                        direction = 'd'
                    else:
                        direction = 'a'

            if y_dist < 0:
                if ((self.x), self.y - 1) not in self.game.walls:
                    direction = 's'
                else:
                    if x_dist > 0:
                        direction = 'd'
                    else:
                        direction = 'a'

        elif abs(y_dist) == abs(x_dist):
            coinflip = random.randint(0, 1)
            if coinflip == 0:
                if y_dist > 0:
                    direction = 'w'
                elif y_dist < 0:
                    direction = 's'
            elif coinflip == 1:
                if x_dist > 0:
                    direction = 'a'
                elif x_dist < 0:
                    direction = 'd'

        self.move(direction)

    def take_damage(self, dealer, amount, weapon):
        if self.name != 'blecks':
            roll = random.randint(1, 2)
            if amount >= self.hp / 2 or self.hp - amount <= 4:
                if roll == 1:

                    if self.subtype == 'civilian':
                        self.game.messages.append(f"{self.name} screams!")
                        self.emoji = '😱'

                elif roll == 2:

                    if self.subtype == 'civilian':
                        self.game.messages.append(f"{self.name}: aahh!")
                        self.emoji = '😱'

            else:
                if roll == 1:
                    if self.subtype == 'civilian':
                        self.game.messages.append(f"{self.name} flinches")
                        self.emoji = '😨'

                elif roll == 2:
                    if self.subtype == 'civilian':
                        self.game.messages.append(f"{self.name}: ow!")
                        self.emoji = '😨'

        else:
            if dealer.subtype == 'civilian':
                dealer.emoji = '😡'
            if weapon.name != 'taser':
                self.game.messages.append(f"{dealer.name} hits you with a {weapon.name}!")
            
        if self.subtype == 'civilian' or self.subtype == 'guard':
            for p in self.game.npc_locations.keys():
                if p.subtype == 'guard' and dealer.subtype != 'guard':
                    if distance_between((dealer.x, dealer.y), (p.x, p.y)) <= p.vision:
                        p.guard_targets.append(dealer)
                        self.game.messages.append(f"{p.name}: not in my town you don't!")
            
            
        self.hp -= amount
        if self.hp <= 0:
            if self.name == 'blecks':
                self.game.blecks.emoji = '💀'
                draw_grid(g)
                print(self.game.messages)
                input('\n you die..')
            else:
                self.game.messages.append(f"{self.name} dies...")
                    
                for key, value in self.game.npc_locations.items():
                    if value == (self.x, self.y):
                        del self.game.npc_locations[key]
                        self.is_alive = False
                        Person._registry.remove(self)
                        break
        if dealer.name == 'blecks' and weapon.name != 'taser':
            npc_turn()

    def inventory_actions(self):
        i = 1
        for x in self.inventory:
            print(str(i) + '. ' + x.emoji + ' ' + x.name)
            i += 1
        player_choice = input('x = back\n')
        self.game.draw_grid(self.game.g)
        if player_choice.isnumeric() == True:
            chosen_item = self.inventory[int(player_choice) - 1]
            self.item_actions(chosen_item)
        elif player_choice == 'x':
            self.game.player_turn()
        else:
            print('invalid command\n')
            self.inventory_actions()

    def wander(self):
        move_roll = random.randint(1, 100)
        if move_roll <= self.move_probability:
            dir_roll = random.randint(1, 4)
            if dir_roll == 1:
                direction = 'd'
            elif dir_roll == 2:
                direction = 'a'
            elif dir_roll == 3:
                direction = 'w'
            elif dir_roll == 4:
                direction = 's'
            if self.subtype == 'civilian':
                self.emoji = '😐'
            self.move(direction)


def main():
    """
    Run a new blecks game!
    """
    game = Game()
    intro = "Welcome, Blecks. It's the big city now. see for yourself...\n one character per command: \n wasd = move; e = inv; q = pick up"
    game.place_objects()
    game.player_turn(intro)


# If this script is being run directly (not just being imported by another script), run main()
if __name__ == "__main__":
    sys.exit(main())
