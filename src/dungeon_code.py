import random
from itertools import permutations, combinations_with_replacement
import json


def get_orientation(s):
    if s == '': return 0
    d = {'l':-1,'c':0,'r':1,'b':2}
    return sum([d[i] for i in s.lower()])%4

def make_orient_dict(s):
    o = get_orientation(s)
    move_list = ['c','r','b','l']
    return {i%4:m for i,m in zip(range(o,o+4), move_list)}

def spiral_back(s, lvl):
    if len(s) == lvl-1: return s
    mirror_dict = {'l':'r','r':'l','c':'b','b':'c'}
    d = {'l':'r','r':'l','c':'c'}
    return mirror_dict[s[0]] + s[1:-2] + s[-1]

def forking_paths(x, p, lvl, b=[]):
    if len(x) > 0: b.append(x[:])
    if len(x) < lvl:
        if len(x)==0: s=4
        else: s=3
        for i in p[:s]:
            forking_paths(x+[i],p)
    return b


class room():
    def __init__(self, name, path, desc = ''):
        self.name = name
        self.path = path
        self.desc = desc
        self.is_edge = False
        self.flip_orient = False

    def set_neighbors(self, door_0, door_1, door_2, door_3):
        self.doors = door_0, door_1, door_2, door_3

    def print_info(self):
        print('Current room:', self.name)
        print('Path:', self.path)
        print('Neighbors: ', end='')
        print(', '.join(self.doors))
        print('--------------------------------')

class room_crawler():
    def __init__(self, load_json=True, shuffle=True, lvl=3):
        self.lvl=lvl
        self.load_room_list()
        self.shuffle_rooms(shuffle)
        if load_json:
            self.load_from_json()
        else:
            self.build_room_tree()
        self.orient = 0
        self.start_room()
        self.o_dict = {'l':-1,'c':0,'r':1,'b':2}
        self.dir_dialogue = {   'l':'To your left is a door leading to the',
                                'c': 'In front of you is a door leading to the',
                                'r': 'To your right is a door leading to the',
                                'b': 'Behind you is a door leading to the' }
        self.moves = []

    def load_room_list(self):
        with open('../json_docs/room_list7.json','r') as f:
            self.room_list = json.load(f)

    def shuffle_rooms(self, shuffle):
        if shuffle:
            random.seed(1337) #random.seed(7)
            random.shuffle(self.room_list)

    def build_room_tree(self):
        b = forking_paths([],['l','r','c','b'], self.lvl)
        b = [''.join(i) for i in b]
        self.rooms = {i:j for i,j in zip(b, self.room_list)}
        self.rooms[''] = 'Start'
        d = dict()
        for i in [''] + b:
            r = room(self.rooms[i], i)
            o = make_orient_dict(i)
            neighbors = [i + o[j] if o[j] != 'b' else i[:-1] for j in range(4)]
            if len(i) == self.lvl:
                neighbors = [spiral_back(n,self.lvl) for n in neighbors]
                r.is_edge = True
            r.set_neighbors(*[self.rooms[n] for n in neighbors])
            d[r.name] = r
        self.room_dict = d
        self.room_list = self.room_list[:len(b)]

    def load_from_json(self):
        with open('../json_docs/tomb_of_terribleness.json','r') as f:
            self.rooms = json.load(f)
        d = dict()
        for i in self.rooms.keys():
            r = room(self.rooms[i], i)
            o = make_orient_dict(i)
            neighbors = [i + o[j] if o[j] != 'b' else i[:-1] for j in range(4)]
            if len(i) == self.lvl:
                neighbors = [spiral_back(n,self.lvl) for n in neighbors]
                r.is_edge = True
            r.set_neighbors(*[self.rooms[n] for n in neighbors])
            d[r.name] = r
        self.room_dict = d
        self.room_list = [i for i in self.room_dict.keys()]

    def start_room(self):
        self.current_room = self.room_dict['Start']
        self._make_move_conv()

    def print_info(self):
        for i in self.room_dict.items():
            i[1].print_info()

    def _make_move_conv(self):
        move_list = ['c','r','b','l']
        o = self.orient
        self.dir_to_orient = {m:i%4 for i,m in zip(range(o,o+4), move_list)}

    def update_orientation(self, d):
        self.orient = (self.orient + self.o_dict[d]) % 4

    def is_start_door(self, d):
        return (self.current_room.name == 'Start') and (self.dir_to_orient[d] == 2)

    def enter_room(self, skip_separator=False):
        print('You enter the', self.current_room.name)
        if not skip_separator: print('------------------------------')

    def move(self, d, verbose=True, debug=False):
        d = d.lower()
        x = self.dir_to_orient[d]
        next_room = self.room_dict[self.current_room.doors[x]]
        self.update_orientation(d)
        self._make_move_conv()
        self.current_room = next_room
        if verbose:
            if self.current_room.is_edge and next_room.is_edge:
                print('cross over')
            self.enter_room(skip_separator=True)
            if debug:
                print('Location:', self.current_room.path)
                print('Orientation:', self.orient)
            print('------------------------------')

    def look(self, d):
        d = d.lower()
        if self.is_start_door(d):
            print('\t Behind you is a door leading back out of the old wing.')
        else:
            print('\t',self.dir_dialogue[d], self.current_room.doors[self.dir_to_orient[d]])

    def look_around(self):
        for i in ['l','c','r','b']:
            self.look(i)

class DungeonHandler():
    def __init__(self, *args, monster_pop=16, lvl=3):
        self.lvl=lvl
        self.monster_pop = monster_pop
        self.names = args
        self.crawlers = dict()
        self.make_crawlers()
        self.make_monsters()

    def make_crawlers(self):
        for i in self.names:
            rc = room_crawler(lvl=self.lvl)
            setattr(self, i, rc)
            self.crawlers[i] = rc

    def make_monsters(self):
        self.monsters = [room_crawler() for i in range(self.monster_pop)]
        for i in self.monsters:
            i.current_room = i.room_dict[random.choice(i.room_list)]

    def move_monsters(self, silent=False):
        player_rooms = [i.current_room.name for i in self.crawlers.values()]
        for i in range(self.monster_pop):
            m = random.choice(['r','c','l','b'])
            self.monsters[i].move(m, verbose=False)
            if not silent:
                print(self.monsters[i].current_room.name)
            if self.monsters[i].current_room.name in player_rooms:
                print("Monster collision!")

    def move_all(self,m):
        for i in self.names:
            self.crawlers[i].move(m, verbose=False)
        self.crawlers[i].enter_room()

    def look(self):
        if len(set([i.current_room.name for i in self.crawlers.values()])) == 1:
            self.crawlers['jeeves'].look_around()
        else:
            print('Not all adventurers are in the same room.')

    def player_locations(self):
        for i,j in zip(self.crawlers.keys(), self.crawlers.values()):
            print(i,':',j.current_room.name)

    def is_player(self, x):
        if x in [i.current_room.name for i in self.crawlers.values()]:
            return True
        else: return False

    def is_monster(self, x):
        if x in [i.current_room.name for i in self.monsters]:
            return True
        else: return False

    def room_occ(self,x):
        if self.is_monster(x) and self.is_player(x):
            return '⬛☠ '
        if self.is_monster(x):
            return '⬛    ' # 'XXXX'
        if self.is_player(x):
            return '⇨   '# '⬅⬅' # '⬜⬜'
        else:
            return '      '

    def forking_paths(self, x, fork_func, a):
        p = ['l','r','c','b']
        if len(x) > 0:
            path = ''.join(x)
            fork_func(path, a[path], self.room_occ(a[path]))
        if len(x) < self.lvl:
            if len(x)==0: s=4
            else: s=3
            for i in p[:s]:
                self.forking_paths(x+[i], fork_func, a)

    def dungeonmap(self):
        a = self.crawlers['jeeves'].rooms
        lvl = 3
        b = []
        def format_room(path, rm_name, rm_occ):
            print(rm_occ,'\t'*(len(path)), path.upper(), ':', rm_name)
        self.forking_paths([], format_room, a)

    def save_dungeon(self):
        a = self.crawlers['jeeves'].rooms
        lvl = 3
        b = []
        def format_room(path, rm_name, rm_occ):
            with open('../json_docs/tomb_of_terribleness.json', 'a') as f:
                sep='\t'*(len(path)-1)
                f.write('{}"{}":"{}",\n'.format(sep, path, rm_name))
        self.forking_paths([], format_room, a)
