FROM neo4j:latest



# 复制自定义配置（如果有）
RUN mkdir -p /var/lib/neo4j/conf
RUN mkdir -p /var/lib/neo4j/import
COPY neo4j.conf /var/lib/neo4j/conf/


EXPOSE 7474 7687 6362
CMD ["neo4j"]
