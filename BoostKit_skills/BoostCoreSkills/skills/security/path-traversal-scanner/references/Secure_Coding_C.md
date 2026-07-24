# C 安全编码示例

## 基础路径验证

```c
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <stdio.h>
#include <errno.h>

int safe_read_file(const char *base_dir, const char *filename) {
    char base_real[PATH_MAX];
    char target_real[PATH_MAX];
    char target_path[PATH_MAX];
    size_t base_len;
    
    if (base_dir == NULL || filename == NULL) {
        errno = EINVAL;
        return -1;
    }
    
    if (realpath(base_dir, base_real) == NULL) {
        return -1;
    }
    
    base_len = strlen(base_real);
    
    int ret = snprintf(target_path, PATH_MAX, "%s/%s", base_real, filename);
    if (ret < 0 || ret >= PATH_MAX) {
        errno = ENAMETOOLONG;
        return -1;
    }
    
    if (realpath(target_path, target_real) == NULL) {
        return -1;
    }
    
    if (strncmp(target_real, base_real, base_len) != 0) {
        errno = EACCES;
        return -1;
    }
    
    size_t target_len = strlen(target_real);
    if (target_len > base_len && target_real[base_len] != '/') {
        errno = EACCES;
        return -1;
    }
    
    FILE *fp = fopen(target_real, "r");
    if (fp == NULL) {
        return -1;
    }
    
    // ... 读取文件内容
    
    fclose(fp);
    return 0;
}
```

## 用户输入验证

```c
#include <string.h>
#include <ctype.h>
#include <errno.h>

int validate_filename(const char *filename) {
    if (filename == NULL || *filename == '\0') {
        errno = EINVAL;
        return -1;
    }
    
    size_t len = strlen(filename);
    if (len > 255) {
        errno = ENAMETOOLONG;
        return -1;
    }
    
    if (filename[0] == '.') {
        errno = EINVAL;
        return -1;
    }
    
    // 注意：不能使用strchr(filename, '\0')，因为它永远匹配末尾空终止符
    if (strstr(filename, "..") != NULL ||
        strchr(filename, '/') != NULL ||
        strchr(filename, '\\') != NULL ||
        strchr(filename, '%') != NULL ||
        strchr(filename, '\n') != NULL ||
        strchr(filename, '\r') != NULL) {
        errno = EINVAL;
        return -1;
    }
    
    // 使用memchr检查空字节嵌入，用len-1排除末尾空终止符
    if (len > 0 && memchr(filename, '\0', len - 1) != NULL) {
        errno = EINVAL;
        return -1;
    }
    
    int dot_count = 0;
    for (const char *p = filename; *p; p++) {
        if (!isalnum((unsigned char)*p) && *p != '_' && *p != '-') {
            if (*p == '.') {
                dot_count++;
                if (dot_count > 1) {
                    errno = EINVAL;
                    return -1;
                }
            } else {
                errno = EINVAL;
                return -1;
            }
        }
    }
    
    return 0;
}
```

## 网络数据验证

```c
#include <sys/socket.h>
#include <string.h>
#include <limits.h>
#include <errno.h>

int safe_network_file_access(const char *base_dir, int sock_fd) {
    char buffer[PATH_MAX];
    ssize_t n = recv(sock_fd, buffer, sizeof(buffer) - 1, 0);
    
    if (n <= 0) {
        errno = EIO;
        return -1;
    }
    
    buffer[n] = '\0';
    
    // 注意：不能检查"\0"，因为strstr会匹配末尾空终止符
    const char *dangerous_chars[] = {"..", "/", "\\", "%", "\n", "\r", NULL};
    for (int i = 0; dangerous_chars[i] != NULL; i++) {
        if (strstr(buffer, dangerous_chars[i]) != NULL) {
            errno = EINVAL;
            return -1;
        }
    }
    
    // 使用memchr检查空字节嵌入（n是recv返回的实际字节数）
    if (memchr(buffer, '\0', n) != NULL) {
        errno = EINVAL;
        return -1;
    }
    
    if (validate_filename(buffer) != 0) {
        return -1;
    }
    
    return safe_read_file(base_dir, buffer);
}
```

## TOCTOU竞态条件缓解（C）

```c
#include <fcntl.h>
#include <unistd.h>

int safe_read_file_no_race(const char *base_dir, const char *filename) {
    // ... 路径验证代码 ...
    
    int fd = open(target_real, O_RDONLY | O_NOFOLLOW);
    if (fd < 0) {
        if (errno == ELOOP) {
            return -1;
        }
        return -1;
    }
    
    char buffer[1024];
    ssize_t n;
    while ((n = read(fd, buffer, sizeof(buffer))) > 0) {
        // 处理数据
    }
    
    close(fd);
    return 0;
}
```
