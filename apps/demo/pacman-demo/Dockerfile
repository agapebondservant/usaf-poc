FROM python:2.7-buster

WORKDIR /app

RUN sed -i 's/deb.debian.org/archive.debian.org/g' /etc/apt/sources.list && \
  sed -i 's|security.debian.org/debian-security|archive.debian.org/debian-security|g' /etc/apt/sources.list && \
  sed -i '/buster-updates/d' /etc/apt/sources.list

RUN apt-get update -o Acquire::Check-Valid-Until=false && \
  apt-get install -y --no-install-recommends git && \
  rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/ParthKolekar/pacman-game.git .

RUN pip install --no-cache-dir .

ENTRYPOINT ["pacman-game"]
CMD ["--difficulty", "1", "--size-x", "20", "--size-y", "20"]