## TNaLaGmes

TNaLaGmes is a Toolbox for Natural Language Games

I asked myself, what if every game object could talk to you with natural language?

TNaLaGmes is a library that provides tools and default models for a variety of constructs, it was made thinking about games, but it really is about text enabling random code constructs!

## Default Constructs

Every object provides some nlp functionality and includes a natural language pipeline that can be easily modified to provide intelligence

by default every object only understands "yes" and "no"

    from tnalagmes import TNaLaGmesConstruct
    
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
    print(construct.output)  # hello world\nhow are you?   #\n was added
    print(construct.output)  # empty
    
    
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


By default turns are disabled, you can enable them by ch

  
## Game Engines

# OregonEngine

Survival Voices Games like Orange Trail

# TextAdventurer

Adventure Games in the infocom spirit

# TextBattle

Turn Based battle games

# TextRPG

Open World Text Rpg Games

## Game Design

1. Not to be killed without warning. 

2. Not to be given horribly unclear hints. 

3. To be able to win without experience of past lives. 

4. To be able to win without knowledge of future events. 

5. Not to have the game closed off without warning. 

6. Not to need to do unlikely things. 

7. Not to need to do boring things for the sake of it. 

8. Not to have to type exactly the right verb. 

9.  To be allowed reasonable synonyms. 

10.  To have a decent parser. 

11.  To have reasonable freedom of action. 

12.  Not to depend much on luck. 

13.  To be able to understand a problem once it is solved. 

14.  Not to be given too many red herrings. 

15.  To have a good reason why something is impossible. 

16.  Not to need to be American. 

17.  To know how the game is getting on. 