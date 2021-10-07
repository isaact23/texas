# TEXAS HOLD'EM (Program by Isaac Thompson)

import random, itertools, copy, sys
import os
from playsound import playsound
import pyttsx3

# Set to true to enable betting.
do_bets = False

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
SUITS = ['C', 'D', 'H', 'S']
SORT_RANKS = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, 'T': 8, 'J': 9, 'Q': 10, 'K': 11, 'A': 12}
SORT_SUITS = {'C': 0, 'D': 1, 'H': 2, 'S': 3}
RANK_NAMES = {'2': 'Two', '3': 'Three', '4': 'Four', '5': 'Five', '6': 'Six', '7': 'Seven', '8': 'Eight', '9': 'Nine', 'T': 'Ten',
              'J': 'Jack', 'Q': 'Queen', 'K': 'King', 'A': 'Ace'}
SUIT_NAMES = {'C': 'Clubs', 'D': 'Diamonds', 'H': 'Hearts', 'S': 'Spades'}

DEAL_IN = ["Deal me in.",
           "What are you waiting for? Give me two cards.",
           "You're the dealer. Go ahead and deal.",
           "Give me some cards please."]
FLOP = ["Time for the flop.",
        "Put down the first three cards"]
PLAYER_SPEECH_1 = ["Not bad.",
                   "That's more than half.",
                   "The odds are in your favor.",
                   "You have an acknowledgable chance, my friend.",
                   "Just you wait. This will all change."]
PLAYER_SPEECH_2 = ["That's pretty good.",
                   "How sad.",
                   "Don't worry, the odds will change shortly.",
                   "You hear that? It's the winds of change.",
                   "I have to say I am not happy with you."]
PLAYER_SPEECH_3 = ["I might as well fold.",
                   "This is rather unfortunate.",
                   "Dang.",
                   "No. This can't be happening. No!",
                   "Welp. This is happening."]
PLAYER_WIN = ["You won this time around.",
              "You win. What a shame.",
              "You won. For the first time. For the last time.",
              "Welp, I've been destroyed.",
              "Good game.",
              "Let's play again so I can righteously win."]
CPU_SPEECH_1 = ["Looks good for me.",
                "That's a good thing.",
                "Hopefully it stays that way.",
                "Flip a coin and it'll land on my side.",
                "Heh."]
CPU_SPEECH_2 = ["Prepare to lose.",
                "The odds are in my favor.",
                "Ha ha ha ha.",
                "I will be beating you shortly.",
                "I will trump you!"]
CPU_SPEECH_3 = ["You sir are doomed.",
                "You might as well fold",
                "Just give up. As far as you know I've got pocket aces",
                "Prepare yourself mentally to be obliterated",
                "This is the end for you!",
                "Ha! You can't win!",
                "You humans will never beat me!"]
CPU_WIN = ["You lose. Would you like to play again?",
           "You have been righteously destroyed.",
           "Good golly. Looks like humans are being phased out.",
           "Rest in peace.",
           "I win. Let's play again so I can win again.",
           "Victory goes to me. What a surprise.",
           "Get wrecked.",
           "You've been destroyed by a computer. How do you feel?",
           "Wow, what a loser. You should have been luckier."]
NEURAL_SPEECH = ["Well, this is going to be a boring round.",
                 "The outlook is not great for either of us",
                 "Let's both fold on three. One, two, three. Just kidding, I never fold.",
                 "I cannot express my infinite exhilaration through my sarcastic robot voice.",
                 "Yawn."]
DRAW = ["We tied. What are the odds?",
        "Tie game. How embarassing for both of us."]

# Set up audio engine
audio_engine = pyttsx3.init()
audio_engine.setProperty('rate', 210)

# Synthesize text as speech
def say(text):
    print(text)
    try:
        audio_engine.say(text)
        audio_engine.runAndWait()
    except:
        pass

# Convert a card identity to a name (like 3H to Three of Hearts)
def name_card(card):
    return RANK_NAMES[card[0]] + " of " + SUIT_NAMES[card[1]]

# Report the calculated game odds to the player.
# Includes statements of astronomical wit.
def tell_odds(prediction):
    player_percent = str(round(prediction['player_win'] * 1000)/10)
    player_str = "You are " + player_percent + " percent likely to win. "
    computer_percent = str(round(prediction['computer_win'] * 1000)/10)
    computer_str = "I am " + computer_percent + " percent likely to win. "
    #draw = str(round(chances['draw'] * 1000)/10)
    if prediction['draw'] > 0.5:
        say("This is probably going to be a tie round.")
    elif prediction['player_win'] > 0.9:
        say(player_str + random.choice(PLAYER_SPEECH_3))
    elif prediction['player_win'] > 0.7:
        say(player_str + random.choice(PLAYER_SPEECH_2))
    elif prediction['player_win'] >= 0.5:
        say(player_str + random.choice(PLAYER_SPEECH_1))
    elif prediction['computer_win'] > 0.9:
        say(computer_str + random.choice(CPU_SPEECH_3))
    elif prediction['computer_win'] > 0.7:
        say(computer_str + random.choice(CPU_SPEECH_2))
    elif prediction['computer_win'] > 0.5:
        say(computer_str + random.choice(CPU_SPEECH_1))
    else:
        say(random.choice(NEUTRAL_SPEECH))

# A class that runs the game.
class PredictionAlgorithm():

    def __init__(this):

        this.turn = 1
        this.next_round() # Main setup function - executed every round

        this.player_money = 500
        this.computer_money = 500

    def next_round(this): # Reset and switch turns
        if this.turn == 0:
            this.turn = 1
        else:
            this.turn = 0

        this.community_cards = []
        this.computer_hand = []
        this.player_hand = []

        this.player_bet = 0
        this.computer_bet = 0

        this.deck = []
        for suit in SUITS:
            for rank in RANKS:
                this.deck.append(rank + suit)
        random.shuffle(this.deck)

        this.maximum_percent_loss = round((random.random() + 0.15) * 10) / 10 # Prevents overbetting. The higher, the more aggressive.
        this.maximum_percent_loss = 0.5

    def draw_card(this): # Allow the player to specify a card, then remove it from the deck.
        card = None
        while card == None:
            card = input("Draw a card: ")
            card = card.upper()
            if len(card) != 2:
                print("Not a valid card. Must be two characters long: one for the rank, second for the suit.")
                card = None
            elif (not card[0] in RANKS) or (not card[1] in SUITS):
                print("Not a valid card. Use the format: 2H for Two of Hearts, TC for Ten of Clubs, etc.")
                card = None
            elif not card in this.deck:
                print("That card is no longer in the deck. Choose a different card.")
                card = None
        this.deck.remove(card)

        print("Drew the " + RANK_NAMES[card[0]] + " of " + SUIT_NAMES[card[1]])
        return card

    def play(this): # Go through a round until a winner is determined.

        if do_bets:
            say("You have " + str(this.player_money) + " tokens. I have " + str(this.computer_money) + " tokens.")
            #say("I am playing with an aggressiveness factor of " + str(this.maximum_percent_loss))
            if this.computer_money == 0:
                say(random.choice(PLAYER_WIN))
                sys.exit()
            elif this.computer_money == 1:
                say("You play the big blind this round.")
                this.player_bet = 2
                this.computer_bet = 1
            elif (this.turn == 1 or this.player_money == 1) and this.player_money != 0:
                say("You play the small blind this round.")
                this.player_bet = 1
                this.computer_bet = 2
            elif this.turn == 0 and this.player_money > 1:
                say("You play the big blind this round.")
                this.player_bet = 2
                this.computer_bet = 1
            else:
                say(random.choice(CPU_WIN))
            sys.exit()
        
        say(random.choice(DEAL_IN))

        #CardDetector.GetComputerHand()
        for i in range(2):
            this.computer_hand.append(this.draw_card())

        result = this.bets()
        if result == 2:
            return
        if do_bets:
            this.state_bets()
            
        say(random.choice(FLOP))

        for i in range(3):
            this.community_cards.append(this.draw_card())
        
        if do_bets:
            if this.computer_bet != this.computer_money and this.player_bet != this.player_money:
                result = this.bets()
                if result == 2:
                    return
                this.state_bets()
            
        tell_odds(this.find_winning_chances(0.35))

        say("Deal another card.")
        this.community_cards.append(this.draw_card())

        if do_bets:
            if this.computer_bet != this.computer_money and this.player_bet != this.player_money:
                result = this.bets()
                if result == 2:
                    return
                this.state_bets()

        tell_odds(this.find_winning_chances(0.4))

        say("Deal the final card.")
        this.community_cards.append(this.draw_card())

        if do_bets:
            if this.computer_bet != this.computer_money and this.player_bet != this.player_money:
                result = this.bets()
                if result == 2:
                    return
                this.state_bets()

        tell_odds(this.find_winning_chances(0.45))

        say("Alright, show me your hand.")
        for i in range(2):
            this.player_hand.append(this.draw_card())

        player_best_hand = this.find_best_hand(this.community_cards + this.player_hand)
        computer_best_hand = this.find_best_hand(this.community_cards + this.computer_hand)

        say("Your best hand was " + player_best_hand.name)
        say("My best hand was " + computer_best_hand.name)

        winner = this.winning_hand(player_best_hand, computer_best_hand)
        if winner == 0:
            say(random.choice(PLAYER_WIN))
            this.player_wins()
        elif winner == 1:
            say(random.choice(CPU_WIN))
            this.computer_wins()
        elif winner == 2:
            say(random.choice(DRAW))

    def computer_wins(this):
        this.computer_money += this.player_bet
        this.player_money -= this.player_bet
        this.next_round()

    def player_wins(this):
        this.player_money += this.computer_bet
        this.computer_money -= this.computer_bet
        this.next_round()

    def state_bets(this):
        print("You have bet " + str(this.player_bet))
        print("Computer has bet " + str(this.computer_bet))

    # Run through a betting cycle with the player.
    def bets(this):
        if do_bets:
            computer_played = False
            player_played = False
            skip_player = False
            if this.turn == 1:
                skip_player = True

            chances = None
                
            while True: # Betting cycle
                this.state_bets()
                
                if skip_player:
                    skip_player = False
                else: # Player bet
                    bet = [""] # Obtain the command
                    commands = ["bet", "raise", "call", "check", "fold"]
                    while not bet[0] in commands:
                        bet = input("Bet, Raise, Call, Check, or Fold: ").split()
                        if len(bet) == 0:
                            bet = [""]
                        else:
                            bet[0] = bet[0].lower()

                    player_played = True
                    
                    if bet[0] == "bet" or bet[0] == "raise": # Parse the command
                        try:
                            bet[1] = int(bet[1])
                            amount = bet[1]
                            if bet[1] + this.computer_bet > this.player_money:
                                print("You only have " + str(this.player_money))
                                raise Exception() # Break out of try loop and ask for a new bet
                        except: # Get a valid bet
                            amount = -1
                            while amount < 0:
                                amount = input("How much: ")
                                try:
                                    amount = int(amount)
                                    if amount + this.computer_bet > this.player_money:
                                        amount = -1
                                        print("You only have " + str(this.player_money))
                                except:
                                    amount = -1
                        this.player_bet += amount
                    elif bet[0] == "call" or bet[0] == "check":
                        if this.player_bet < this.computer_bet: # Raise the bet to match the computer bet
                            this.player_bet = this.computer_bet
                        if this.player_bet > this.player_money: # Limit calling to the player's money
                            this.player_bet = this.player_money
                        if player_played and computer_played:
                            return
                    elif bet[0] == "fold":
                        this.computer_wins()
                        return 2

                this.state_bets()

                # Computer bet
                if chances == None:
                    chances = this.find_winning_chances({0: 0.22, 3: 0.3, 4: 0.3, 5: 1}[len(this.community_cards)])

                if this.player_bet > this.computer_bet:
                    call_bet = this.player_bet # Match the player without exceeding the computer balance.\
                else:
                    call_bet = this.computer_bet
                if call_bet > this.computer_money:
                    call_bet = this.computer_money

                expected_outcomes = {'fold': this.computer_money - this.computer_bet}

                if this.computer_money - this.computer_bet + 1 > 0: # If we can raise, calculate which raise value is the best.
                    for raise_value in range(0, this.computer_money - this.player_bet + 1):
                        expected_outcomes[raise_value] = {}
                        expected_outcomes[raise_value]['win'] = this.computer_money + this.player_bet + raise_value
                        expected_outcomes[raise_value]['loss'] = this.computer_money - this.player_bet - raise_value
                        expected_outcomes[raise_value]['draw'] = this.computer_money
                        expected_outcomes[raise_value]['expected'] = expected_outcomes[raise_value]['win'] * chances['computer_win'] + \
                                                                     expected_outcomes[raise_value]['loss'] * chances['player_win'] + \
                                                                     expected_outcomes[raise_value]['draw'] * chances['draw']

                computer_played = True

                best_choice = 'fold'
                best_expected_value = expected_outcomes['fold']
                for choice in expected_outcomes:
                    if not choice == 'fold':
                        if expected_outcomes[choice]['expected'] > best_expected_value:
                            #if expected_outcomes[choice]['loss'] >= this.computer_money * (1 - this.maximum_percent_loss):
                            best_choice = choice
                            best_expected_value = expected_outcomes[choice]['expected']

                if best_choice == 'fold':
                    say("I fold.")
                    this.player_wins()
                    return 2
                elif best_choice == 0: # Call/Check
                    if this.computer_bet == this.player_bet:
                        say("I check.")
                    else:
                        say("I call.")
                    this.computer_bet = call_bet
                    if player_played and computer_played:
                        return
                else: # Call and raise
                    say("I call and raise " + str(best_choice))
                    this.computer_bet = this.player_bet + best_choice

    def find_winning_chances(this, accuracy=1): # Accuracy of 1 calculates perfectly, but lower values are faster.
        # Increments for each possible final outcome, then calculated as percentages in the end.
        player_wins = 0
        computer_wins = 0
        draws = 0

        false_deck = copy.deepcopy(this.deck)
        while len(false_deck) > len(this.deck) * accuracy:
            false_deck.pop(random.randrange(0, len(false_deck)))
        
        community_combos = list(itertools.combinations(false_deck, 5 - len(this.community_cards)))
        for community_combo in community_combos:
            community_combo = list(community_combo)
            for card in community_combo:
                false_deck.remove(card) # Temporarily remove the community cards from the deck
            full_community_combo = community_combo + this.community_cards # Add the cards we already know so we have a set of five
            player_combos = list(itertools.combinations(false_deck, 2))
            
            for player_combo in player_combos: # Based on reduced deck, determine all possibilities for the player's hand and beating the computer
                player_combo = list(player_combo)

                best_player_hand = this.find_best_hand(player_combo + full_community_combo)
                best_computer_hand = this.find_best_hand(this.computer_hand + full_community_combo)
                
                winner = this.winning_hand(best_player_hand, best_computer_hand)
                if winner == 0:
                    player_wins += 1
                elif winner == 1:
                    computer_wins += 1
                else:
                    draws += 1
            false_deck += community_combo # Add the cards back to the deck
        
        total_scenarios = player_wins + computer_wins + draws
        return {'player_win': player_wins / total_scenarios,
                'computer_win': computer_wins / total_scenarios,
                'draw': draws / total_scenarios}

    def find_best_hand(this, cards): # Find the best hand out of the community cards and two personal cards.
        combinations = list(itertools.combinations(cards, 5))
        best_hand = None
        
        for combo in combinations:
            hand = Hand()
            hand.cards = list(combo)
            hand.evaluate()
            if best_hand == None:
                best_hand = hand
            else:
                if this.winning_hand(hand, best_hand) == 0:
                    best_hand = hand
            
        return best_hand

    def winning_hand(this, hand0, hand1):
        if hand0.hand_type < hand1.hand_type:
            return 0
        elif hand0.hand_type > hand1.hand_type:
            return 1
        else:
            assert len(hand0.high_cards) == len(hand1.high_cards), 'These two hands have a different number of kickers: ' \
                 + str(hand0.cards) + ' ' + str(hand1.cards)

            i = 0
            while i < len(hand0.high_cards):
                if SORT_RANKS[hand0.high_cards[i][0]] > SORT_RANKS[hand1.high_cards[i][0]]:
                    return 0
                elif SORT_RANKS[hand0.high_cards[i][0]] < SORT_RANKS[hand1.high_cards[i][0]]:
                    return 1
                i += 1

        return 2 # Draw

class Hand(): # 5 card hand

    # Initialize an empty hand.
    def __init__(this, cards=[]):
        this.name = None
        this.hand_type = -1
        this.high_cards = {}

        this.cards = cards

    # Add a card to the hand.
    def append(this, card):
        this.cards.append(card)

    # Determine the value of our hand.
    # Identify royal flush, straights, two-pair combos, etc.
    def evaluate(this):
        
        this.cards = sorted(this.cards, key=lambda card: (SORT_RANKS[card[0]], card[1])) # Sort the cards by rank first, then by suit

        # Flush
        flush = True
        for i, card in enumerate(this.cards):
            if i == 4:
                break
            elif this.cards[i][1] != this.cards[i + 1][1]:
                flush = False
                break

        # Royal flush
        if flush:
            if this.cards[0][0] == 'T' and this.cards[1][0] == 'J' and this.cards[2][0] == 'Q' and this.cards[3][0] == 'K' and this.cards[4][0] == 'A':
                this.hand_type = 0
                this.name = 'Royal Flush'
                return

        # Straight (Search both ways from the beginning card to find straight from both directions
        straight = False
        r = 0
        l = 0
        while True:
            difference = abs(SORT_RANKS[this.cards[r + 1][0]] - SORT_RANKS[this.cards[r][0]])
            if difference == 1 or difference == 12:
                r += 1
                if r == 4:
                    break
            else:
                break
        while True:
            difference = abs(SORT_RANKS[this.cards[-l - 1][0]] - SORT_RANKS[this.cards[-l][0]])
            if difference == 1 or difference == 12:
                l += 1
                if l == 4:
                    break
            else:
                break
        if r + l == 4:
            straight = True

        # Straight flush
        if straight and flush:
            this.hand_type = 1
            if this.cards[r][0] == '4' or this.cards[r][0] == '3' or this.cards[r][0] == '2':
                this.name = 'Straight Flush (Ace-High)'
                this.high_cards[0] = this.cards[4]
            elif this.cards[4][0] == 'A' and this.cards[3][0] == '5':
                this.name = 'Straight Flush (Steel Wheel)'
                this.high_cards[0] = this.cards[r]
            else:
                this.name = 'Straight Flush (' + RANK_NAMES[this.cards[4][0]] + '-High)'
                this.high_cards[0] = this.cards[4]
            return

        # Group cards for later disambiguation
        groups = [[this.cards[0]]]
        for i, card in enumerate(this.cards):
            if i > 0:
                new_card = True
                for group in groups:
                    if group[0][0] == card[0]:
                        group.append(card)
                        new_card = False
                        break
                if new_card:
                    groups.append([card])
        groups = sorted(groups, key=lambda group: -len(group)) # Biggest groups first

        # 4 of a kind
        if len(groups[0]) == 4:
            this.hand_type = 2
            this.high_cards[0] = groups[0][0]
            this.high_cards[1] = groups[1][0]
            this.name = 'Four of a Kind'
            return
                        
        # Full House
        if len(groups[0]) == 3 and len(groups[1]) == 2:
            this.hand_type = 3
            this.high_cards[0] = groups[0][0]
            this.high_cards[1] = groups[1][0]
            if groups[0][0][0] == 'K' and groups[0][1][0] == 'K' and groups[0][2][0] == 'K' and groups[1][0][0] == 'A' and groups[1][1][0] == 'A':
                this.name = 'Full House (Nativity)'
            else:
                this.name = 'Full House'
            return
        
        # Flush
        if flush:
            this.hand_type = 4
            this.high_cards[0] = groups[0][0]
            this.name = 'Flush'
            return
        
        # Straight - code adapted from earlier (Wheel, Sucker Straight)
        if straight:
            this.hand_type = 5
            if this.cards[r][0] == '4' or this.cards[r][0] == '3' or this.cards[r][0] == '2':
                this.name = 'Straight (Ace-High)'
                this.high_cards[0] = this.cards[4]
            elif this.cards[4][0] == 'A' and this.cards[3][0] == '5':
                this.name = 'Sucker Straight'
                this.high_cards[0] = this.cards[r]
            else:
                this.name = 'Straight (' + RANK_NAMES[this.cards[4][0]] + '-High)'
                this.high_cards[0] = this.cards[4]
            return
        
        # Three of a Kind
        if len(groups[0]) == 3:
            this.hand_type = 6
            this.name = 'Three of a Kind'
            this.high_cards[0] = groups[0][0] # Three of a kind
            this.high_cards[1] = groups[2][0] # High kicker
            this.high_cards[2] = groups[1][0] # Low kicker
            return
            
        # Two Pairs
        if len(groups[0]) == 2 and len(groups[1]) == 2:
            this.hand_type = 7
            this.name = 'Two Pairs'
            this.high_cards[0] = groups[1][0] # Highest pair
            this.high_cards[1] = groups[0][0] # Lowest pair
            this.high_cards[2] = groups[2][0] # Kicker
            return
        
        # Pair
        if len(groups[0]) == 2:
            this.hand_type = 8
            this.name = 'Pair'
            this.high_cards[0] = groups[0][0] # Pair
            this.high_cards[1] = groups[3][0] # High kicker
            this.high_cards[2] = groups[2][0] # Mid kicker
            this.high_cards[3] = groups[1][0] # Low kicker
            return
            
        # Junk
        this.hand_type = 9
        this.name = 'Junk'
        assert len(groups) == 5, "Error! We have been dealt a broken hand."
        this.high_cards[0] = groups[4][0] # Highest card
        this.high_cards[1] = groups[3][0]
        this.high_cards[2] = groups[2][0]
        this.high_cards[3] = groups[1][0]
        this.high_cards[4] = groups[0][0] # Lowest card
        return


if __name__ == "__main__":
    ALG = PredictionAlgorithm()
    say("Let's play Texas Hold'Em.")
    while True:
        ALG.play()
