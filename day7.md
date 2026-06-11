# Untitled

# 🌐 雲端基礎架構與維運實戰全書 (AWS & GCP 雙強對齊)

> 💡 **筆記定位**：本手冊融合雲端治理（FinOps）、身分資安（IAM）、自動化維運（DevOps）、標籤化網路防禦以及實務故障排除（Troubleshooting），作為企業級 AI 專案（Dify + Bedrock）的落地底座。
> 

---

## 📂 Topic 1：雲端治理與成本控管 (Cloud Governance & FinOps)

### 📌 雲端三大核心基石

- **可用性 (Availability)**：透過多可用區 (Multi-AZ) 與負載均衡（LB），解耦「業務邏輯層」與「全代管 AI 宇宙」，確保單點崩潰時服務不中斷。
- **安全性 (Security)**：落實縱深防禦 (Defense in Depth)，從外牆網路防火牆、標籤權限隔離到內層私有網段鎖死。
- **計費模式 (Billing Models)**：採用按量計費 (Pay-as-you-go)，以秒級或小時級計算，需建立嚴格監控以防範帳單炸彈。

### 👥 帳戶與組織架構對照

> 💡 **核心邏輯**：資源按專案隔離，帳單由組織統一收納。
> 
- **GCP Project (專案)**：GCP 的核心隔離單位。所有資源（如 GCE、RDS）都必須隸屬特定專案，專案間預算與網路預設防禦隔離。
- **GCP Billing Account (計費帳戶)**：獨立的計費實體，可一對多綁定多個 Project 進行統一扣款。
- **AWS Organization (組織)**：企業級多帳號管理工具（等同 GCP Organization），用來合併多帳戶帳單並下達頂層安全策略 (SCP)。

### 🚨 預算防禦機制 (Budget)

- **預算警報 (Budget Alerts)**：設定費用預算上限與閾值 (如消費觸發 50%、80%、100%)。
- **自動化熔斷**：一旦觸發閾值，利用 CloudWatch/Cloud Monitoring 自動發送警告通知至 LINE/Slack/Discord，在開發期實施預算熔斷。

---

## 🔐 Topic 2：身分安全與團隊協作 (IAM & Collaboration)

### 🤝 專案團隊開發 (Join Project)

- **實務操作**：在 GCP 的 **IAM & Admin (管理員)** 頁面，點擊「Grant Access (授予存取權)」，將同學的 **Google Email** 新增至專案。
- **最小權限原則 (Principle of Least Privilege)**：根據職責精準指派角色。例如：
    - `Compute Viewer` (唯讀，只能看不能改)
    - `Compute Admin` (具備完全控制虛擬機的權限)
    - *切勿直接給予全局 Owner 權限，嚴防誤刪與資安漏洞。*

### 🔑 身分識別管理元件

- **User Account (個人帳號)**：實名制個人帳號，便於透過稽核日誌 (Cloud Logging) 追蹤「是誰動了雲端資源」。
- **Organization Group (組織群組)**：將特定職能 (如開發組、運維組) 的權限打包。加人時直接將帳號丟進群組，避免單獨設定導致管理疏漏。
- **Safe MFA (多因素驗證)**：強制所有 IAM 帳號、Group 登入時須搭配手機 Authenticator App 或硬體金鑰 (FIDO2)，阻斷 99% 密碼外洩引發的篡權風險。

---

## 🏗️ Topic 3：虛擬機運維與自動化 (Compute Engine & DevOps)

### 💻 運算資源服務

- **GCE (Google Compute Engine)**：GCP 的全代管虛擬機服務 (對應 AWS 的 EC2)。

### 🧠 元數據與動態環境變數 (Metadata)

- **秘密窗口 (IP: 169.254.169.254)**：虛擬機內部與機房底層溝通的特製 API。
- **實務應用**：
    - **查詢外部 IP**：可透過特製 Header 繞過外網，在 Linux 內直接獲取本機公網外部 IP。
    - **動態環境變數**：作為變數託管中心，程式啟動時自動撈取，落實「代碼與設定分離」的操作效能。

> GCP 查詢外部 IP 實戰指令：
`curl -H "Metadata-Flavor: Google" <http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip`>
> 

### ⚙️ Startup Script (啟動腳本 ➔ 免連線自動化)

- **技術落地**：建立虛擬機時在進階設定的「Startup Script」框內寫入指令。
- **實戰範例 (開機自動安裝 Docker 並運行 Flask 專案)：**
    - `#!/bin/bash`
    - `apt-get update`
    - `apt-get install -y docker.io`
    - `systemctl start docker`
    - `systemctl enable docker`
    - `docker pull an367968/my-flask-app:latest`
    - `docker run -d -p 80:5000 --name web-service an367968/my-flask-app:latest`
- **優勢**：**開機即完工**。開發者完全不需要登入黑畫面手動打字，落實運維自動化。

### 🔏 零信任安全連線 (Zero-Trust SSH)

- 捨棄傳統手動產生並上傳 `.pem` 密鑰的危險做法。
- 改用 GCP 的 **Identity-Aware Proxy (IAP)** 或瀏覽器一鍵 SSH，由雲端平台進行即時的身分憑證動態注入。

---

## 🛡️ Topic 4：標籤化網路防禦 (Network Security & Tag Management)

### 🏷️ 雲端標籤家族的本質區別

- **Label (行政/成本標籤)**：用於**商業與財務管理**。鍵值對形式，例：`project: ai-scheduler`，便於在綜合帳單中精算特定專案的花費。
- **Tag / Network Tag (技術/網路標籤)**：單一字串，用於**控制網路流量與防火牆規則**。

### 🧱 標籤化防火牆策略 (Tag-based Firewall Rules)

- **傳統痛點**：舊式防火牆必須死死綁定特定虛擬機的內部 IP，一旦機器重啟、IP 變動就會當場失效。
- **標籤維運邏輯**：
    1. **建立規則**：建立防火牆 Policy，目標對象指定為特定的 **Network Tag** (例如：`http-server`)，方向設定為 Ingress (輸入)，開通 TCP Port 80。
    2. **套用規則**：未來任何虛擬機只要在設定裡貼上 `http-server` 這個標籤，**就會瞬間繼承該防火牆規則，自動對外開通 Port 80**，實現軟體定義網路（SDN）。

---

## 🚨 Topic 5：實務故障排除與災難復原 (Troubleshooting & DR)

### 🔥 場景一：雲端硬碟 (EBS/Disk) 空間滿了怎麼辦？

> **當系統顯示 No space left on device 或 Docker 爆掉時的處理 SOP：**
> 
1. **Step 1（雲端熱插拔擴容）**：至 AWS/GCP 控制台找到該虛擬機的磁碟區（AWS 稱為 EBS），點擊「Modify/Edit」，直接調整容量 (如 20GB ➔ 50GB)。此步驟可**在不停機、不影響線上服務的情況下線上完成**。
2. **Step 2（Linux 檔案系統認列）**：登入主機執行以下指令讓作業系統正式吃滿新擴展的空間。
    - 擴展磁碟分區 (以 xvda 磁碟的第 1 分區為例)：
    `sudo growpart /dev/xvda 1`
    - 擴展檔案系統 (適用於 EXT4 格式，讓空間正式可用)：
    `sudo resize2fs /dev/xvda1`

### 🔥 場景二：如何橫向擴展一模一樣的虛擬機？

> **當門市流量爆增，需要快速複製多台「排班管家伺服器」背負負載時：**
> 
1. **製作鏡像 (AMI / Image)**：
    - 在跑得最完美的機器上點擊右鍵 ➔ `Actions` ➔ `Image and templates` ➔ `Create Image` (AWS 稱為 AMI)。
    - 這會將當前的 OS、Docker、代碼、環境變數完整打包封裝成一隻「系統大補帖」。
2. **複製投放 (Launch from AMI)**：
    - 在啟動全新虛擬機的頁面中，作業系統選擇 **「My AMIs (我的映像檔)」** 並指定剛才做好的那一隻大補帖。
    - 開機完成後，新機器內部直接自帶一模一樣的環境，達成秒級複製與高可用橫向擴展（Scale Out）。