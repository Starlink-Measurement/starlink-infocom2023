# hash:sha256:6f3a93666d73e5f942bee679dea3c7bdd803886b55af4a720fc2288a6104cf74
FROM registry.codeocean.com/codeocean/miniconda3:4.9.2-python3.8-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive

COPY postInstall /
RUN /postInstall
