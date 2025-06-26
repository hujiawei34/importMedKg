#!/bin/bash
cwd=$(cd $(dirname $0);pwd)
cd $cwd

# 停止并删除容器
docker compose down

# 启动容器
docker compose up -d --build
docker ps --filter "name=neo4j-pre-inquiry-bone-local"
docker logs --tail 50 neo4j-pre-inquiry-bone-local