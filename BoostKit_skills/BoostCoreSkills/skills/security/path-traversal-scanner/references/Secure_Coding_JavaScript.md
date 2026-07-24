# JavaScript (Node.js) 安全编码示例

## 基础路径验证

```javascript
const path = require('path');
const fs = require('fs');

function safeReadFile(baseDir, filename) {
    /**
     * 安全保证：
     * 1. 使用resolve()规范化路径
     * 2. 严格的边界检查，确保路径分隔符匹配
     * 3. 防止/app/data被/app/data2绕过
     */
    const basePath = path.resolve(baseDir);
    const targetPath = path.resolve(baseDir, filename);
    
    if (targetPath !== basePath && 
        !targetPath.startsWith(basePath + path.sep)) {
        throw new Error('路径穿越检测！');
    }
    
    const relative = path.relative(basePath, targetPath);
    if (relative.startsWith('..') || path.isAbsolute(relative)) {
        throw new Error('路径穿越检测！');
    }
    
    return fs.readFileSync(targetPath, 'utf8');
}
```

## 用户输入验证

```javascript
const path = require('path');
const fs = require('fs');

function validateUserFilename(filename) {
    /**
     * 安全保证：
     * 1. 严格的白名单验证，仅允许ASCII安全字符
     * 2. 长度限制
     * 3. 禁止隐藏文件
     * 4. 正确的验证顺序
     */
    if (!filename || filename.trim().length === 0) {
        throw new Error('文件名不能为空');
    }
    
    if (filename.length > 255) {
        throw new Error('文件名过长');
    }
    
    if (filename.startsWith('.')) {
        throw new Error('不允许隐藏文件');
    }
    
    const safePattern = /^[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)?$/;
    
    if (!safePattern.test(filename)) {
        throw new Error('文件名包含非法字符');
    }
    
    return filename;
}

function safeUserFileAccess(baseDir, userInput) {
    const safeFilename = validateUserFilename(userInput);
    
    const basePath = path.resolve(baseDir);
    const targetPath = path.resolve(baseDir, safeFilename);
    
    if (targetPath !== basePath && 
        !targetPath.startsWith(basePath + path.sep)) {
        throw new Error('路径穿越检测');
    }
    
    const relative = path.relative(basePath, targetPath);
    if (relative.startsWith('..') || path.isAbsolute(relative)) {
        throw new Error('路径穿越检测');
    }
    
    return fs.readFileSync(targetPath, 'utf8');
}
```

## 网络数据验证

```javascript
const path = require('path');
const fs = require('fs');

function safeNetworkFileAccess(baseDir, socket) {
    return new Promise((resolve, reject) => {
        socket.on('data', (data) => {
            try {
                const filename = data.toString('utf8');
                
                const dangerousChars = ['..', '/', '\\', '\0', '%', '\n', '\r'];
                for (const char of dangerousChars) {
                    if (filename.includes(char)) {
                        reject(new Error('文件名包含非法字符'));
                        return;
                    }
                }
                
                const basePath = path.resolve(baseDir);
                const targetPath = path.resolve(baseDir, filename);
                
                if (targetPath !== basePath && 
                    !targetPath.startsWith(basePath + path.sep)) {
                    reject(new Error('路径穿越检测'));
                    return;
                }
                
                const relative = path.relative(basePath, targetPath);
                if (relative.startsWith('..') || path.isAbsolute(relative)) {
                    reject(new Error('路径穿越检测'));
                    return;
                }
                
                resolve(fs.readFileSync(targetPath, 'utf8'));
            } catch (error) {
                reject(error);
            }
        });
    });
}
```
