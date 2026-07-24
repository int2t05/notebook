# Java 安全编码示例

## 基础路径验证

```java
import java.nio.file.*;
import java.io.IOException;

public String safeReadFile(String baseDir, String filename) throws IOException {
    Path basePath = Paths.get(baseDir).normalize().toAbsolutePath();
    Path targetPath = basePath.resolve(filename).normalize().toAbsolutePath();
    
    String basePathStr = basePath.toString();
    String targetPathStr = targetPath.toString();
    
    if (!targetPathStr.equals(basePathStr) && 
        !targetPathStr.startsWith(basePathStr + FileSystems.getDefault().getSeparator())) {
        throw new SecurityException("路径穿越检测！");
    }
    
    String relative = basePath.relativize(targetPath).toString();
    if (relative.startsWith("..") || relative.isEmpty()) {
        throw new SecurityException("路径穿越检测！");
    }
    
    return Files.readString(targetPath);
}
```

## 用户输入验证

```java
import java.nio.file.*;
import java.util.regex.Pattern;

public class SafeFileAccess {
    private static final Pattern SAFE_FILENAME = 
        Pattern.compile("^[a-zA-Z0-9_\\-]+(\\.[a-zA-Z0-9_\\-]+)?$");
    
    public String validateUserFilename(String filename) {
        if (filename == null || filename.trim().isEmpty()) {
            throw new IllegalArgumentException("文件名不能为空");
        }
        
        if (filename.length() > 255) {
            throw new IllegalArgumentException("文件名过长");
        }
        
        if (filename.startsWith(".")) {
            throw new IllegalArgumentException("不允许隐藏文件");
        }
        
        if (!SAFE_FILENAME.matcher(filename).matches()) {
            throw new IllegalArgumentException("文件名包含非法字符");
        }
        
        return filename;
    }
    
    public String safeUserFileAccess(String baseDir, String userinput) 
            throws IOException {
        String safeFilename = validateUserFilename(userinput);
        
        Path basePath = Paths.get(baseDir).normalize().toAbsolutePath();
        Path targetPath = basePath.resolve(safeFilename)
                                   .normalize()
                                   .toAbsolutePath();
        
        String basePathStr = basePath.toString();
        String targetPathStr = targetPath.toString();
        
        if (!targetPathStr.equals(basePathStr) && 
            !targetPathStr.startsWith(basePathStr + FileSystems.getDefault().getSeparator())) {
            throw new SecurityException("路径穿越检测");
        }
        
        String relative = basePath.relativize(targetPath).toString();
        if (relative.startsWith("..") || relative.isEmpty()) {
            throw new SecurityException("路径穿越检测");
        }
        
        return Files.readString(targetPath);
    }
}
```

## 网络数据验证

```java
import java.nio.file.*;
import java.nio.charset.StandardCharsets;

public String safeNetworkFileAccess(String baseDir, byte[] networkData) 
        throws IOException {
    String filename = new String(networkData, StandardCharsets.UTF_8);
    
    String[] dangerousPatterns = {"..", "/", "\\", "\0", "%", "\n", "\r"};
    for (String pattern : dangerousPatterns) {
        if (filename.contains(pattern)) {
            throw new IllegalArgumentException("文件名包含非法字符");
        }
    }
    
    Path basePath = Paths.get(baseDir).normalize().toAbsolutePath();
    Path targetPath = basePath.resolve(filename)
                               .normalize()
                               .toAbsolutePath();
    
    String basePathStr = basePath.toString();
    String targetPathStr = targetPath.toString();
    
    if (!targetPathStr.equals(basePathStr) && 
        !targetPathStr.startsWith(basePathStr + FileSystems.getDefault().getSeparator())) {
        throw new SecurityException("路径穿越检测");
    }
    
    String relative = basePath.relativize(targetPath).toString();
    if (relative.startsWith("..") || relative.isEmpty()) {
        throw new SecurityException("路径穿越检测");
    }
    
    return Files.readString(targetPath);
}
```

## TOCTOU竞态条件缓解（Java）

```java
import java.nio.file.*;
import java.nio.channels.*;

public String safeReadFileNoRace(String baseDir, String filename) throws IOException {
    Path basePath = Paths.get(baseDir).normalize().toAbsolutePath();
    Path targetPath = basePath.resolve(filename).normalize().toAbsolutePath();
    
    String basePathStr = basePath.toString();
    String targetPathStr = targetPath.toString();
    
    if (!targetPathStr.equals(basePathStr) && 
        !targetPathStr.startsWith(basePathStr + FileSystems.getDefault().getSeparator())) {
        throw new SecurityException("路径穿越检测！");
    }
    
    try (FileChannel channel = FileChannel.open(targetPath, StandardOpenOption.READ)) {
        Path realPath = targetPath.toRealPath();
        if (!realPath.equals(targetPath)) {
            throw new SecurityException("检测到文件替换攻击");
        }
        
        ByteBuffer buffer = ByteBuffer.allocate(1024);
        StringBuilder content = new StringBuilder();
        while (channel.read(buffer) != -1) {
            buffer.flip();
            content.append(StandardCharsets.UTF_8.decode(buffer));
            buffer.clear();
        }
        return content.toString();
    }
}
```
