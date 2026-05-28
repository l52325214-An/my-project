# 學習筆記：DevOps 雲端架構與多環境部屬

> 💡 **核心總結**：本筆記完整涵蓋了現代軟體工程的標準 SOP，包含「本地開發 ➔ 版本控制 ➔ 容器化打包 ➔ 雲端權限管理 ➔ 雲端伺服器部屬 ➔ 雲端服務互相溝通」。
> 

## 📦 Topic 1: DevOps - 透過 Docker 進行多系統兼容與 GitHub 多分支管理

### 1. Git & GitHub 核心名詞與觀念

| **專有名詞** | **核心意義與功能** |
| --- | --- |
| **Repository** | 專案資料夾（程式碼的雲端或本地儲存庫）。 |
| **Commit** | 存檔的紀錄點（將當前修改正式打包留存，建立歷史節點）。 |
| **Branch** | 分支，平行的工作線（不影響主線的安全開發環境）。 |
| **PR / MR** | Pull Request / Merge Request，請求別人 Review 自己改動的程式碼。 |
| **Push / Pull** | 將改動的程式碼「上傳」到雲端，或從雲端「下載」最新版本。 |
| **Clone** | 第一次將遠端專案完整下載到本地電腦。 |
| **Init** | 在本地建立一個全新的 Git 專案。 |

### 2. GitHub 多分支開發標準流程 (Git Flow)

1. **取得專案**：複製 GitHub 的 HTTPS 網址 ➔ 終端機執行 `git clone` ➔ `cd` 進入專案資料夾。
2. **開發與提交**：建立或修改檔案後，依序執行：
    - `git status`（查看改動狀態）
    - `git add .`（暫存所有改動）
    - `git commit -m "你的更新說明"`（正式存檔）
3. **歷史查詢**：使用 `git log` 查看過往提交紀錄。
4. **同步與分支切換**：
    - 下載最新進度：`git pull`
    - 建立並切換到開發分支：`git branch dev`
    - 第一次將新分支推上雲端並永久綁定：Bash
        
        ```
        git push --set-upstream origin dev
        ```
        
5. **合併回主線**：在 GitHub 網頁點擊 **Compare and pull request** ➔ 填寫說明確認後 Create ➔ 團隊審核後 Merge。

### 3. Docker 容器化打包流程

> 確保程式碼在任何系統環境都能擁有一致的執行結果。
> 
1. 在本機下載並開啟 **Docker Desktop**。
2. 確保程式碼在本機的 Docker 環境可以正常運行。
3. 將程式碼與環境配置寫入 **Dockerfile**。
4. **封裝映像檔 (Build)**：Bash
    
    ```
    docker build -t 你的映像檔名稱 .
    ```
    
5. **上傳雲端倉庫 (Push)**：Bash
    
    ```
    docker push 你的DockerHub帳號/你的映像檔名稱:latest
    ```
    

## ☁️ Topic 2: DevOps 與 AWS 雲端開發實戰

### 1. IAM 權限控管與本地連線 (AWS CLI)

**👨‍💻 管理員設定（賦予權限）**

- 搜尋 **IAM** ➔ 進入「使用者群組」 ➔ 選擇 `dev` Group。
- 刪除原有不必要的權限 ➔ 新增許可 ➔ 連接政策：搜尋並加入 **`AmazonS3FullAccess`**。

**🧑‍💻 開發人員設定（取得憑證與本地註冊）**

- IAM ➔ 使用者 ➔ 點選開發人員帳號 ➔ 安全憑證 ➔ **建立存取金鑰**（目的選：本機代碼）。
- 下載並妥善保存。（🚨 **資安鐵則：絕不可將憑證給他人或上傳至 GitHub，外洩有極大安全漏洞！**）
- 下載安裝 AWS CLI：Bash
    
    ```
    msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi /qr
    ```
    
- **本地綁定金鑰**：終端機輸入 `aws configure`，並依序填入金鑰 ID、金鑰密碼、區域（如 `ap-northeast-1`）與輸出格式。
- **確認連線成功**：輸入下方指令，出現 `UserID`, `Account`, `Arn` 即代表註冊成功。Bash
    
    ```
    aws sts get-caller-identity
    ```
    

### 2. 建立與管理 S3 儲存桶 (Bucket)

- **核心觀念**：`Bucket` = 放檔案的地方（資料夾）；`Object` = 檔案本身。上傳檔案必須有一個 Bucket 接收。
- **用指令建立指定區域的 Bucket**（例如建在台灣最近的東京機房，名稱需全球唯一）：Bash
    
    ```
    aws s3api create-bucket --bucket ckc-26 --region ap-northeast-1 --create-bucket-configuration LocationConstraint=ap-northeast-1
    ```
    
    *(💡 成功會回傳 `"Location": "http://ckc-26.s3.amazonaws.com/"`)*
    
- **查看 Bucket 清單**：Bash
    
    ```
    aws s3 ls
    ```
    

### 3. 租用 EC2 雲端主機與運行 Docker

1. **建立 EC2**：地區選台北 ➔ 系統選 Amazon Linux 2023 ➔ 等級選 `t3.small` ➔ 硬碟 10G（*⚠️ IAM 執行個體設定檔先保留空白*）。
2. **連線主機**：使用 SSH 與加密金鑰（`.pem`）登入 Linux。
3. **下載並啟動 Docker 專案**：Bash
    
    ```
    docker run -d -p 19191:19191 --name my-flask-app 你的DockerHub帳號/my-flask-app:latest
    ```
    
4. **確認運行狀態**：輸入 `docker ps` 查看 Container 是否順利啟動。

### 4. 🌟 進階資安架構：EC2 授權訪問 S3 (無金鑰開發)

> **開發情境**：開發 `/feature3` 檔案上傳管理頁面，檔案要存入 `ckc-26` Bucket，並部屬到 EC2。
> 
> 
> **資安鐵則**：程式碼裡面**絕對不能**寫死存取金鑰 (Access Key)，必須透過 IAM Role 授權！
> 
1. 剛開好的 EC2 是一張白紙，雖然裡面裝了 AWS CLI，但輸入 `aws s3 ls` 會顯示沒有權限。
2. 進入 AWS 後台 ➔ **IAM** ➔ **角色 (Roles)** ➔ **建立角色**。
3. 選擇 **AWS 服務** ➔ 使用案例選 **EC2** ➔ 許可政策勾選 **`AmazonS3FullAccess`** ➔ 完成建立角色。
4. 回到 **EC2 列表** ➔ 選取該台主機 ➔ 點擊右上角 **動作** ➔ **安全性** ➔ **修改 IAM 角色** ➔ 掛載剛剛建好的 Role。
5. 完成後，EC2 不需任何密碼設定，就能合法、安全地對 S3 進行讀寫！