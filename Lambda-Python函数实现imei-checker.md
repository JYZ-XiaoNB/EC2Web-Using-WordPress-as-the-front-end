# Lambda-Python函数实现imei-checker #
## 创建Lambda函数 ##
将python程序改为适用于Lambda函数（body做为输入值）
**注意：**
当需要安装外部import时，需要在本地创建\python\lib\python3.12\site-packages文件夹（文件夹名称要是AWS上Lambda python的版本），在该文件夹中安装库，并且压缩成layer.zip上传到lambda的layer上。
通过在Lambda测试栏修改json文件进行测试：
```
{
   "imei": "12345678901234"
}
```
## 配置API Gateway ##
在API Gateway创建新的资源，新建一个/verify-imei的目录，在下面创建方法（GET/POST）：
选择Lambda集成类型 → 选择刚才创建的Lambda函数（注意选对地区）
**注意：**如果选用了GET，需要添加映射模板
```
{
    "imei": "$input.params('imei')"
}
```

之后，编辑方法请求，不需要验证程序**无需IAM**，可以勾选上需要API密钥，确保安全性。部署资源，为阶段取名为prod，即可获取调用URL

## Postman ##
下载安装Postman
**Header设置：**
    Content-Type: application/json
**Body设置：（适用于POST）**
```
{
   "imei": "12345678901234"
}
```
**Authoriza设置：**
优于我们不使用IAM所以这里选择API Key，输入Value即可

如果是POST方法，URL直接输入https://p07m7ny5bg.execute-api.ap-southeast-1.amazonaws.com/prod/verify-imei
如果是GET方法，则输入https://p07m7ny5bg.execute-api.ap-southeast-1.amazonaws.com/prod/verify-imei?imei=123456789012345进行测试。