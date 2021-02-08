FROM fedora:latest
RUN dnf update -y && \
    dnf -y install python rpm-build copr-cli git && \
    rm -rf /var/lib/rpm/cache && dnf -y clean all

RUN useradd -ms /bin/bash builder
USER builder
WORKDIR /src
