[TOC]

# 部署

1. 下载最新镜像:

    `docker pull neo4j:latest`

2. 容器化部署
3. 配置

neo4j.conf文件内容如下 :

```shell
# Neo4j 配置示例
# 服务器模式（单机或集群）
dbms.mode=CORE

# 默认数据库
dbms.default_database=neo4j

# 允许远程访问
dbms.connector.bolt.enabled=true
dbms.connector.bolt.listen_address=0.0.0.0:7687

# HTTP 访问
dbms.connector.http.enabled=true
dbms.connector.http.listen_address=0.0.0.0:7474

# HTTPS 访问（如果启用）
dbms.connector.https.enabled=false

# 内存管理
dbms.memory.pagecache.size=512M
dbms.memory.heap.initial_size=512M
dbms.memory.heap.max_size=1G

# 认证设置（默认启用）
dbms.security.auth_enabled=true

# 允许 Cypher 远程查询
dbms.security.allow_csv_import_from_file_urls=true

# 日志级别
server.directories.logs=/logs
# 设置调试日志级别
server.logs.debug.enabled=true
server.logs.debug.level=INFO

# 查询日志（记录长时间运行的查询）
db.logs.query.enabled=true
db.logs.query.threshold=100ms

# HTTP API 日志
dbms.logs.http.enabled=true

# JVM 垃圾回收日志
server.logs.gc.enabled=true




# 备份路径
dbms.backup.address=0.0.0.0:6362

```

docker file 如下:

```dockerfile
FROM neo4j:latest
# 复制自定义配置（如果有）
RUN mkdir -p /var/lib/neo4j/conf
RUN mkdir -p /var/lib/neo4j/import
COPY neo4j.conf /var/lib/neo4j/conf/
EXPOSE 7474 7687 6362
CMD ["neo4j"]
```

docker-compose.yml

```yaml
services:
  neo4j-pre-inquiry-bone-local:
    build:
      context: .
      dockerfile: Dockerfile
    image: neo4j-pre-inquiry-bone-local:latest
    container_name: neo4j-pre-inquiry-bone-local
    restart: always
    user: "7474:7474"
    environment:
      - NEO4J_AUTH=neo4j/neo4j@gkry
      - NEO4J_dbms_memory_pagecache_size=512M
      - NEO4J_dbms_memory_heap_initial__size=512M
      - NEO4J_dbms_memory_heap_max__size=1G
    ports:
      - "37474:7474"
      - "37687:7687"
      - "36362:6362"
    volumes:
      - /data/neo4j/bone-local/data:/data
      - /data/neo4j/bone-local/logs:/logs
      - /data/neo4j/bone-local/conf:/var/lib/neo4j/conf
      - /data/neo4j/bone-local/import:/var/lib/neo4j/import

```

拉起镜像:

在docker-compose.yml文件所在目录执行如下命令:

`docker compose up -d --build`

停止镜像:

在docker-compose.yml文件所在目录执行如下命令:

`docker compose down`

# 导入数据



# 连接

1. 浏览器连接(推荐)

    ![image-20250603144427350](https://hjw2727img.oss-cn-nanjing.aliyuncs.com/images/image-20250603144427350.png)
    
2. cypher-shell 连接
   
    ```shell
    cypher-shell -u neo4j -p neo4j@gkry -a bolt://192.168.0.188:17687 "match(n) return count(n);"
    ```
    
    ![image-20250603145150321](https://hjw2727img.oss-cn-nanjing.aliyuncs.com/images/image-20250603145150321.png)
    
2. 直接使用curl连接
       

    ```shell
    curl -u neo4j:neo4j@gkry -X POST http://127.0.0.1:27474/db/neo4j/tx/commit   -H "Content-Type: application/json"   -d '{"statements": [{"statement": "MATCH (n) RETURN COUNT(n) AS nodes"}]}'
    ```



# 使用

neo4j中有两个概念:**node**和**relationship**

先上图

```cypher
match(d:Disease {name:"股骨干骨折"}) -[r:HAS_SYMPTOM] ->(s:Symptom) return d, r,s;
```

![image-20250626105748355](https://hjw2727img.oss-cn-nanjing.aliyuncs.com/images/image-20250626105748355.png)



1. node(实体),对应上图中的红色或者紫色的圆圈

    - node有label,表示不同标签的,图中有两类node: Disease 和 Symptom

    - node 有属性(property),图中右边可见'股骨干骨折' 这个node有4个property:

      - elementId: 自动自成,相当于node的uuid,但是用的时候要用elementId()方法调用

        例如查询如下

        ```cypher
        match(d:Disease ) where elementId(d)='4:a3f5d0c0-e785-4377-b9e8-021c7761f455:0' return d;
        ```

      - id:也是自动生成,可以用来查询,

        ```cypher
        match(d:Disease ) where id(d) =0 return d;
        ```

      - name和 overview都是自定义属性,可以用来查询

        ```cypher
        //通过where条件查询
        match(d:Disease ) where d.name='股骨干骨折' return d;
        //通过filter 查询
        match(d:Disease {name:"股骨干骨折"} ) return d;
        ```

2. relationship 对应上图中的线

    有一个label即:HAS_SYPMTOM

    属性中只有自动生成的elementId和id

    查询语法如下

    ```cypher
    match (d)-[r:HAS_SYMPTOM ] ->(s) where id(r)=9 return d,r,s;
    ```

    ![image-20250626111419171](https://hjw2727img.oss-cn-nanjing.aliyuncs.com/images/image-20250626111419171.png)

    

    

语法理解:

以如下语法为例:

```cypher
match(d:Disease {name:"股骨干骨折"}) -[r:HAS_SYMPTOM] ->(s:Symptom) return d, r,s;
```

总体结构如下:

`match () -[] -> () return ;`

1. 以match开头

2. 圆括号内()是node,圆括号内文本为  d:Disease {name: ""} 

   1. d 自定义的可以换成di,do,diabllo等随意,但是后面的return的时候会用到
   2. Disease是node的label,表示要查询哪一类node
   3. {}内是属性,写法类似JSON格式,注意id和elementId无法通过这个方式使用

3. `- [] ->`表示关系,- 和->是关系的方向

   例如我这边定义的是疾病 HAS_SYMPTOM 症状

   也可以建立反向的关系,例如 症状 INDICATE 疾病

   另外[]内,r也是自定义的标识符,同理return会用到,冒号后面的label是关系类别,例如我的数据库中还有另一种关系HAS_CAUSE,查询语句为:`match (di:Disease {name:"股骨干骨折"} )-[r:HAS_CAUSE ] ->(s) RETURN di,r,s;`

4. where是条件查询,类似关系数据库(mysql)的where语句,不解释

5. return后面是要显示的结果,可以用as,和count,distinct等方法

   例如我想要查询症状最多的疾病的语句如下:

   ```cypher
   match (d:Disease) -[r:HAS_SYMPTOM] ->(s:Symptom) return distinct d.name as disease_name ,count(s) as sypmtom_num  order by sypmtom_num desc;
   ```

   ![image-20250626113913315](https://hjw2727img.oss-cn-nanjing.aliyuncs.com/images/image-20250626113913315.png)

其他增删改一般导入后使用较少,感兴趣的可以[Neo4j documentation - Neo4j Documentation](https://neo4j.com/docs/)



# 附录

docker配置国内镜像源:

/etc/docker/daemon.json

```json
{
    "registry-mirrors": [
        "https://docker.registry.cyou",
        "https://docker-cf.registry.cyou",
        "https://dockercf.jsdelivr.fyi",
        "https://docker.jsdelivr.fyi",
        "https://dockertest.jsdelivr.fyi",
        "https://mirror.aliyuncs.com",
        "https://dockerproxy.com",
        "https://mirror.baidubce.com",
        "https://docker.m.daocloud.io",
        "https://docker.nju.edu.cn",
        "https://docker.mirrors.sjtug.sjtu.edu.cn",
        "https://docker.mirrors.ustc.edu.cn",
        "https://mirror.iscas.ac.cn",
        "https://docker.rainbond.cc"
    ],
    "runtimes": {
        "nvidia": {
            "args": [],
            "path": "nvidia-container-runtime"
        }
    }
}
```

