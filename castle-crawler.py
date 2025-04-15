import random

# ===============================
# GRID CONFIGURATION & GLOBALS
# ===============================
GRID_MIN = -5       # Minimum x/y coordinate
GRID_MAX = 5        # Maximum x/y coordinate
ROOM_PROBABILITY = 0.7  # Chance a cell (non-forced) gets a room

# -------------------------------
# Secret Path Variables
# -------------------------------
# The secret sequence of moves to eventually trigger the Final Boss Room.
secret_sequence = ["east", "north", "west", "south", "east", "north", "west", "south"]
# Indices (0-indexed) that are locked and require a silver key.
secret_locked_indices = {1, 4, 6}
secret_keys_needed = len(secret_locked_indices)  # Number of silver keys to distribute and require in secret moves
secret_path_progress = 0  # Tracks correct progress along the sequence

# ===============================
# Room Types & Descriptions
# ===============================
room_types = ["library", "kitchen", "armory", "bedchamber", "study", "dungeon", "crypt", "gallery"]

room_type_descriptions = {
    "library": "You enter a quiet library filled with dusty tomes and ancient scrolls.",
    "kitchen": "You step into the castle's kitchen, where the aroma of stale bread and herbs lingers.",
    "armory": "You find yourself in an armory, with racks of glistening weapons and battered shields lining the walls.",
    "bedchamber": "You enter a dimly lit bedchamber, where an opulent bed and faded decor suggest once royal inhabitants.",
    "study": "You enter a study cluttered with maps, parchments, and mysterious artifacts.",
    "dungeon": "You descend into a dungeon, where cold, damp stone and iron bars evoke a sense of dread.",
    "crypt": "You step into a silent crypt, the air thick with the scent of decay and ancient secrets.",
    "gallery": "You wander into an art gallery, where portraits of nobility watch over the room in silent judgment."
}

# ===============================
# SPECIAL ROOMS (Not on the Grid)
# ===============================
special_rooms = {
    "final_boss_room": {
        "name": "final_boss_room",
        "description": ("You have entered the final chamber. A massive figure looms before you—the Final Boss, "
                        "radiating unfathomable malice. This is the threshold to the treasure..."),
        "items": [],
        "exits": {},  # To be set dynamically.
        "locked": False,
        "dark": False,
        "monsters": ["final boss"]
    },
    "secret_treasure_room": {
        "name": "secret_treasure_room",
        "description": ("Incredible! You've discovered the secret treasure room filled with riches beyond imagination. "
                        "Glittering gold, rare weapons, enchanted armor, and ancient relics are piled high."),
        "items": ["legendary sword", "enchanted armor", "infinite health potion", "golden crown"],
        "exits": {},
        "locked": False,
        "dark": False,
        "monsters": []
    }
}

# ===============================
# GRID-BASED ROOM STORAGE
# ===============================
# grid_rooms will be a dictionary keyed by (x, y) tuples.
grid_rooms = {}

# ===============================
# PLAYER STATE
# ===============================
# The player's "position" is a tuple for grid rooms, or a string key if in a special room.
player_state = {
    "position": (0, 0),       # Starting at (0,0) – the Entry Hall.
    "inventory": [],
    "health": 100,
    "torch_active": False,    # If True, a torch is active and will burn out on the next move.
    "equipment": {            # Equipment slots: one each for helmet, armor, shield, boots, gloves; two weapon slots.
        "helmet": None,
        "armor": None,
        "shield": None,
        "boots": None,
        "gloves": None,
        "weapon_left": None,
        "weapon_right": None
    },
    "last_room": None         # Stores the grid coordinate from which the player entered the Final Boss Room.
}

# ===============================
# HELPER FUNCTIONS
# ===============================
def get_offset(direction):
    """Return (dx, dy) for the given cardinal direction."""
    offsets = {"north": (0, 1), "south": (0, -1), "east": (1, 0), "west": (-1, 0)}
    return offsets.get(direction, (0, 0))

def get_current_room():
    """Return the current room object from grid_rooms or special_rooms."""
    pos = player_state["position"]
    if isinstance(pos, tuple):
        return grid_rooms.get(pos)
    else:
        return special_rooms.get(pos)

# ===============================
# ROOM GENERATION FUNCTIONS
# ===============================
def create_random_room(room_type):
    """
    Create a random room of the given room_type.
      - The room's description is pulled from room_type_descriptions.
      - It gets 1–3 items randomly chosen from the items pool.
      - It has a random chance to be dark.
      - It gets a random list of monsters.
      - It is marked as locked with a 30% chance.
    """
    items_pool = ["health potion", "shield", "helmet", "boots", "gloves", "armor"]
    monsters_pool = ["goblin", "orc", "skeleton", "zombie", "bat"]
    room = {
        "name": room_type,
        "description": room_type_descriptions[room_type],
        "items": random.sample(items_pool, random.randint(1, min(3, len(items_pool)))),
        "exits": {},  # Exits will be computed later.
        "locked": (random.random() < 0.3),  # 30% chance the room is locked.
        "dark": random.choice([True, False]),
        "monsters": []
    }
    # Determine monsters: 50% chance no monster; 30% one monster; 20% two monsters.
    roll = random.random()
    if roll < 0.5:
        room["monsters"] = []
    elif roll < 0.8:
        room["monsters"] = [random.choice(monsters_pool)]
    else:
        if len(monsters_pool) >= 2:
            room["monsters"] = random.sample(monsters_pool, 2)
        else:
            room["monsters"] = [random.choice(monsters_pool)]
    return room

def initialize_grid():
    """
    Pre-generate the grid for coordinates from GRID_MIN to GRID_MAX.
      - Each cell (other than forced ones) gets a room with probability ROOM_PROBABILITY.
      - Forced cells: (0,0) is the Entry Hall; (0,1) is the Throne Room.
      - Additionally, no room is created for cells where x == 0 and y < 0.
      - For each random room, a room type is randomly chosen from room_types.
    """
    global grid_rooms
    for x in range(GRID_MIN, GRID_MAX + 1):
        for y in range(GRID_MIN, GRID_MAX + 1):
            coord = (x, y)
            # Skip cells along the center column with negative y.
            if x == 0 and y < 0:
                continue
            if coord == (0, 0):
                grid_rooms[coord] = {
                    "name": "entry_hall",
                    "description": ("You stand in a bright, welcoming entry hall of Castle Crawler. "
                                    "Sunlight streams through a stained-glass window."),
                    "items": ["torch", "sword"],
                    "exits": {},
                    "locked": False,
                    "dark": False,
                    "monsters": []
                }
            elif coord == (0, 1):
                grid_rooms[coord] = {
                    "name": "throne_room",
                    "description": "You enter the grand throne room, echoes of past royalty haunting the air.",
                    "items": [],
                    "exits": {},
                    "locked": False,
                    "dark": False,
                    "monsters": []
                }
            else:
                if random.random() < ROOM_PROBABILITY:
                    rtype = random.choice(room_types)
                    grid_rooms[coord] = create_random_room(rtype)
    # Compute exits for each room based on adjacent coordinates.
    for (x, y), room in grid_rooms.items():
        exits = {}
        if (x, y + 1) in grid_rooms:
            exits["north"] = (x, y + 1)
        if (x, y - 1) in grid_rooms:
            exits["south"] = (x, y - 1)
        if (x + 1, y) in grid_rooms:
            exits["east"] = (x + 1, y)
        if (x - 1, y) in grid_rooms:
            exits["west"] = (x - 1, y)
        room["exits"] = exits

# After grid initialization, distribute silver keys.
def distribute_silver_keys():
    """Distribute 'silver key' into randomly selected grid rooms (excluding forced rooms)."""
    available_coords = [coord for coord in grid_rooms if grid_rooms[coord]["name"] not in ["entry_hall", "throne_room"]]
    if len(available_coords) < secret_keys_needed:
        selected_coords = available_coords  # if not enough, assign to all.
    else:
        selected_coords = random.sample(available_coords, secret_keys_needed)
    for coord in selected_coords:
        grid_rooms[coord]["items"].append("silver key")

# Initialize the grid and then distribute silver keys.
initialize_grid()
distribute_silver_keys()

# ===============================
# GAME ENGINE FUNCTIONS (GRID-BASED)
# ===============================
def describe_current_room():
    """Display the current room's description, items, monsters, and available exits."""
    room = get_current_room()
    if room is None:
        print("There's nothing here.")
        return
    print(f"\n{room['description']}")
    # If the room is dark and the player has no torch, nothing is visible.
    if room["dark"] and "torch" not in player_state["inventory"]:
        print("It's too dark to see anything clearly.")
    else:
        if room["items"]:
            print("You see:")
            for item in room["items"]:
                print(f"- {item}")
        if room["monsters"]:
            print("Monsters here:")
            for monster in room["monsters"]:
                print(f"- {monster}")
    # Show exits.
    if isinstance(player_state["position"], tuple):
        exits = room.get("exits", {})
        if exits:
            print("Exits:", ", ".join(exits.keys()))
        else:
            print("There are no obvious exits!")
    else:
        if room.get("exits"):
            print("Exits:", ", ".join(room["exits"].keys()))
        else:
            print("There are no obvious exits!")

def move(direction):
    """
    Move the player in the specified direction.
      - If in a grid room, compute the new coordinate and check for boundaries.
      - Before moving, if the destination room is locked, check if the player has a silver key.
          * If yes, consume the key and unlock the room.
          * If not, inform the player that the door is locked.
      - Integrate secret path logic: If the move matches the secret sequence, increment progress;
        if near-complete, transition to the Final Boss Room.
      - In special rooms, use fixed exit mapping.
      - Process torch burnout upon entering a new room.
    """
    global secret_path_progress

    # Special room processing.
    if not isinstance(player_state["position"], tuple):
        current_key = player_state["position"]
        room = special_rooms.get(current_key)
        if room and direction in room.get("exits", {}):
            new_key = room["exits"][direction]
            player_state["position"] = new_key
            describe_current_room()
        else:
            print("You can't go that way.")
        return

    # Grid room processing.
    current_coord = player_state["position"]
    room = grid_rooms.get(current_coord)
    if room is None:
        print("You are in an empty void!")
        return

    # Secret Path Logic.
    if secret_path_progress < len(secret_sequence) and direction == secret_sequence[secret_path_progress]:
        secret_path_progress += 1
    else:
        secret_path_progress = 0

    # If secret sequence is at penultimate step, transition to Final Boss Room.
    if secret_path_progress == len(secret_sequence) - 1:
        player_state["last_room"] = current_coord
        print("A heavy door creaks open, revealing a foreboding chamber...")
        special_rooms["final_boss_room"]["exits"] = {
            "back": current_coord,
            "continue": "secret_treasure_room"
        }
        player_state["position"] = "final_boss_room"
        secret_path_progress = 0
        describe_current_room()
        return

    # Compute new coordinate.
    dx, dy = get_offset(direction)
    new_coord = (current_coord[0] + dx, current_coord[1] + dy)
    if new_coord[0] < GRID_MIN or new_coord[0] > GRID_MAX or new_coord[1] < GRID_MIN or new_coord[1] > GRID_MAX:
        print("You can't go that way; the castle's walls block your path!")
        return
    if new_coord in grid_rooms:
        dest_room = grid_rooms[new_coord]
        # Check if destination room is locked.
        if dest_room.get("locked", False):
            if "silver key" in player_state["inventory"]:
                player_state["inventory"].remove("silver key")
                dest_room["locked"] = False
                print("You unlock the door with a silver key.")
            else:
                print("The door is locked! You need a silver key to enter.")
                return
        player_state["position"] = new_coord
        describe_current_room()
    else:
        print("You can't go that way.")

    # Torch burnout: if a torch was active, it burns out when entering a new room.
    if player_state.get("torch_active"):
        print("Your torch burns out as you enter the new room.")
        if "torch" in player_state["inventory"]:
            player_state["inventory"].remove("torch")
        player_state["torch_active"] = False

# ===============================
# INVENTORY, EQUIPMENT & COMBAT FUNCTIONS
# ===============================
def take(item_name):
    """Pick up a specific item from the current room."""
    room = get_current_room()
    if room and item_name in room.get("items", []):
        player_state["inventory"].append(item_name)
        room["items"].remove(item_name)
        print(f"You took the {item_name}.")
    else:
        print(f"There is no {item_name} here.")

def take_all():
    """Pick up all items in the current room."""
    room = get_current_room()
    if room and room.get("items"):
        for item in room["items"][:]:
            player_state["inventory"].append(item)
        room["items"].clear()
        print("You took all the items in the room.")
    else:
        print("There are no items to take.")

def drop(item_name):
    """
    Drop a specified item from your inventory into the current room.
    The item is removed from inventory and added to the room's items list.
    """
    if item_name in player_state["inventory"]:
        player_state["inventory"].remove(item_name)
        room = get_current_room()
        if room is not None:
            room.setdefault("items", []).append(item_name)
        print(f"You dropped the {item_name}.")
    else:
        print(f"You don't have {item_name} in your inventory.")

def show_inventory():
    """Display the items in your inventory."""
    if player_state["inventory"]:
        print("You have:")
        for item in player_state["inventory"]:
            print(f"- {item}")
    else:
        print("Your inventory is empty.")

def equip(item_name):
    """
    Equip an item from your inventory.
    Allowed equipment:
      - One each: helmet, armor (or enchanted armor), shield, boots, gloves.
      - Two weapon slots for a sword or legendary sword.
    """
    if item_name not in player_state["inventory"]:
        print(f"You don't have a {item_name} to equip.")
        return
    if item_name == "helmet":
        if player_state["equipment"]["helmet"] is None:
            player_state["equipment"]["helmet"] = item_name
            player_state["inventory"].remove(item_name)
            print("You don the helmet.")
        else:
            print("You already have a helmet equipped.")
    elif item_name in ["armor", "enchanted armor"]:
        if player_state["equipment"]["armor"] is None:
            player_state["equipment"]["armor"] = item_name
            player_state["inventory"].remove(item_name)
            print("You don the armor.")
        else:
            print("You already have armor equipped.")
    elif item_name == "shield":
        if player_state["equipment"]["shield"] is None:
            player_state["equipment"]["shield"] = item_name
            player_state["inventory"].remove(item_name)
            print("You equip the shield.")
        else:
            print("You already have a shield equipped.")
    elif item_name == "boots":
        if player_state["equipment"]["boots"] is None:
            player_state["equipment"]["boots"] = item_name
            player_state["inventory"].remove(item_name)
            print("You put on the boots.")
        else:
            print("You already have boots equipped.")
    elif item_name == "gloves":
        if player_state["equipment"]["gloves"] is None:
            player_state["equipment"]["gloves"] = item_name
            player_state["inventory"].remove(item_name)
            print("You put on the gloves.")
        else:
            print("You already have gloves equipped.")
    elif item_name in ["sword", "legendary sword"]:
        if player_state["equipment"]["weapon_left"] is None:
            player_state["equipment"]["weapon_left"] = item_name
            player_state["inventory"].remove(item_name)
            print("You wield the sword in your left hand.")
        elif player_state["equipment"]["weapon_right"] is None:
            player_state["equipment"]["weapon_right"] = item_name
            player_state["inventory"].remove(item_name)
            print("You wield the sword in your right hand.")
        else:
            print("Both your hands are already occupied.")
    else:
        print(f"The {item_name} cannot be equipped.")

def show_equipment():
    """Display your currently equipped items."""
    eq = player_state["equipment"]
    print("Equipped Items:")
    for slot, item in eq.items():
        print(f"{slot.capitalize()}: {item if item is not None else 'Empty'}")

def use(item_name):
    """
    Use a consumable item:
      - Health potion: increases health by 25 (capped at 100).
      - Torch: lights the current room and marks the torch as active (so it burns out on the next move).
    """
    if item_name in player_state["inventory"]:
        if item_name == "health potion":
            new_health = min(100, player_state["health"] + 25)
            player_state["health"] = new_health
            print(f"You used a health potion. Your health is now: {new_health}")
            player_state["inventory"].remove("health potion")
        elif item_name == "torch":
            room = get_current_room()
            if room is not None:
                room["dark"] = False
            print("You light the torch. The room is now illuminated.")
            player_state["torch_active"] = True
        else:
            print(f"You cannot 'use' the {item_name} directly.")
    else:
        print(f"You don't have a {item_name}.")

def attack(monster_name):
    """
    Attack a monster in the current room.
    New randomness:
      - ~25% chance the monster attacks first.
      - ~25% chance your attack misses, leaving you vulnerable to a counterattack.
    If armed (with a sword or legendary sword), your attack normally defeats the monster.
    If unarmed, the monster deals damage reduced by 15% per equipped item (capped at 75%).
    """
    room = get_current_room()
    if room is None or monster_name not in room.get("monsters", []):
        print(f"There is no {monster_name} here.")
        return

    monster_first_roll = random.random()  # 25% chance for monster to strike first.
    miss_roll = random.random()             # 25% chance for your attack to miss.

    base_damages = {
        "goblin": 5,
        "orc": 10,
        "skeleton": 8,
        "zombie": 7,
        "bat": 3,
        "final boss": 30
    }
    base_damage = base_damages.get(monster_name, 5)
    damage_bonus = secret_path_progress * 2  # Bonus damage from secret path progress.
    total_damage = base_damage + damage_bonus

    armed = (player_state["equipment"]["weapon_left"] in ["sword", "legendary sword"] or
             player_state["equipment"]["weapon_right"] in ["sword", "legendary sword"])

    if monster_first_roll < 0.25:
        print("The monster strikes before you can act!")
        armor_slots = ["helmet", "armor", "shield", "boots", "gloves"]
        armor_count = sum(1 for slot in armor_slots if player_state["equipment"].get(slot) is not None)
        reduction_percentage = min(armor_count * 0.15, 0.75)
        inflicted_damage = round(total_damage * (1 - reduction_percentage))
        if inflicted_damage < 1 and total_damage > 0:
            inflicted_damage = 1
        print(f"The {monster_name} deals {inflicted_damage} damage to you!")
        player_state["health"] -= inflicted_damage
        print("Your health is now:", player_state["health"])
        if player_state["health"] <= 0:
            print("You have been slain by the monster's preemptive strike!")
            return

    if miss_roll < 0.25:
        print("You swing your weapon, but miss the monster entirely!")
        armor_slots = ["helmet", "armor", "shield", "boots", "gloves"]
        armor_count = sum(1 for slot in armor_slots if player_state["equipment"].get(slot) is not None)
        reduction_percentage = min(armor_count * 0.15, 0.75)
        inflicted_damage = round(total_damage * (1 - reduction_percentage))
        if inflicted_damage < 1 and total_damage > 0:
            inflicted_damage = 1
        print(f"Your miss leaves you vulnerable! The {monster_name} counterattacks, dealing {inflicted_damage} damage!")
        player_state["health"] -= inflicted_damage
        print("Your health is now:", player_state["health"])
        return

    if armed:
        print(f"You attack the {monster_name} with your weapon and defeat it!")
        room["monsters"].remove(monster_name)
    else:
        armor_slots = ["helmet", "armor", "shield", "boots", "gloves"]
        armor_count = sum(1 for slot in armor_slots if player_state["equipment"].get(slot) is not None)
        reduction_percentage = min(armor_count * 0.15, 0.75)
        inflicted_damage = round(total_damage * (1 - reduction_percentage))
        if inflicted_damage < 1 and total_damage > 0:
            inflicted_damage = 1
        print(f"You are unarmed! The {monster_name} attacks, dealing {inflicted_damage} damage!")
        player_state["health"] -= inflicted_damage
        print("Your health is now:", player_state["health"])
        room["monsters"].remove(monster_name)
        while True:
            response = input("You must escape! Type 'run' to flee: ").strip().lower()
            if response == "run":
                if room.get("exits"):
                    new_pos = random.choice(list(room["exits"].values()))
                    player_state["position"] = new_pos
                    describe_current_room()
                else:
                    print("There is nowhere to run!")
                break
            else:
                print("You hesitate! The monster strikes again!")
                player_state["health"] -= inflicted_damage
                print("Your health is now:", player_state["health"])

def show_help():
    """Display a list of available commands."""
    help_text = """
Available Commands:
- go <direction>   : Move in the specified direction (e.g., 'go north', 'go east', etc.).
- look             : Describe your current surroundings.
- take <item>      : Pick up an item (e.g., 'take sword').
- take all         : Pick up all items in the room.
- drop <item>      : Drop a specific item from your inventory into the current room.
- use <item>       : Use an item (e.g., 'use health potion', 'use torch').
- equip <item>     : Equip an item (e.g., 'equip helmet', 'equip sword').
- inventory        : Show your current inventory.
- equipment        : Show what you currently have equipped.
- attack <monster> : Attack a monster in the room.
- help             : Display this help message.
- quit             : Exit the game.
"""
    print(help_text)

# ===============================
# GAME LOOP & WELCOME MESSAGE
# ===============================
print("""
Welcome to Castle Crawler!

Venture into the shadowed halls of this ancient castle, where whispers of a hidden treasure echo in every corridor.
Legends speak of riches beyond imagination—and of those who perished seeking them. Your mission, should you dare,
is to uncover the secret path leading to the treasure, or fall to the castle’s eternal curse.

May fortune favor the brave!
""")
describe_current_room()

while True:
    command = input("\n> ").strip().lower()
    if command == "quit":
        print("Goodbye, brave crawler.")
        break
    elif command.startswith("go "):
        direction = command[3:]
        move(direction)
    elif command == "look":
        describe_current_room()
    elif command.startswith("take all"):
        take_all()
    elif command.startswith("take "):
        item = command[5:]
        take(item)
    elif command.startswith("drop "):
        item = command[5:]
        drop(item)
    elif command == "inventory":
        show_inventory()
    elif command.startswith("equip "):
        item = command[6:]
        equip(item)
    elif command == "equipment":
        show_equipment()
    elif command.startswith("use "):
        item = command[4:]
        use(item)
    elif command.startswith("attack "):
        monster = command[7:]
        attack(monster)
    elif command == "help":
        show_help()
    else:
        print("I don't understand that command.")
