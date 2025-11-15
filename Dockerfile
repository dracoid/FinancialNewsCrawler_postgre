FROM ubuntu:latest
LABEL authors="dracoid"

ENTRYPOINT ["top", "-b"]