# motrol_rating
入口：myagent_main.py
http://localhost:29506/agent/chat
payload={
input: ""
}

## 使用说明
1. **安装依赖**:  
   需要根据requirements.txt安装依赖  
    cd到项目目录 linux操作可能是  
   ```bash
   python3 -m pip install -r requirement.txt
   ```
2. **地址下载**:  
   https://github.com/adryfish/fingerprint-chromium/releases/download/142.0.7444.175/ungoogled-chromium-142.0.7444.175-1-x86_64_linux.tar.xz  
   网址下载压缩包，解压里面的文件到本地，然后重新压缩为zip格式，再上传到服务器，再解压文件，文件夹重命名为fingerprint_browser  

3. **redis本地仓库**:  
   任务队列需要redis，通过redis进行获取返回的结果ID，再根据ID进行查询数据内容，默认本地redis，详情配置在othertool.conredis文件  
   默认是无头浏览器，开启俩个获取有效的token就行，因为接口有限制，开多个也能获取，但是要实现多代理IP去请求接口，不然也是返回限制无法获取  

4. **fastapi配置**:  
   api_method.rating_fastapi.py  
   是接口设置文件，默认Token是API_TOKEN参数，可自行更改，更改后header的Token需要更改为自己设置的token  

5. **启动服务，默认 29507 端口，可自行更改**:  
   ```bash
   python3 -m main
   ```

6. **接口1：**:  
    curl:
    ```bash
    curl --location 'http://{服务器ip}:29507/motrol/submit' \
    --header 'Token: mumu' \
    --header 'Content-Type: application/json' \
    --data '{
        "user_name": "name",
        "user_count": 20,
        "mode": "12,16"
    }'
    ```
    接口1返回结果：  
    {
        "task_id": "name_20_1780371011577158561",
        "msg": ""
    }
    user_name: 用户名  
    user_count：查询局数  
    mode：模式（默认"12,16",可不填，可填 金 玉 王 12 16 9）  
    映射字段 mode_dict = {
        "金": "8",
        "玉": "12",
        "王": "16"
    }  
    "mode": "金"  
    "mode": "玉"  
    "mode": "王"  
    "mode": "9"  
    "mode": "12"  
    "mode": "16"  

7. **接口2：**:  
    curl:
    ```bash
    curl --location 'http://{服务器ip}:29507/result/name_20_1780371011577158561' \
    --header 'Token: mumu'
    ```
    接口2返回结果：  
    {
        "status": "pending",
        "create_time": "2026-06-01 18:20:47",
        "total": 100,
        "finished": 65
    }  
    或  
    图片资源  

8. **接口3：**:  
    ```bash
    curl --location 'http://{服务器ip}:29507/motrol/submit_paipu' \
    --header 'Token: mumu' \
    --header 'Content-Type: application/json' \
    --data '{
        "paipu_id": "250503-578881db-322c-4125-8d6c-250e66ac1315_a26520956"
    }'
    ```
    接口3返回结果：  
    {
        "task_id": "250503-578881db-322c-4125-8d6c-250e66ac1315_a26520956_1780386622732854641",
        "msg": ""
    }  
    获取单个牌谱的rating，若能查到pt也会获取pt  

9. **接口4：**:  
    ```bash
    curl --location 'http://{服务器ip}:29507/task_delete/name_100_1780390096501063493' \
    --header 'Token: mumu'
    ```
    接口4返回结果：  
    {
        "msg": "已删除name_100_1780390096501063493 任务"
    }  
    删除指定任务，防止过多任务占用资源  

10. **可能用到的linux命令**:  
    更新apt:
    ```bash
    sudo apt update
    ```
    检查浏览器是否输出版本号有输出才能使用:
    ```bash
    ./fingerprint_browser/chrome --version
    ```
    安装服务器chrome gui框架:
    ```bash
    sudo apt install -y libatk-bridge2.0-0 libatk1.0-0 libgtk-3-0 libnss3 libxss1 libasound2 libgbm1 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libpangocairo-1.0-0 libpango-1.0-0 libcairo2
    ```
    安装linux字体:
    ```bash
    apt install -y fonts-noto-cjk
    ```
    
11. **仅供参考借鉴学习，仅供参考借鉴学习，仅供参考借鉴学习，仅供参考借鉴学习**