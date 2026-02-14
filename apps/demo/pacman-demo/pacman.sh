#!/bin/bash

cat << "EOF"
 __________                                         ________
\______   \_____    ____   _____ _____    ____    /  _____/_____    _____   ____
 |     ___/\__  \ _/ ___\ /     \\__  \  /    \  /   \  ___\__  \  /     \_/ __ \
 |    |     / __ \\  \___|  Y Y  \/ __ \|   |  \ \    \_\  \/ __ \|  Y Y  \  ___/
 |____|    (____  /\___  >__|_|  (____  /___|  /  \______  (____  /__|_|  /\___  >
                \/     \/      \/     \/     \/          \/     \/      \/     \/
EOF

echo "Enter the difficulty level (1 = low, 2 = medium, 3 = high):"

read difficulty

podman build -t pacman-game .

podman run -it pacman-game --difficulty $difficulty --size-x 40 --size-y 40