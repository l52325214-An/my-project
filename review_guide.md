# 專案審查與部署指南 (Project Review & Deployment Guide)

本文件供主管審查此專案的 Docker 化與功能實作成效。目前最新的 Docker 映像檔已成功部署並運行於**測試機 (Testing Machine)** 上，同時本機測試也已全數通過。

---

## 1. 測試機快速審查 (Staging/Testing Server Review)

最新的專案版本已部署至測試環境，您可以直接透過以下網址進行審查，無須於本機執行任何指令：

* 🌐 **測試機網頁主頁**: `http://<測試機IP或網域>:19191` (請將其替換為您測試機的實際 IP)
  * 點選頁面中的 **早上計畫 (Feature 1)** 與 **下午計畫 (Feature 2)** 按鈕，確認內容是否能動態載入。
  * 點選 **📂 S3 檔案管理頁面 (Feature 3)** 連結，確認能否安全瀏覽、上傳及下載 S3 儲存桶中的檔案。
* 🔗 **Feature 1 API 節點**: `http://<測試機IP或網域>:19191/feature1`
* 🔗 **Feature 2 API 節點**: `http://<測試機IP或網域>:19191/feature2`
* 🔗 **Feature 3 S3 管理頁面**: `http://<測試機IP或網域>:19191/feature3`

---

## 2. 專案基本資訊 (Project Overview)
* **網頁框架**: Python Flask (v3.0+)
* **服務連接埠 (Port)**: `19191`
* **Docker 映像檔名稱**: `my-flask-app:latest`
* **容器名稱**: `my-flask-container`

---

## 3. 安全性設計：AWS S3 金鑰保護機制 (Feature 3)
為了確保金鑰安全性，本專案在存取 AWS S3 儲存桶 `ckc-26` 時**絕無硬編碼存取金鑰 (No Hardcoded Access Keys)**。

### 測試環境與生產環境之安全配置：
1. **本機測試 (Local Dev)**：
   * 程式碼會自動使用本機的認證鏈。如果要在本機操作 S3，請先執行 `aws configure` 設定憑證，或設定 `AWS_ACCESS_KEY_ID` 與 `AWS_SECRET_ACCESS_KEY` 環境變數。
   * 若未設定憑證，網頁會出現友善的引導警示，並安全地鎖定上傳功能，避免錯誤。
2. **測試機/生產環境 (EC2 Deployment)**：
   * 未來部署至 EC2 時，**不需傳入任何金鑰**。
   * 請在 AWS 控制台將此 EC2 執行個體關聯至一個 **IAM 角色 (IAM Instance Profile)**。
   * 此 IAM 角色必須擁有讀寫 S3 儲存桶 `ckc-26` 的權限（例如 `s3:ListBucket`, `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject`）。Docker 中的 Boto3 會自動透過 AWS 憑證鏈取得臨時權限進行存取。

---

## 4. 本機執行與審查步驟 (Optional: Local Run)

如果您需要在您自己的電腦上執行本機測試，請遵循以下步驟（需安裝 Docker Desktop）：

1. **在本機啟動 Docker 容器**：
   ```bash
   docker run -d -p 19191:19191 --name my-flask-container my-flask-app
   ```
2. **本機審查網址**：
   * 互動網頁: [http://localhost:19191](http://localhost:19191)
   * Feature 3 S3 管理頁面: [http://localhost:19191/feature3](http://localhost:19191/feature3)

---

## 5. 單元測試驗證 (Unit Tests)
本專案已附帶自動化測試，並在建置前通過驗證。為了避免測試環境因沒有 AWS 憑證而建置失敗，已使用 `unittest.mock` 技術對 S3 的呼叫進行完整 Mock 測試：

```bash
python -m pytest
```
* 測試模組: `test/test_main.py`
* 目前狀態：**8項測試全部通過 (Passed)**（新增了 5 項針對 S3 檔案列表、上傳、下載及刪除的 Mock 測試）

---

## 6. 測試機運維常用指令
若需在測試機上管理此容器，可使用以下 Docker 指令：

* **查看容器日誌 (Logs)**:
  ```bash
  docker logs -f my-flask-container
  ```
* **重啟容器 (Restart)**:
  ```bash
  docker restart my-flask-container
  ```
* **停止服務 (Stop)**:
  ```bash
  docker stop my-flask-container
  ```
