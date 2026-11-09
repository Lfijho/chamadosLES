# Graphviz usa libgd ao exportar o desenho de atividades em PNG.
FROM plantuml/plantuml:1.2025.10
USER root
RUN apt-get update && apt-get install -y --no-install-recommends libgd3 && rm -rf /var/lib/apt/lists/*
USER 1000:1000
