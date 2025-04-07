# EC2Web-Using-WordPress-as-the-front-end
使用AWSEC2搭建了一个网页，以wordpress做为前端，python程序为后端，编写了imei_checker的插件进行连接
# 构建EC2：imei网站 #
## 1.创建EC2 ##
1.首先创建EC2实例，注意ssh连接并保存好私钥文件，以便使用SSH远程登陆。
2.AWS的公有DNS每次运行实例都会变化，需要使用弹性IP分配给所用的EC2实例从而使IP固定不变。
3.安全组设置需要在入站添加：80，443，22端口（http,httpd,ssh）出站添加所有TCP协议（端口0~65535）
## 2.wordpress安装及配置 ##
配置环境
```
sudo yum update -y
sudo amazon-linux-extras install -y lamp-mariadb10.2-php7.2 php7.2
sudo yum install -y httpd mariadb-server
```
运行MySQL安全脚本，新建MySQL root用户的密码,之后安装wordpress并将文件复制到Apache根目录

`sudo cp -r wordpress/* /var/www/html/`

接着要为wordpress设置正确的权限：

1.将 /var/www/html/ 目录及其所有子目录和文件的所有者和所属组均改为 apache 用户和 apache 组。确保 Web 服务器有权限读取和执行这些文件（例如执行 PHP 脚本或访问静态资源）。

`sudo chown -R apache:apache /var/www/html/`

2.递归设置 /var/www/html/ 目录及其内容的权限为 755。
755：权限模式的八进制表示，具体含义如下：

目录：755 = drwxr-xr-x
所有者（apache）：rwx（读、写、执行）
所属组（apache）：r-x（读、执行）
其他用户：r-x（读、执行）

`sudo chmod -R 755 /var/www/html/`

之后为wordpress创建了一个专用的SQL数据库用以存放各种数据，通过执行`sudo vi /var/www/html/wp-config.php`存入了wordpress的数据库名称，用户以及密码
```
define('DB_NAME', 'wordpress');
define('DB_USER', 'wordpressuser');
define('DB_PASSWORD', 'your_password');
```
**注意：**
wordpress第一次打开后会将本机的域名也存入了该数据库中，由于AWS的域名会随着实例的重启而改变，所以这样会导致wordpress下次无法正常打开。这里提供了两种解决办法：
1.分配弹性ip（最为推荐，这样能固定域名）
2.为wordpress分配一个新的数据库并且修改wp-congfig.php的内容，这样就避免了重装wordpress的麻烦操作（不推荐，因为需要每次都分配一个新的，记录一下如果更换了ip可以做的操作）


然后只要重启Apache服务就能打开该网页了，注意一定要挂VPN不然会打不开。
还需要记住直接用curl +公有ip是看不到正确显示的，当时就以为配置有误花费了大量的时间。所以要记住使用curl -L查看是否成功。
原因：如果 WordPress 配置了强制 HTTPS 或更改了站点地址（如从 /wp-admin/install.php 重定向），不加 -L 会错过实际内容。
## 3.创建连接python程序的插件 ##
1.imei-checker.php

通过这个php文件设计该插件的样式，通过HTML语言设置了一个输入框和一个验证按钮：
```
return '
<div class="imei-checker-container">
    <form id="imeiCheckForm">
        <div class="form-group">
            <label for="imei_input">请输入IMEI号码：</label>
            <input type="text" id="imei_input" pattern="\d{15}" required>
        </div>
        <button type="submit" class="submit-btn">立即验证</button>
    </form>
    <div id="imeiResult" class="result-container">
        <div id="resultContent"></div>
    </div>
</div>';
```
还通过向本地5000端口的Python服务发送POST请求以实现和python程序的连接：
```
$response = wp_remote_post('http://localhost:5000/verify_imei', [
    'headers' => ['Content-Type' => 'application/json'],
    'body' => json_encode(['imei' => $imei]),
    'timeout' => 15
]);
```
还有AJAX前后端交互技术的相关代码主要是通过Javascript与服务端建立联系处理，编写了imei-checker.js的插件配套的 JavaScript 代码，负责处理 IMEI 验证表单的交互逻辑以及style.css负责插件的容器，按钮等设计。将三个文件放入/var/www/html/wp-content/plugins/imei-checker/目录下即可

有关Javascript和AJAX的内容因为没有学习过，还要日后慢慢理解

2.python代码

简单的利用beautifulsoup进行爬网，因为目标网站存在两个名为"result-panel"的class：
```
<div class="result-panel">356596051659016</div>
<div class="result-panel">◯</div>
```
我只想获取下面的结果，所以通过该代码读取第二个结果：
```python
 soup = BeautifulSoup(response.text, 'html.parser')
        result_span = soup.find_all('div', class_='result-panel')
        if len(result_span) >= 2:  # 确保至少有两个匹配项
            true_panel = result_span[1]  # 取第二个（索引 1）
```
这样就完成了结果读取，然后只要通过5000端口启动服务就可以了：
```
app.run(host='0.0.0.0', port=5000, debug=False)
```
python程序编写完后，通过`sudo systemctl start  imei-checker
`就能保证代码一直在后台运行了
**注意：**
该代码会一直在后台运行，如果直接已python imei_checker.py的方式运行会显示5000端口被占用，需要stop，才能解放端口


3.wordpress页面操作

插件编写成功后，就能在wordpress的插件栏找到imei服务的插件了，启用之后，在页面的区块编辑器上选用“经典”区块，**而不是“代码”区块**然后输入"[imei_checker]"再打开页面就能实现该网页了。
**根本原因：**
WordPress的区块编辑器（Gutenberg）对短代码的处理方式与传统编辑器不同，可能导致：

- 短代码被当作纯文本显示

- 插件输出被过滤

- 前端资源未正确加载
  
## 更改域名链接CloudFront ##

将EC2的公有DNS链接添加到Clooud Front的源中并添加行为**因为EC2只有HTTP，所以在行为中选择HTTP和HTTPS**
打开EC2的Wordpress后台，在"设置" → "常规" 中将原来的EC2域名换成自己的域名。
**注意：**
  如果出现问题，也可以在EC2中修改Sql来更改域名
进入MySQL
    `mysql -u 用户名 -p`
选择wordpress的数据库
    `USE 数据库名;`
检查当前域名设置
    `SELECT * FROM wp_options WHERE option_name IN ('siteurl', 'home');`
更新为新域名
    `UPDATE wp_options SET option_value = 'https://你的新域名.com' WHERE option_name = 'siteurl';`
    `UPDATE wp_options SET option_value = 'https://你的新域名.com' WHERE option_name = 'home';`
