FROM fedora:latest
RUN dnf -y install python rpm-build copr-cli git python3-devel python3-toml python3-poetry && \
    rm -rf /var/lib/rpm/cache && dnf -y clean all

RUN useradd -ms /bin/bash builder
USER builder
WORKDIR /src
