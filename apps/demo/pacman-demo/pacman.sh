#!/bin/bash

cat << "EOF"
 __________                                         ________
\______   \_____    ____   _____ _____    ____    /  _____/_____    _____   ____
 |     ___/\__  \ _/ ___\ /     \\__  \  /    \  /   \  ___\__  \  /     \_/ __ \
 |    |     / __ \\  \___|  Y Y  \/ __ \|   |  \ \    \_\  \/ __ \|  Y Y  \  ___/
 |____|    (____  /\___  >__|_|  (____  /___|  /  \______  (____  /__|_|  /\___  >
                \/     \/      \/     \/     \/          \/     \/      \/     \/
EOF

podman build -t pacman-game .

echo "Enter the difficulty level (1 = low, 2 = medium, 3 = high):"

read difficulty

echo "INSTRUCTIONS: To play the game, hit ENTER, then use the following keys
 to navigate:
 w = UP
 a = LEFT
 s = DOWN
 d = RIGHT
 q = QUIT"

podman run -it pacman-game --difficulty $difficulty --size-x 20 --size-y 20
