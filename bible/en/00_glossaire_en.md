# Guild Rush — Glossary (EN)
Translation of `bible/00_glossaire.md`, which remains the reference. One line per term.
<!-- fr_sha1: e122ddbd166877d8c1900e91fa13add160cb8fab (00_glossaire.md traduit) -->

## Structure
- **Round**: one turn of each player. **Turn**: Rest → Scheme → Assault → Withdrawal.
- **Room**: a monster's slot in the center. 4 rooms in a row (1-2-3-4): neighbor = number ±1, distance = difference of numbers.
- **Expedition**: your zone facing a room (Exp. 1-4), same neighbors as its room. 3 units max, tokens included.
- **Camp**: your fallback and healing zone, targeted by raids. Touches all your Expeditions; it isn't a room (not a neighbor, not Reach, not Glyph). No unit limit.
- **Enter**: arrive in a room (play, move, return from the Camp).
- **Elite**: a stronger monster that carries a relic. Doesn't evolve.
- **Reign**: a boss's effect, active from setup until its death.
- **Tavern / Forest / Circle**: the room where your Terrain is (barrel / grove / circle).

## Phases
- **Rest**: energy to max, draw 1, heal Recovering units, Guardian passive.
- **Scheme**: Scouts, face-down cards, break camp.
- **Assault**: play, move, attack room by room, then 1 raid max.
- **Withdrawal**: count treasure, Terrain level up.

## Combat
- **Combat**: your attackers in a room against their targets. The monster strikes 1 attacker (chosen by the opponent), then your attackers together, then (Brawl) the enemy units. 1 strike per unit per turn; damage = Power. Being in a room without attacking triggers nothing.
- **Duel**: opened by each combat, before the strikes. The opponent answers first, then Reflex card / Terrain bonus / pass. 2 passes = strikes.
- **Brawl**: both players in the same room. Order: monster, active player, opponent. The killing blow takes everything.
- **Fall back**: if the opponent kills the monster during a Brawl, a unit that attacked may return to the Camp (not if Snared).
- **Raid**: after a success in a room, your units in that room attack the enemy Camp (1 per Assault, from round 2). Success = treasure stolen.
- **Plunder**: destroying the enemy Terrain = +1 treasure.
- **Enemy**: enemy unit, Guardian or Terrain. A monster is never an enemy. **Target**: any unit, Guardian, Terrain or monster, on either side.
- **Duration**: tag at the end of an effect. [turn]: end of the current turn, even the opponent's. [combat]: end of that combat. [raid]: end of that raid. [Rest]: your next Rest. [next turn]: end of its owner's next turn. [1 hit]: until it is used. No tag: instant or permanent. Every "X per turn" resets each turn, yours and your opponent's.

- **Damage**: stays on the card (tokens) until healed. At 0 HP: death (Terrain: destroyed; Guardian: Knocked out).
- **Bonus HP**: HP buffs (+X HP, +X/+X) take damage first and disappear when the buff ends. Damage they absorb doesn't stay.
- **Wounded**: unit with at least 1 damage on its base HP. Normal movement: only toward the Camp.
- **Heal X**: removes X damage. "Fully healed": removes all damage.

## Cards
- **Guardian**: guild leader (1 per deck), Rest and Camp defense passives. Its **pool**: its 10 units + 3 own spells.
- **Terrain**: barrel (Drunkards), grove (Druids) or circle (Mages). HP, doesn't strike, levels 1-3.
- **Level**: Lvl 1 when placed; +1 at Withdrawal if it didn't move since your last Withdrawal (max 3). Lvl 3 = **Stronghold** (+1 treasure / monster killed here by your units or your spells).
- **Break camp**: move the Terrain to a neighboring Expedition (-1 level). Once per Scheme.
- **Signature**: 1 copy max per deck.
- **Token**: summoned unit (Sprout 1/1, Wolf 2/1), counts toward the limit of 3. Full Expedition: no summon.
- **Camp defense**: effect that applies when your Camp is raided, at the Effects step of the raid.
- **In its room / In the Tavern…**: continuous effect, active while the condition is true.

## Keywords
- **Arrival**: when you play it from your hand (not a token). **Last breath**: on death. **Combat**: at the Declare step of a combat where it attacks, is attacked or strikes in a Brawl, [combat]. **Monster kill**: when it deals the blow that kills a monster. **Spellcast**: when you play a Spell card (an Incantation isn't one). **Revealed**: when its Bluff card is turned over. **Withdrawal**: at your Withdrawal phase.
- **Swift**: after its combat on your Assault, the unit may change room (outside the movement limit) and attack 1 more time.
- **Reflex**: playable in a Duel, as well as on your Assault. Without Reflex, a spell is played only on your Assault, outside a Duel.
- **Reach**: the unit can attack in a room neighboring its Expedition; the monster doesn't strike back; it doesn't count as present in that room (no Brawl, no Stronghold, no Fall back). Respects Protector. On a spell: it can target a room neighboring one of your units.
- **Reinforce**: triggers when the unit is called back to the Camp during a raid.
- **Protector**: an attack (unit or monster) against your units or your Terrain in its room must target it. Spells, effects and Ambushes target freely. Protects even when Stunned; in a raid, comes before the Guardian.
- **Scout**: played at Scheme, directly in the chosen Expedition, and doesn't change room this turn. Its "Scheme:" effect triggers again at each of your Schemes while it is in an Expedition.
- **Bluff**: placed face down in an Expedition at Scheme, revealed at the start of your Assault. While hidden, it counts toward the limit of 3 but can't be attacked or targeted.
- **Try your luck**: reveal the top card of your deck, then put it at the bottom of your deck. Success if its cost is 2 or more. Empty deck: failure.
- **Ambush** (monster): effect when it fills an empty room at the start of a turn (not at setup).

## States (tokens)
- **Stunned**: doesn't strike in its next combat (attack or Brawl), then the token goes away; with no combat: [next turn]. Stunned during its attack: that attack is canceled. Stunned monster: doesn't strike or strike back [turn].
- **Poisoned**: -1 HP at each of its owner's Rests, until healed. At Rest, poison applies before healing.
- **Swift**: has the Swift keyword [turn].
- **Unflinching**: can't be Stunned [turn] (Whisky).
- **Tipsy**: drank a drink (a 2nd = Stunned) [turn].
- **Hangover**: Stunned [next turn] (Rum).
- **Backlash**: -2 HP at your next Rest (Absinthe).
- **Snared**: can't change room [next turn] (Web, Gatekeeper: while the source is in the room).
- **Recovering**: wounded unit that arrived at the Camp. Fully healed at your next Rest, then stays at the Camp until the end of that turn.
- **Knocked out**: Guardian at 0 HP, no longer defends; comes back at its next Rest (HP to max).
- **Trap**: face-down token set by a Scout on its room (1 per player per room, outside the limit of 3). Triggers on the 1st enemy unit that enters the room (tokens included), then discarded.
- **Wager**: token on the Betting Keg (3 max), gained per monster killed here. 3 Wagers = 1 treasure at Withdrawal. Lost if the barrel explodes.
- **Decoy**: Trap with no effect, set instead of the real one to bluff.
- **Aegis**: ignores the next hit received (all its damage, from one source) [1 hit]. Doesn't stack. Doesn't block HP losses (Poisoned, Backlash).
- **Glyph**: face-up token placed by a Mage on a room (2 max per player per room, outside the limit of 3). The 1st enemy unit that enters the room or attacks in it (Reach included) takes 1 damage and is Stunned, then a Glyph is removed. Only 1 Glyph triggers per unit per turn.

## Resources
- **Energy**: 3 in round 1, +1 per round, max 6. Unspent energy stays until your Rest (Reflexes on the opponent's turn).
- **Pint** (Drunkards): -1 HP to the barrel (-2 strong drink) → effect on a unit.
- **Soak** (Drunkards): once per turn, the barrel takes all the damage of one hit instead of one of your units in its room.
- **Sap** (Druids): tokens on the grove (4 max), pay for recipes.
- **Arcana** (Mages): tokens on the circle (4 max), +1 per spell you cast, pay for Incantations. An Incantation isn't a spell. **Overload** (Unstable Hearth): up to 6, each token above 4 deals 1 damage to the circle at your Rest.
- **Treasure**: score. Game ends at 12 at the end of a round, or when the boss is killed (end of the turn). Most treasure wins.
- **Treasure map**: comeback, +1 treasure at Withdrawal if you're behind. Can be stolen by a raid.
