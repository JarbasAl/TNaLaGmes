## TNaLaGmes

TNaLaGmes is a Toolbox for Natural Language Games

I asked myself, what if every game object could talk to you with natural language?

TNaLaGmes is a library that provides tools and default models for a variety of constructs, it was made thinking about games, but it really is about text enabling random code constructs!

## Constructs

Every object provides some nlp functionality and includes a natural language pipeline that can be easily modified to provide intelligence

by default every object only understands "yes" and "no"

    from tnalagmes import TNaLaGmesConstruct
    
    construct = TNaLaGmesConstruct()
    
    print(construct.parse_command("no"))
    print(construct.parse_command("yes"))
    
    # you sound negative
    # you sound positive
    # ?

you can access the underlying intent parser directly, you can see the vocabulary for yes and no is well populated

    print(construct.calc_intent("yes"))
    print(construct.calc_intent("no"))
    print(construct.calc_intent("what can you do"))
    
    {'target': None, '__tags__': [{'entities': [{'data': [('yes', 'correct'), ('yes', 'yes'), ('yes', 'affirmative'), ('yes', 'y'), ('yes', 'right'), ('yes', 'confirm'), ('yes', 'agree'), ('yes', 'Concept'), ('yes', 'agreed')], 'match': 'yes', 'key': 'yes', 'confidence': 1.0}], 'match': 'yes', 'start_token': 0, 'end_token': 0, 'key': 'yes', 'from_context': False}], 'intent_type': 'game_object:yes', 'utterance': 'yes', 'yes': 'yes', 'normalized_utterance': 'yes', 'confidence': 1.0}
    {'normalized_utterance': 'no', '__tags__': [{'entities': [{'data': [('no', 'disagree'), ('no', 'abort'), ('no', 'negative'), ('no', 'disagreed'), ('no', 'incorrect'), ('no', 'Concept'), ('no', 'no'), ('no', 'n'), ('no', 'wrong')], 'match': 'no', 'key': 'no', 'confidence': 1.0}], 'match': 'no', 'start_token': 0, 'end_token': 0, 'key': 'no', 'from_context': False}], 'intent_type': 'game_object:no', 'utterance': 'no', 'target': None, 'no': 'no', 'confidence': 1.0}
    {'sent': '', 'conf': 0.0, 'matches': {}, 'name': ''}


TNaLaGmes constructs are powered by adapt and padatious, in essence they are mini mycrofts!

A special property of TNaLaGmesConstruct is the self.output variable

There are input and output buffers for async communication and these are accessed by this variable

    # read buffer
    print(construct.output) # empty
    # put something into the buffer
    construct.output = "hello world"
    # read current buffer
    print(construct.output)  # hello world
    print(construct.output) # empty
    # put something into the buffer
    construct.output = "hello world!"
    construct.output = "how are you?"
    # read current buffer
    print(construct.output)  # hello world\nhow are you?   # \n was added
    print(construct.output)  # empty
    
 
 
##### YOU REACHED A CONSTRUCTION AREA, NOTHING IS COMPLETE 

   
# Calendar

The calendar object tracks the passage of days, it also incorporates the concept of turns for games

    "What day/date/week/weekday/month/year is it?"
    
    
    "next turn"
    "how many turns left"
    "how many turns passed"
    "how many days per turn"
    "maximum number of turns"
    "increase speed"
    "decrease speed"
    "rollback X days/months/weeks/years"
    "advance X days/months/weeks/years"


By default turns are disabled, you can enable them by ....

 
# Progress Tracker

Tracks progress along 2 values

    "total distance"
    "current mileage"
    "add mileage"
    "subtract mileage"
    "are you completed?"
 
# InventoryObject

an object with value, name, description and type

    what are you
    what can you do
    what is your name
    how much are you worth

# Inventory

object package, tracks some currency

    what do you have
    how much money do you have
    how much are you worth
    spend X money

# Ability

an ability for other other objects

    what is your name
    what is your cost
    what is your damage
    what are you
    generate some damage
 
# NPC

basic template for a Non Playable Character

    hello world
    what is your name
    
    attack
    take damage
    heal
    spend mana
    cast spell
 
# Room

object describing a scene 

    look up / down / left / right / front /back / north / south / west / east ....
    who is in the roon
    items in the room
    connected rooms
    describe room
    room name
                    
## Game Engines

A few assumptions are made, all engines are derived from TNaLaGmesEngine

Once again this is not necessarily meant for games, they are just an awesome use case

# TNaLaGmesEngine

This is the base structure to build games out off

    save
    load
    quit
    what game is this
    
All engines start by asking you

        Do you need instructions?

Using the engine! just import it and override on_turn

    from tnalagmes.engines import TNaLaGmesEngine
    
    class TemplateGame(TNaLaGmesEngine):
    
        def __init__(self):
            TNaLaGmesEngine.__init__(self, "TemplateGame",
                                     from_json=False)
            self.calendar.change_speed(1)  # each turn now advances the calendar a day
    
        def on_turn(self):
            # main loop
            pass
     

Run it!

Turn based, but turns are defined by a calendar object that by default tracks real date and start disabled

        class TemplateGame(TNaLaGmesEngine):
       
    
            def __init__(self):
                TNaLaGmesEngine.__init__(self, "TemplateGame")
                self.calendar.change_speed(1)  # each turn now advances the calendar a day
        
            def on_turn(self):
                print(self.calendar.pretty_date)       
                self.calendar.advance_date()
        
        
            if __name__ == "__main__":
                game = TemplateGame()
                game.play()
        

There is a configurable maximum of turns before the engine exits, enabled if you change the game speed, otherwise the engine runs forever

    Do you need instructions?

    no
    
    12, Oct 2018
    13, Oct 2018
    14, Oct 2018
    15, Oct 2018
    16, Oct 2018
    17, Oct 2018
    18, Oct 2018
    19, Oct 2018
    20, Oct 2018
    21, Oct 2018
    22, Oct 2018
    23, Oct 2018
    24, Oct 2018
    25, Oct 2018
    26, Oct 2018
    27, Oct 2018
    28, Oct 2018
    29, Oct 2018
    30, Oct 2018

  
# OregonEngine

Travel Voices Games like [Oregon Trail](http://www.died-of-dysentery.com/oregon-trail.html), game logic based on the [1985 version](https://en.wikipedia.org/wiki/The_Oregon_Trail_(1985_video_game))

# Oregon78Engine

Travel Voices Games like [the original Oregon Trail](https://en.wikipedia.org/wiki/The_Oregon_Trail_(1971_video_game)), game logic ported directly from the [1978 source code](https://www.filfre.net/misc/oregon1978.bas)

# Oregon75Engine

Travel Voices Games like [the original Oregon Trail](https://en.wikipedia.org/wiki/The_Oregon_Trail_(1971_video_game)), game logic ported directly from the [1975 source code](https://www.filfre.net/misc/oregon1975.bas)

Differences between Oregon75 and Oregon78 are minimal

# TextAdventurer

Adventure Games in the infocom spirit

# TextBattle

Turn Based battle games, pokemon style battle

# TextRPG

Open World Text Rpg Games, a rpg world for you to populate with objects

## Game Design

You see where this is going, objects are inteligent, engines are intelligent, everything can be interacted with

Suggestions/Issues/PRs for more engines or object models accepted

Here are some game design guidelines before you run out to make AI powered text games
    
    
    1. Not to be killed without warning. 
    
    2. Not to be given horribly unclear hints. <- made easy for you! just add help intents
    
    3. To be able to win without experience of past lives. 
    
    4. To be able to win without knowledge of future events. 
    
    5. Not to have the game closed off without warning. 
    
    6. Not to need to do unlikely things. 
    
    7. Not to need to do boring things for the sake of it. 
    
    8. Not to have to type exactly the right verb. <- made easy for you! expand keywords
    
    9.  To be allowed reasonable synonyms. <- made easy for you! expand keywords
    
    10.  To have a decent parser. <- solved for you!
    
    11.  To have reasonable freedom of action. <- mostly solved for you! everything can be interacted with
    
    12.  Not to depend much on luck. 
    
    13.  To be able to understand a problem once it is solved. 
    
    14.  Not to be given too many red herrings. 
    
    15.  To have a good reason why something is impossible. 
    
    16.  Not to need to be American. 
    
    17.  To know how the game is getting on. 