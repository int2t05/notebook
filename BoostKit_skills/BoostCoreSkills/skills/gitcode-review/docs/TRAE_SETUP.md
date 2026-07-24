# 在trae上使用
本文档提供在trae上使用本skill的指导
## 步骤1 安装 GitCode MCP 服务器
从源码安装gitcode_mcp_server
### 克隆仓库
```
git clone https://gitcode.com/gitcode-ai/gitcode_mcp_server.git
```
### 安装依赖
```
pip install -r requirements.txt
```
### 源码安装
```
cd gitcode_mcp_server
pip install .
```

## 步骤2 在trae中配置 GitCode MCP 服务器
![image.png](https://raw.gitcode.com/user-images/assets/9298425/dd3dc38b-953a-4491-9d63-cd09783c0df8/image.png 'image.png')

**选择手动添加, 并输入以下配置**

```
{
  "mcpServers": {
    "gitcode": {
      "command": "python",
      "args": ["-m", "gitcode_mcp"],
      "env": {
        "GITCODE_TOKEN": "你的访问令牌"
      },
      "description": "GitCode MCP服务，用于与GitCode代码托管平台交互"
    }
  }
}
```

**添加成功后可以看到gitcode的server**

![image.png](https://raw.gitcode.com/user-images/assets/9298425/b06146be-a44f-4b03-9501-ca0d2e1c7468/image.png 'image.png')

## 步骤3 安装skills cli（如有可跳过）
首先安装node.js环境，并确认npm存在

`npm -v`

安装npx和skills

`npm install -g npx`
`npm install -g skills`

## 步骤4 安装gitcode-review skill

通过npx安装gitcode-review skill

`npx skills add https://gitcode.com/CarbonadoRain/gitcode-review.git`

**勾上trae，traeCN**

![image.png](https://raw.gitcode.com/user-images/assets/9298425/6d117d5a-91bb-46be-8db1-42d535ed9031/image.png 'image.png')

**按需选择**

![image.png](https://raw.gitcode.com/user-images/assets/9298425/f1b0e01c-ef61-422b-bc5e-147683310db5/image.png 'image.png')

## 步骤5 enjoy！
重启trae，可以看到skill

![image.png](https://raw.gitcode.com/user-images/assets/9298425/9d9399e3-a062-4b52-a7dc-5fd22d067ebd/image.png 'image.png')

选择Builder with MCP, 与AI用自然语言对话，即可调用skill！示例为让trae审阅Boostkit/hyperscan最新的PR

![image.png](https://raw.gitcode.com/user-images/assets/9298425/c810787d-d1be-4855-91b7-2a31dca0133c/image.png 'image.png')