cwd=$(cd $(dirname $0);pwd)
cd $cwd

# 停止并删除容器
docker compose down
