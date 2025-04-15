                                        I. 3 Project Ideas from ChatGPT:
a. Rule-Based Chatbot – simulates human-like conversation by matching user inputs to predefined patterns or keywords and responding accordingly. It does not "understand" language but rather responds based on explicit rules using if-elif blocks, regular expressions, and dictionaries mapping input phrases to outputs. Below is a snippet of code it would use to create pattern-matching rules:
IF user_input CONTAINS "sad" THEN respond "I'm sorry to hear that. Want to talk more about it?"
IF user_input STARTS WITH "I feel" THEN respond "Why do you feel {X}?"
	
b. Puzzle Solver / Logic Game – acts like a human logic puzzle solver. It applies heuristics and deterministic rules to deduce solutions to puzzles like Sudoku, Logic grid puzzles, and simple constraint satisfaction problems. It applies hard-coded strategies a human would use. For example to help solve a Sudoku puzzle, we would use the below code snippet:
IF a cell has only one valid number left THEN place that number
IF a number can only fit in one cell of a row/column/box THEN place it there
For heuristics it would use something along the following:

Rule Type                 Rule Example Logic
Naked Single            "Only one number fits in this cell"
Hidden Single           "This number only fits in one spot in this row"
Elimination             "If a number is placed, eliminate it from peers"

With python, the puzzle grid would get iterated over and apply these rules until the board stops changing.
	
c. Text-Based Adventure Game Engine – an interactive narrative game where the player explores, collects items, talks to characters, and solves puzzles using typed commands. Each action advances the story or affects the world. The world is built of rooms/scenes, and the game responds to typed input using rules. This I feel is more complex than the other 2 examples, because it uses much more than if-elif statements; it also involves user input, directions, items (which includes inventories and destroying/selling/dropping items, stores maybe to buy/sell items), global environmentals/decisions having affects on other later decisions/outcomes, etc. The rules would be used to Control valid player actions (go north, take key, use torch), Check conditions (IF player has key AND door is locked THEN unlock door), or Trigger events or consequences (IF player enters room_with_monster AND has no sword THEN game over). Each rule would check the game state and determine outcomes. Example rules:

Situation                                Rule Logic
Player tries to enter locked room  | IF current_room == "hallway" AND "key" in inventory: unlock door
Player picks up torch              | IF "torch" in room_items: add "torch" to inventory
Player uses sword on monster       | IF current_room == "monster_den" AND "sword" in inventory: kill monster
Player types invalid command       | ELSE: show "I don't understand that."

Rooms, items, and actions are often defined using dictionaries or simple classes, and you write the logic in if/elif structures or rule-engine-like functions.


I am choosing to create the text-based adventure game engine. I feel like it’s a little different than the other options (so hopefully not as boring to code and test). I actually created something like this at work before just using if else statements in bash, but was extremely simple. Just from using chatGPT, it included so many things I didn’t even come close to thinking about when I made my game before.


                                             II. Designing Castle Crawler, the text-based adventure game engine
We'll break the logic into 6 key categories:
    1. Movement Rules – handle navigation between rooms. Pseudocode:
       IF command == "go north" AND "north" in current_room.exits
        THEN current_room = current_room.exits["north"]
       ELSE IF command == "go north" AND current_room.locked["north"] == True
       IF "key" in inventory
        THEN unlock and move
       ELSE
        THEN print "The door is locked."
    2. Interaction Rules – handle using or manipulating objects. Pseudocode:
       IF command == "take torch" AND "torch" in current_room.items
        THEN inventory.add("torch") AND current_room.items.remove("torch")
       IF command == "use torch" AND "torch" in inventory AND current_room.dark
        THEN current_room.dark = False AND print("You light the torch. Now you can see!")
    3. Inventory Rules – inspect or manage player’s inventory. Pseudocode:
       IF command == "inventory"
        THEN print inventory list
    4. Condition-Based Rules – enforce logical restrictions or trigger story events. Pseudocode:
       IF command == "open door" AND "key" not in inventory
        THEN print "You need a key to open this door."
       IF current_room == "monster_den" AND "sword" not in inventory
        THEN print "The monster attacks! You died." AND end_game()
    5. Room Description & Discovery Rules – show the rooms description, visible items, and available exits. Pseudocode:
       IF entering a new room:
        IF room is dark AND "torch" not in inventory
          THEN print "It's too dark to see anything."
        ELSE
          print current_room.description
          print "You see: " + list of items in current_room.items
          print "Exits: " + list of current_room.exits.keys()
       IF command == "look":
        THEN re-display the same info above
    6. Fallback/Error Handling Rules – catch anything unrecognized or invalid. Pseudocode:
       IF command not in allowed_actions
        THEN print "I don't understand that command. Try again."

Optional Advanced Rules (Add Later)
    • NPC interaction: IF player says "talk to wizard" THEN return dialog
    • Timed events: IF player stays in a room too long THEN trigger trap
    • Quest logic: IF all objectives completed THEN unlock final door

                                                    IV. Reflection
