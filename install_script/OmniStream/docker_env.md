
# Docker搭建开发环境指南

## 一 安装docker并导入OS镜像
### docker安装
离线安装的话可以网上搜教程
推荐直接直接yum install -y docker安装

### OS镜像导入
```
wget --no-check-certificate https://mirrors.huaweicloud.com/openeuler/openEuler-22.03-LTS-SP4/docker_img/aarch64/openEuler-docker.aarch64.tar.xz
docker load -i openEuler-docker.aarch64.tar.xz
```

## 二 启动容器
提前查询物理机上的需要使用的端口有没有被占用
```
ss -tuln | grep -E "30111|30112|30113|30114|30115|30116"
```
执行下列命令启动启动（容器名、端口和宿主机上的目录自行调整）：

- 30111用于打开Flink的WebUI，浏览器访问 ip:30111 【可能需要关闭宿主机防火墙，命令：systemctl stop firewalld】
- 30112用于ssh连接
- 30113-30116用于远程Debug或其他
- 将宿主机上/home/${CONTAINER_NAME}挂载到了容器的/home目录、/home/${CONTAINER_NAME}/opt挂载到容器的/opt目录
```
CONTAINER_NAME=xyw_flink
docker run -itd --name $CONTAINER_NAME --hostname $CONTAINER_NAME --privileged=true -p 0.0.0.0:30111:8081 -p 0.0.0.0:30112:22 -p 0.0.0.0:30113:9993 -p 0.0.0.0:30114:9994 -p 0.0.0.0:30115:9995 -p 0.0.0.0:30116:9996 -v /home/${CONTAINER_NAME}:/home/ -v /home/${CONTAINER_NAME}/opt:/opt openeuler-22.03-lts-sp4 /bin/bash
```
以登录模式进入容器命令行
```
docker exec -u 0 -it ${CONTAINER_NAME} /bin/bash --login
```

## 三 基础配置
### 宿主机执行
因为容器内没有守护进程，需要直接配置coredump文件生成的路径
需要注意的是，/proc/sys/kernel/core_pattern是容器和宿主机共享的，这里会导致宿主机和所有容器的coredump生成目录都被修改
并且修改后生成的coredump没有被自动管理，磁盘空间不足时需要手动删除
```
# 默认的配置为 |/usr/lib/systemd/systemd-coredump %P %u %g %s %t %c %h
mkdir -p /home/corefile
echo "/home/corefile/core-%P-%u-%g-%s-%t-%c-%h" > /proc/sys/kernel/core_pattern
```

### 容器内执行
```
# coredump生成目录
mkdir -p /home/corefile

# OmniStream启动时的依赖库归档目录
mkdir -p /home/Dependency_library

# 忽略yum证书校验
echo "sslverify=0" >> /etc/yum.conf

# 安装基础依赖
yum install -y openssl zlib dos2unix patch maven openssh-clients openssh-server passwd vim findutils net-tools gcc cmake make gcc-c++ unzip zip wget iproute iputils file gdb boost-devel git autoconf xz perf

# 设置系统编码，避免乱码
yum install -y glibc-locale-source
localedef --no-archive -i en_US -f UTF-8 en_US.UTF-8
cat > /etc/locale.conf << EOF
LANG="en_US.UTF-8"
EOF
source /etc/profile

# 配置ssh
sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/PermitRootLogin no/PermitRootLogin yes/' /etc/ssh/sshd_config
sed -i 's#^Subsystem.*#Subsystem  sftp  /usr/libexec/openssh/sftp-server#' /etc/ssh/sshd_config
ssh-keygen -A
ssh-keygen -t rsa -f ~/.ssh/id_rsa -N "" -q

# 后台启动sshd，可用kill命令停止(ps -ef | grep /usr/sbin/sshd | grep -v grep)
# 容器重启后，需要重新执行该命令
/usr/sbin/sshd -D &
```

## 四 配置maven
打开/etc/maven/settings.xml用下面的内容替换
```
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/SETTINGS/1.2.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.2.0 https://maven.apache.org/xsd/settings-1.2.0.xsd">
    <proxies>
        <proxy>
            <id>http-proxy</id>
            <active>false</active>
            <protocol>http</protocol>
            <host>proxy.huawei.com</host>
            <port>8080</port>
            <nonProxyHosts>localhost,127.0.0.1,*.huawei.com</nonProxyHosts>
            <username>p_atlas</username>
            <password>proxy@123</password>
        </proxy>
        <proxy>
            <id>https-proxy</id>
            <active>false</active>
            <protocol>https</protocol>
            <host>proxy.huawei.com</host>
            <port>8080</port>
            <nonProxyHosts>localhost,127.0.0.1,*.huawei.com</nonProxyHosts>
            <username>p_atlas</username>
            <password>proxy@123</password>
        </proxy>
    </proxies>
    <mirrors>
        <mirror>
            <id>huaweicloud-maven</id>
            <name>Huawei Cloud Maven Repository</name>
            <url>https://repo.huaweicloud.com/repository/maven/</url>
            <mirrorOf>central</mirrorOf>
        </mirror>
    </mirrors>

    <pluginGroups></pluginGroups>
    <servers></servers>
    <profiles>
        <profile>
            <id>huaweicloud</id>
            <activation>
                <activeByDefault>true</activeByDefault>
            </activation>
            <repositories>
                <repository>
                    <id>huaweicloud-maven</id>
                    <name>Huawei Cloud Maven Repository</name>
                    <url>https://repo.huaweicloud.com/repository/maven/</url>
                    <releases>
                        <enabled>true</enabled>
                    </releases>
                    <snapshots>
                        <enabled>true</enabled>
                    </snapshots>
                </repository>
            </repositories>
            <pluginRepositories>
                <pluginRepository>
                    <id>huaweicloud-maven</id>
                    <name>Huawei Cloud Maven Repository</name>
                    <url>https://repo.huaweicloud.com/repository/maven/</url>
                    <releases>
                        <enabled>true</enabled>
                    </releases>
                    <snapshots>
                        <enabled>true</enabled>
                    </snapshots>
                </pluginRepository>
            </pluginRepositories>
        </profile>
    </profiles>

    <activeProfiles>
        <activeProfile>huaweicloud</activeProfile>
    </activeProfiles>
</settings>
```

## 五 【可选】个性化配置
### 命令行配置
下列配置作用：
- 显示当前路径
- 如果当前是否在容器内
- 显示当前git分支
```
cat >> ~/.bashrc << 'EOF'
RESET_COLOR='\[\033[0m\]'
RED='\[\033[1;31m\]'
GREEN='\[\033[1;32m\]'
YELLOW='\[\033[1;33m\]'
BLUE='\[\033[1;34m\]'

docker_marker() {
  if [ -f /.dockerenv ]; then
    echo "[Docker]"
  else
    echo ""
  fi
}

git_branch() {
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    return
  fi

  local branch
  branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
  if [ "$branch" = "HEAD" ]; then
    echo " $branch(detached)"
  else
    echo " $branch"
  fi
}


PS1="${GREEN}\u@\h${RED}\$(docker_marker):${BLUE}\w${YELLOW}\$(git_branch)${RESET_COLOR}\$ "
EOF

source ~/.bashrc
```