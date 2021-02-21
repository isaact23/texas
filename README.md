# texas
A Texas Hold'Em prediction algorithm

I found this code in my archives from several years ago, so I made some
changes to make it functional, then pushed it to GitHub. Complete with an
unfinished betting system and lots of snarky quotes.

## prerequisites

You will need:
* windows 10 (this program has not been tested on other operating systems)
* playing cards (optional)

## how to play

The program will walk you through it. In Texas Hold'em, each player
gets two cards. Deal these cards and tell the computer which cards it has.
Next, put down three cards in the middle and report these to the computer.
As this stage of the game goes on, the computer will continuously calculate
its winning chances by iterating through possible endgame scenarios.
Once five cards are down in the middle, you reveal your hand to the computer.
Whoever has the best 5-card hand wins. You can use all 5 cards in the middle,
4 from the middle and 1 from your hand, or 3 from the middle and 2 from
your hand.

## hand rankings

Note: sometimes players will get the same hand. Ties are broken by looking at
the 'kicker' card and finding the highest number.

* Royal Flush - AKQJT - same suit
* Straight Flush - e.g. 89TJQ - cards of the same suit of sequential ranks
* Four of a Kind - all four cards in one rank
* Full House - three of a kind and a pair
* Flush - all same suit
* Straight - sequential ranks
* Three of a Kind
* Two pairs
* Pair
* Junk