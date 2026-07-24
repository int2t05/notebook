# Go 安全编码示例

## 基础路径验证

```go
package main

import (
    "errors"
    "io/ioutil"
    "path/filepath"
    "strings"
)

func safeReadFile(baseDir, filename string) (string, error) {
    /**
     * 安全保证：
     * 1. 使用EvalSymlinks解析符号链接后再Clean规范化
     * 2. 严格的边界检查，确保路径分隔符匹配
     * 3. 防止/app/data被/app/data2绕过
     */
    basePath, err := filepath.EvalSymlinks(baseDir)
    if err != nil {
        basePath = filepath.Clean(baseDir)
    } else {
        basePath = filepath.Clean(basePath)
    }
    
    targetPath := filepath.Join(basePath, filename)
    targetPath = filepath.Clean(targetPath)
    
    evalTarget, err := filepath.EvalSymlinks(targetPath)
    if err == nil {
        targetPath = filepath.Clean(evalTarget)
    }
    
    sep := string(filepath.Separator)
    if targetPath != basePath && 
       !strings.HasPrefix(targetPath, basePath + sep) {
        return "", errors.New("路径穿越检测")
    }
    
    rel, err := filepath.Rel(basePath, targetPath)
    if err != nil {
        return "", errors.New("路径穿越检测")
    }
    if strings.HasPrefix(rel, "..") {
        return "", errors.New("路径穿越检测")
    }
    
    content, err := ioutil.ReadFile(targetPath)
    if err != nil {
        return "", err
    }
    
    return string(content), nil
}
```

## 用户输入验证

```go
package main

import (
    "errors"
    "fmt"
    "io/ioutil"
    "path/filepath"
    "regexp"
    "strings"
)

func validateUserFilename(filename string) error {
    /**
     * 安全保证：
     * 1. 严格的白名单验证，仅允许ASCII安全字符
     * 2. 长度限制
     * 3. 禁止隐藏文件
     * 4. 正确的验证顺序
     */
    if len(strings.TrimSpace(filename)) == 0 {
        return errors.New("文件名不能为空")
    }
    
    if len(filename) > 255 {
        return errors.New("文件名过长")
    }
    
    if strings.HasPrefix(filename, ".") {
        return errors.New("不允许隐藏文件")
    }
    
    matched, err := regexp.MatchString(`^[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)?$`, filename)
    if err != nil {
        return fmt.Errorf("正则表达式错误: %w", err)
    }
    if !matched {
        return errors.New("文件名包含非法字符")
    }
    
    return nil
}

func safeUserFileAccess(baseDir, userInput string) (string, error) {
    if err := validateUserFilename(userInput); err != nil {
        return "", err
    }
    
    basePath, err := filepath.EvalSymlinks(baseDir)
    if err != nil {
        basePath = filepath.Clean(baseDir)
    } else {
        basePath = filepath.Clean(basePath)
    }
    
    targetPath := filepath.Join(basePath, userInput)
    targetPath = filepath.Clean(targetPath)
    
    evalTarget, err := filepath.EvalSymlinks(targetPath)
    if err == nil {
        targetPath = filepath.Clean(evalTarget)
    }
    
    sep := string(filepath.Separator)
    if targetPath != basePath && 
       !strings.HasPrefix(targetPath, basePath + sep) {
        return "", errors.New("路径穿越检测")
    }
    
    rel, err := filepath.Rel(basePath, targetPath)
    if err != nil || strings.HasPrefix(rel, "..") {
        return "", errors.New("路径穿越检测")
    }
    
    content, err := ioutil.ReadFile(targetPath)
    if err != nil {
        return "", err
    }
    
    return string(content), nil
}
```
