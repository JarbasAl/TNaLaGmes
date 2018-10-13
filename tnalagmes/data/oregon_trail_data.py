TERMINOLOGY = {
    'ammunition': ['ammunition'],
    'armour': ['clothing'],
    'attack_damage': ['injuries'],
    'enemy': ['riders'],
    'fuel': ['your oxen team'],
    'medicine': ['miscellaneous supplies'],
    'passive_damage': ['pneumonia'],
    'supplies': ['food'],
    "currency": ["cash"]
}

RANDOM_EVENTS = {
    'attack': {'conclusion': 'quickest draw outside of dodge city!!!\n'
                             "you got 'em!",
               'damage': 'you got shot in the leg and they took one '
                         'of your oxen\n'
                         'better have a doc look at your wound',
               'die': '',
               'error': 'you ran out of bullets---they get lots of '
                        'cash',
               'events': [],
               'intro': 'bandits attack'
               },
    'illness': {'conclusion': '',
                'damage': '',
                'die': '',
                'error': '',
                'events': [],
                'intro': ''
                },
    'poison': {'conclusion': '',
               'die': 'you die of snakebite since you have no '
                      'medicine',
               'error': '',
               'events': [],
               'intro': 'you killed a poisonous snake after it bit '
                        'you'
               },
    'animal': {'conclusion': "nice shootin' pardner---they didn't get "
                             'much',
               'damage': 'you were too low on bullets--\n'
                         'the wolves overpowered you',
               'die': '',
               'error': 'slow on the draw---they got at your food and '
                        'clothes',
               'events': [],
               'intro': 'wild animals attack!'
               },
    'companion': {'conclusion': '',
                  'damage': '',
                  'die': '',
                  'error': '',
                  'events': [],
                  'intro': 'bad luck---your daughter broke her arm\n'
                           'you had to stop and use supplies to make '
                           'a sling'
                  },
    'bad_terrain': {'conclusion': '',
                    'damage': '',
                    'die': '',
                    'error': '',
                    'events': [],
                    'intro': 'wagon gets swamped fording river--lose '
                             'food and clothes'},
    'companion_lose': {'conclusion': '',
                       'damage': '',
                       'die': '',
                       'error': '',
                       'events': [],
                       'intro': 'your son gets lost---spend half the '
                                'day looking for him'},
    'find_supplies': {'conclusion': '',
                      'damage': '',
                      'die': '',
                      'error': '',
                      'events': [],
                      'intro': 'helpful indians show you where to '
                               'find more food'},
    'fuel_damage': {'conclusion': '',
                    'damage': '',
                    'die': '',
                    'error': '',
                    'events': [],
                    'intro': 'ox wanders off---spend time looking for '
                             'it'
                    },
    'shelter_damage': {'conclusion': '',
                       'damage': '',
                       'die': '',
                       'error': '',
                       'events': [],
                       'intro': 'wagon breaks down--lose time and '
                                'supplies fixing it'
                       },
    'shelter_fire': {'conclusion': '',
                     'damage': '',
                     'die': '',
                     'error': '',
                     'events': [],
                     'intro': 'there was a fire in your wagon--food '
                              'and supplies damaged'
                     },
    'supply_damage': {'conclusion': '',
                      'damage': '',
                      'die': '',
                      'error': '',
                      'events': [],
                      'intro': 'unsafe water--lose time looking for '
                               'clean spring'
                      },
    'vehicle_damage': {'conclusion': '',
                       'damage': '',
                       'die': '',
                       'error': '',
                       'events': [],
                       'intro': 'ox injures leg---slows you down rest '
                                'of trip'
                       },
    'heavy_rain': {'conclusion': '',
                   'die': '',
                   'error': '',
                   'events': [],
                   'intro': 'heavy rains---time and supplies lost'
                   },
    'storm': {'conclusion': '',
              'die': '',
              'error': '',
              'events': [],
              'intro': 'hail storm---supplies damaged'
              },
    'fog': {'conclusion': '',
            'die': '',
            'error': '',
            'events': [],
            'intro': 'lose your way in heavy fog---time is '
                     'lost'
            },
    'cold': {'conclusion': 'you have enough clothing to keep '
                           'you warm',
             'die': '',
             'error': "you don't have enough clothing to "
                      'keep you warm',
             'events': [],
             'intro': 'cold weather---brrrrrrr!---'
             }
}

GAME_EVENTS = {
    'damage': {'conclusion': '',
               'error': 'you ran out medical supplies\nyou died of',
               'high': 'bad illness---medicine used',
               'intro': '',
               'mild': 'mild illness---medicine used'},
    'difficulty_damage': {'conclusion': '',
                          'error': '',
                          'events': [],
                          'intro': 'blizzard in mountain pass--time and supplies '
                                   'lost'},
    'easy_difficulty': {'conclusion': 'you made it safely through south pass--no '
                                      'snow',
                        'events': ['you got lost---lose valuable time trying to '
                                   'find trail!',
                                   'wagon damaged!---lose time and supplies',
                                   'the going gets slow'],
                        'intro': 'rugged mountains'
                        },
    'enemy_encounter': {'conclusion': '',
                        'damage': 'lousy shot---you got knifed\n'
                                  "you have to see ol' doc blanchard",
                        'die': 'you ran out of bullets and got massacred by the ',
                        'enemy_run': 'they did not attack',
                        'high_score': 'nice shooting---you drove them off',
                        'hostile_conclusion': ' were hostile--check for losses',
                        'hostile_intro': 'they look hostile',
                        'intro': ' ahead.',
                        'low_score': 'kinda slow with your colt .45',
                        'number_questions': ['tactics\n'
                                             '(1) run  (2) attack  (3) continue  '
                                             '(4) circle wagons\n'
                                             "if you run you'll gain time but "
                                             'wear down your oxen\n'
                                             "if you circle you'll lose time"],
                        'peaceful_conclusion': ' were friendly, but check for '
                                               'possible losses',
                        'peaceful_intro': "they don't look hostile"
                        },
    'explore': {'conclusion': '',
                'error': 'tough---you need more bullets to go hunting',
                'events': ["ri\x07ght betwee\x07n the eye\x07's---you got a\x07 "
                           'big one!!\x07!!',
                           'sorry---no luck today',
                           'nice shot--right through the neck--feast tonight!!'],
                'intro': ''
                },
    'game_over': {'conclusion': 'distance remaining: ',
                  'error': 'time has run out.  winter has set in and you did not '
                           'reach oregon.'
                  },
    'hard_difficulty': {'conclusion': '', 'intro': ''},
    'heal': {'conclusion': "doctor's bill is $20",
             'die': 'you died of',
             'error': "you can't afford a doctor",
             'events': [],
             'intro': ''
             },
    'intro': {'conclusion': 'you can spend all your money before you start your '
                            'trip -\n'
                            'or you can save some of your cash to spend at forts '
                            'along\n'
                            'the way when you run low.  however, items cost more '
                            'at\n'
                            'the forts.  you can also go hunting along the way to '
                            'get\n'
                            'more food.\n'
                            'whenever you have to use your trusty rifle along the '
                            'way,\n'
                            'you will see the words: type bang.  the faster you '
                            'type\n'
                            "in the word 'bang' and hit the 'return' key, the "
                            'better\n'
                            "luck you'll have with your gun.\n"
                            "when asked to enter money amounts, don't use a '$'.\n"
                            'good luck!!!',
              'intro': 'instructions!\n'
                       'this program simulates a trip over the oregon trail from\n'
                       'independence, missouri to oregon city, oregon in 1847.\n'
                       'your family of five will cover the 2000 mile oregon '
                       'trail\n'
                       'in 5-6 months --- if you make it alive.\n'
                       "you had saved $900 to spend for the trip, and you've "
                       'just\n'
                       '   paid $200 for a wagon.\n'
                       'you will need to spend the rest of your money on the\n'
                       '   following items:\n'
                       '     oxen - you can spend $200-$300 on your team\n'
                       "            the more you spend, the faster you'll go\n"
                       "               because you'll have better animals\n"
                       '     food - the more you have, the less chance there\n'
                       '               is of getting sick\n'
                       '     ammunition - $1 buys a belt of 50 bullets\n'
                       '            you will need bullets for attacks by animals\n'
                       '               and bandits, and for hunting food\n'
                       '     clothing - this is especially important for the '
                       'cold\n'
                       '               weather you will encounter when crossing\n'
                       '               the mountains\n'
                       '     miscellaneous supplies - this includes medicine and\n'
                       '               other things you will need for sickness\n'
                       '               and emergency repairs'
              },
    'inventory': {'conclusion': 'after all your purchases, you now have '
                                '{inv.money} dollars left',
                  'error': 'you overspent--you only had $700 to spend.  buy again',
                  'intro': 'how much do you want to spend on '
                  },
    'lose': {'conclusion': 'we thank you for this information and we are sorry '
                           'you\n'
                           "didn't make it to the great territory of oregon\n"
                           'better luck next time\n'
                           '                              sincerely\n'
                           '                 the oregon city chamber of commerce',
             'error': 'your aunt nellie in st. louis is anxious to hear',
             'intro': 'do to your unfortunate situation, there are a few\n'
                      ' formalities we must go through',
             'positive_response': '',
             'yes_no_questions': ['would you like a minister?',
                                  'would you like a fancy funeral?',
                                  'would you like us to inform your next of '
                                  'kin?']
             },
    'low_supplies': {'intro': "you'd better do some hunting or buy food and "
                              'soon!!!!'
                     },
    'maintenance': {'conclusion': '',
                    'error': "you can't eat that well",
                    'intro': 'do you want to eat (1) poorly  (2) moderately\n'
                             'or (3) well'
                    },
    'medium_difficulty': {'conclusion': 'you made it safely through south '
                                        'pass--no snow',
                          'intro': ''
                          },
    'numeric': {'error': 'impossible', 'high': 'too high', 'low': 'too low'},
    'shop': {'conclusion': '',
             'error': "you don't have that much--keep your spending down",
             'events': [],
             'intro': 'enter what you wish to spend on the following'
             },
    'turn': {'die': 'you ran out of food and starved to death',
             'intro': 'do you want to (1) stop at the next fort, (2) hunt, \n'
                      'or (3) continue'
             },
    'win': {'conclusion': 'president james k. polk sends you his\n'
                          '      heartiest congratulations\n'
                          '           and wishes you a prosperous life ahead\n'
                          '                      at your new home',
            'intro': 'you finally arrived at oregon city\n'
                     ' after {objective.total_distance} long miles---hooray!!!!!'
            }
}
