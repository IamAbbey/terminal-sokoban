# Terminal Sokoban

`sokoban` is a "graphical" command line program for playing the popular sokoban game in the terminal.

> Sokoban (倉庫番, Sōko-ban, lit. 'warehouse keeper'[1]) is a puzzle video game in which the player pushes boxes around in a warehouse, trying to get them to storage locations. The game was designed in 1981 by Hiroyuki Imabayashi, and first published in December 1982. - Wikipedia: http://en.wikipedia.org/wiki/

<img src="./demo.gif" width=800px>

## Installation

`sokoban` is only compatible with `python3`, and can be installed through `pip`.

```bash
pip3 install terminal-sokoban
```

You should then be ready to go.

## Play 
Run `sokoban` to start playing the game.

```
sokoban
```

There are over `17,991` stages.

`sokoban` has been tested to work on Linux, Mac, and Windows computers.

### Instruction

- Use the arrow keys to move the player around.

- Use the (r) key to reverse a move.

- Use the (z) key to restart a stage.

- Use the (q) key to quit the game.


## Options

Specify which stage to play

```
sokoban 7
```

## Development
- Clone repository.
- Setup poetry and install dependencies.
- Load stage data using `python script/generate.py`.
- Run Game using play instructions above.

## Credits
- [Blessed](https://github.com/jquast/blessed)
- [cursewords](https://github.com/thisisparker/cursewords)
- Levels data from http://sourcecode.se/sokoban/