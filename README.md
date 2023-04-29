# Minotag
----
2D multiplayer tag game built using pygame and socket libraries in python
for Computer Networks course project in 4th semester.

![minotag](https://github.com/Shogunkayo/Minotag/blob/main/screenshots/home.png)

## Credits
----
- Sprites: [pixlefrog](https://pixelfrog-assets.itch.io/treasure-hunters)
- Music: [timbeek](https://timbeek.itch.io/royalty-free-music-pack-volume-2)
- Sound effects:
    - [benjaminno](https://benjaminno.itch.io/sweet-sounds-sfx-pack)
    - [obsydianx](https://obsydianx.itch.io/interface-sfx-pack-1)
    - [ellr](https://ellr.itch.io/universal-ui-soundpack)

![game](https://github.com/Shogunkayo/Minotag/blob/main/screenshots/game.png)

## Installation
----
- Install the following pip packages.
```
pip install pygame pickle bcrypt psycopg2
```

- Make sure to have postgresql installed and running on the host where you
run the server. Add your credentials in `server.py`. Else, remove the lines 
indicated in `server.py`, if you do not want a database to store user info.

## Features
---
- Multiple rooms for players to play in.
- Localized chat interfaces for each room.

![lobby](https://github.com/Shogunkayo/Minotag/blob/main/screenshots/lobby.png)
