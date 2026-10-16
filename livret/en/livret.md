# Guild Rush — Rulebook

*Proto version · October 16, 2026 · dungeon: the Goblin Mine*

Two guilds descend into the same dungeon. They kill monsters to take their treasure, steal each other's killing blows and plunder each other's Camp. At the end, the richest guild wins.

---

## 1. The goal

Score more treasure than your opponent. The game ends:

- at the **end of a round** in which a player has **12 treasure** or more;
- or at the **end of the turn** in which the **boss** is killed.

Most treasure wins. Tie: the boss's killer wins, otherwise whoever killed the most monsters.

## 2. Your deck

| Card | Count |
|---|---|
| **Guardian** | 1: the leader of your guild |
| **Terrain** | 1, from the Guardian's faction (your choice) |
| **Deck** | 30 cards from your faction, including **at least 20 from your Guardian's pool** |
| **Personal dungeon** | 4 monsters (2 **Elites**, 2 normal, 1 copy each, **9 treasure max** in total) and 1 boss |

- 3 copies max per card, only 1 for a **Signature**.
- A Guardian's **pool**: its 10 units and 3 spells.
- Three factions: **Drunkards** (the Tavern), **Druids** (the Forest), **Mages** (the Circle). Each has 3 Guardians.

## 3. The board

```
          Exp. 1   Exp. 2   Exp. 3   Exp. 4      ← opponent        [Opponent's Camp]
         ┌───────┬────────┬────────┬───────┐
 Dungeon │Room 1 │ Room 2 │ Room 3 │Room 4 │     monster deck · boss · defeated
         └───────┴────────┴────────┴───────┘
          Exp. 1   Exp. 2   Exp. 3   Exp. 4      ← you             [Your Camp]
```

- **Rooms**: 4 in a row, each with a monster. Adjacent = number ±1.
- **Expeditions**: one per room per player, facing the room. **3 units max** (tokens included).
- **Camp**: your fall-back and healing zone, outside the dungeon. It touches all your Expeditions, has no unit limit and is never a room. Your Guardian lives there.
- Your **Terrain** is placed in an Expedition. Its room is your **Tavern / Forest / Circle**. The card is double-sided: the front, visible in play, shows its HP and passives; the back gives its menu (pints, recipes or Incantations).

## 4. Setup

1. Randomly determine the first player. The second player chooses one of the 2 bosses brought; it waits beside the dungeon and its **Reign** applies from now on.
2. Shuffle face down the players' 8 monsters and the 2 Mine monsters (Goblin Sapper, Mimic Minecart). Place 1 in each room; the other 6 form the monster deck.
3. Each player places their Guardian in their Camp and their Terrain beside it, shuffles their deck and draws **5 cards**.
4. At the 1st Assault, each player places their Terrain in the Expedition of their choice.

## 5. The turn

A **round** = one turn for each player. Your turn has 4 phases:

| Phase | What happens |
|---|---|
| **1. Rest** | Energy to max, draw 1, heal Recovering units, Guardian passive. |
| **2. Scheme** | Place your Scouts and your face-down cards (Bluff), break camp if you want. |
| **3. Assault** | Play, move, fight room by room, then 1 raid max. |
| **4. Withdrawal** | Count your treasure, your Terrain levels up. |

**Energy**: 3 in round 1, +1 per round, 6 max. Energy you don't spend stays until your Rest: it pays for your Reflexes on your opponent's turn.

At the start of each turn, empty rooms receive the next monster (the boss when the monster deck is empty).

## 6. The Assault

### Playing and moving

- A unit you play arrives **directly** in the Expedition you choose or in your Camp.
- A unit already in play moves **once per turn**: to an adjacent Expedition or to the Camp, or from the Camp to any Expedition.
- A **Wounded** unit can only go to the Camp, where it becomes **Recovering**.
- **Entering** a room (playing, moving, returning from the Camp) triggers Traps, Glyphs and "enters" effects.

### Fighting

**In short: Declare, Duel, then Monster → You → Them.** The monster always strikes first, unless a card says otherwise.

Attacking is **optional**: being in a room without attacking triggers nothing. You fight **room by room**, in any order; one combat ends before the next begins. Between two combats you can still play and move units.

1. **Declare.** Choose your attackers in this room (and at **Reach** from a neighboring one) and, for **each one**, its target: the monster, an enemy unit or the enemy Terrain in the room (**Protector** applies). A Stunned unit can be declared: it won't strike.
2. **Duel.** Your opponent goes first: a **Reflex** card, a bonus from their Terrain if it is in this room, or pass. Then you, and so on. Two passes in a row: the Duel is over.
3. **The monster strikes** 1 of your **present** attackers, **chosen by your opponent** (Protector applies). It strikes even if you attack another target. Units at Reach are not present.
4. **Your attackers all strike at the same time.** Those that are dead or Stunned don't strike. Damage = Power.
5. **Brawl**, only if your opponent has units in their Expedition facing this room: each one strikes once at the target of its choice (your units, your Terrain or the monster). If some strike the monster, it first strikes back at 1 of them, chosen by you.

Each unit strikes **once per player turn**: a unit that struck in a Brawl during your turn can still attack on its own turn. **Swift**: after its combat, the unit may change rooms and attack once more.

> **Example.** Room 2: a Goblin Snoop (2/3, 1 treasure). You have Drunken Soldier (4/4) and Barmaid (1/3) in your Exp. 2; your opponent has a Wolf Cub (2/1) in theirs.
> 1. You declare: Drunken Soldier → Goblin, Barmaid → Wolf Cub.
> 2. Duel: your opponent passes, you pass.
> 3. The Goblin strikes: your opponent picks the Barmaid (2 damage, she has 1 HP left).
> 4. Your strikes: Drunken Soldier deals 4 damage to the Goblin (dead), Barmaid deals 1 to the Wolf Cub (dead). You take the treasure.
> 5. Brawl: the Wolf Cub is dead, it doesn't strike.

### The killing blow

A monster's **killer** is the player who controls the source of the last damage (unit, spell, Terrain). They take **all** of the monster's treasure, and its relic if it has one. In a Brawl, the kill can be stolen.

**Fall back**: if your opponent kills the monster during a Brawl, your units that attacked may return to the Camp (not if Snared).

### Spells

- A spell is cast in a room where you have a **unit** (your Terrain doesn't count). With **Reach**: also an adjacent room.
- Without **Reflex**, a spell is played during your Assault, outside a Duel. With Reflex, it is played in a Duel, even on your opponent's turn.

## 7. Damage and healing

- Damage **stays** on the card until healed. At 0 HP, the unit dies (Terrain: destroyed; Guardian: Knocked out).
- **Bonus HP** (+X HP, +X/+X) takes damage first and disappears with the buff.
- **Wounded**: at least 1 damage on its base HP. It can only move to the Camp.
- **Recovering**: a wounded unit that reached the Camp is fully healed at your next Rest, then stays in the Camp until the end of that turn.

## 8. The dungeon

- Each monster has **treasure** (gold dot). An **Elite** also carries a **relic**.
- **Ambush**: effect when the monster arrives.
- Damage on a monster stays from one turn to the next.
- Monsters don't evolve.
- A monster gives its owner no advantage: treasure and relic go to the killer, whoever it is.
- The **boss** enters when the monster deck is empty. Its **Reign** works from setup. Killing it ends the game at the end of the turn.

**Prototype**: until decks have their monsters, play with the 10 Mine monsters and Grombak (Reign: monsters in play have +1 HP).

**Mine relics**: Miner's Lantern (look at the next monster), Rune Pickaxe (+2 PWR on your first monster attack), Foreman's Purse (+1 treasure if you killed this turn).

## 9. The raid

The raid strikes the opponent's Camp to steal treasure.

1. **Condition**: from round 2, during your Assault, 1 raid max. One of your units has just killed, in this room, the monster or the last enemy unit.
2. **Departure**: your standing units in this room go to the opponent's Camp (not Snared ones).
3. **Recall**: the defender brings back to the Camp any Expedition units they want (not Snared ones).
4. **Effects**: Reinforce and Camp Defense, defender first.
5. **Raid Brawl**, with no monster: a Duel, then each raider strikes (Protector first, Guardian next), then each standing defender strikes a raider.
6. **Result**: successful if **more raiders than standing defenders** remain (Guardian included). Tie: the defender wins.
7. **Loot**: 1 treasure stolen, **+1 if the Guardian is Knocked out** (2 max).

After the raid, the wounded on both sides become Recovering, the dead are discarded, and your raiders return to your Camp.

## 10. The Terrain

- It has HP, doesn't strike and doesn't block raids. An enemy unit fighting in its room can attack it.
- **Bonuses**: during your Assault, or during any Duel in its room (even on your opponent's turn). They target your units in the room.
- **Level**: Lvl 1 when placed, +1 at Withdrawal if it hasn't moved (3 max). At Lvl 3, it's a **Stronghold**: +1 treasure per monster killed in its room by your units or spells.
- **Break camp** (Scheme): move it to an adjacent Expedition; it loses 1 level.
- **Destroyed**: it returns at Lvl 1 at your next Assault. If your opponent destroyed it, they gain +1 treasure (**plunder**).

## 11. The Treasure map

The catch-up mechanic. At the end of round 1, it goes to the Camp of the player with the least treasure (tie: the second player). At each Withdrawal, its holder gains **+1 treasure if behind**. A successful raid can take it instead of the 1st stolen treasure.

---

## 12. The guilds

### Drunkards — the Tavern
Brawling and big bodies around the barrel. **Pint**: the barrel loses HP to make a unit in its room drink (2 pints per turn, 3 at Lvl 2).

| Cost | Drinks |
|---|---|
| 1 HP | Beer +1 PWR · Cider +2 HP · Mead heals 2 |
| 2 HP | Rum +2 PWR then Hangover · Whisky Unflinching · Absinthe +3 PWR then Backlash |

Mixing: 2 drinks in the same turn = Stunned. **Soak**: once per turn, the barrel takes a hit instead of a unit in its room. **Last round** (once per game): the pint empties the barrel, which explodes.

| Guardian | Style | Terrain |
|---|---|---|
| **Guss the Innkeeper** (3/7) | Balanced: Daily Special, defenders +1 PWR | Oak Barrel (Aura +1 PWR) |
| **Rosa the Brewer** (2/7) | Zone: On the House, 1 damage to raiders | Explosive Barrel (Counter) |
| **Robin the Gambler** (4/5) | Aggressive: Double Down, raiders +1 PWR | Betting Keg (Pot, Wagers) |

### Druids — the Forest
Numbers and summons (Sprouts, Wolves). **Sap**: tokens on the grove (4 max), +1 at Rest (+2 at Lvl 2), pay for 1 recipe per turn. **Undergrowth**: 4 units in the Forest instead of 3.

| Guardian | Style | Terrain |
|---|---|---|
| **Cernun** (2/7) | Balanced: Sap per monster killed, 2 Sprouts on defense | Ancient Grove (buffs) |
| **Belladonna** (1/6) | Zone: Brambles, Stuns on raids | Poison Grove (damage, Poison) |
| **Sylve** (2/5) | Aggressive: Nomad, Pack (Swift Wolves) | Shadow Grove (Reflex recipes) |

### Mages — the Circle
Few bodies, lots of spells: strike with Reach and take the killing blows. **Arcana**: tokens on the circle (4 max), +1 per spell cast, pay for 1 Incantation per turn. An Incantation is not a spell. Circle Lvl 1: Incantations with Reach; Lvl 2: +1 Arcana at Rest.

| Guardian | Style | Terrain |
|---|---|---|
| **Soffia** (2/6) | Balanced: draws if 2 spells in the turn | Rune Circle |
| **Orsin the Runesmith** (2/7) | Zone: Glyphs, defenders with Aegis | Rune Sanctuary (Frost, Bastion) |
| **Ignis the Pyromancer** (3/5) | Aggressive: spells +1 damage to monsters | Unstable Hearth (Overload, Pyroclasm) |

---

## 13. Keywords

| Keyword | Effect |
|---|---|
| **Arrival** | When played. |
| **Last breath** | When it dies. |
| **Combat** | During the unit's combat. |
| **Monster kill** | When it deals the blow that kills a monster. |
| **Spellcast** | When you play a Spell card. |
| **Revealed** | When its Bluff card is flipped. |
| **Withdrawal** | During your Withdrawal phase. |
| **Swift** | After its combat during your Assault, changes rooms (outside the limit) and attacks once more. |
| **Reflex** | Playable in a Duel. |
| **Reach** | Attacks a room adjacent to its Expedition. The monster doesn't strike back; the unit is not present in the room (no Brawl, no Stronghold, no Fall back). Respects Protector. |
| **Protector** | Attacks (units and monsters) against your units or your Terrain in its room must target it. Spells and effects target freely. Protects even when Stunned; in a raid, goes before the Guardian. |
| **Reinforce** | When the unit is recalled to the Camp during a raid. |
| **Scout** | Placed during the Scheme in the Expedition you choose, doesn't move again this turn. Its "Scheme:" effect repeats at each of your Schemes. |
| **Bluff** | Placed face down during the Scheme, revealed at the Assault. |
| **Try your luck** | Reveal the top card of your deck, then put it on the bottom. Success if its cost is 2 or more. |
| **Ambush** | Monster: effect when it arrives. |
| **Signature** | 1 copy max per deck. |
| **Token** | Summoned unit (Sprout 1/1, Wolf 2/1). Counts toward the limit of 3. Full Expedition: no summon. |

**Enemy**: an opposing unit, Guardian or Terrain; a monster is never an enemy. **Target**: anything, monsters included.

## 14. Conditions

| Condition | Effect |
|---|---|
| **Stunned** | Doesn't strike in its next combat (its current attack is cancelled). |
| **Poisoned** | -1 HP at each of its owner's Rests, until healed. |
| **Snared** | Can't change rooms. |
| **Unflinching** | Can't be Stunned this turn. |
| **Tipsy** | Drank this turn; a 2nd drink = Stunned. |
| **Hangover** | Stunned until the end of your next turn. |
| **Backlash** | -2 HP at your next Rest. |
| **Recovering** | Wounded in the Camp: fully healed at your next Rest, then stays in the Camp that turn. |
| **Knocked out** | Guardian at 0 HP: no longer defends, returns at its next Rest with full HP. |
| **Aegis** | Ignores the next hit received, then disappears. Doesn't stack; doesn't block HP loss. |
| **Trap** | Face down, placed by a Scout (1 per player per room). Hits the 1st enemy unit that enters. A **Decoy** is a fake Trap. |
| **Glyph** | Face up, placed by a Mage (2 max per player per room). The 1st enemy unit that enters or attacks here (Reach included) takes 1 damage and is Stunned. 1 Glyph per unit per turn. |
| **Wager** | On the Betting Keg (3 max), +1 per monster killed here. 3 Wagers = 1 treasure at Withdrawal. |
