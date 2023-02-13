FROM neo4j:latest

RUN mkdir -p plugins

COPY --chown=neo4j:neo4j /plugins/apoc-5.3.1-extended.jar plugins/
COPY --chown=neo4j:neo4j /plugins/neo4j-graph-data-science-2.2.6.jar plugins/
COPY --chown=neo4j:neo4j /plugins/neosemantics-5.1.0.0.jar plugins/

RUN echo "dbms.security.procedures.unrestricted=apoc.*,gds.*,neosemantic.*" >> conf/neo4j.conf
RUN echo "dbms.unmanaged_extension_classes=n10s.endpoint=/rdf" >> conf/neo4j.conf


EXPOSE 7474 7473 7687

CMD ["neo4j"]


# docker run --name neo4j -p 7474:7474 -p 7473:7473 -p 7687:7687 -e NEO4J_AUTH=neo4j/password -e NEO4J_dbms_security_auth__enabled=true mon_image_neo4j:latest
