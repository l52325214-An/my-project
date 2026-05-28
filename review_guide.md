# 專案審查與部署指南 (Project Review & Deployment Guide)

本文件供主管審查此專案的 Docker 化與功能實作成效。目前最新的 Docker 映像檔已成功部署並運行於**測試機 (Testing Machine)** 上，同時本機測試也已全數通過。

---

## 1. 測試機快速審查 (Staging/Testing Server Review)

最新的專案版本已部署至測試環境，您可以直接透過以下網址進行審查，無須於本機執行任何指令：

* 🌐 **測試機網頁主頁**: `http://<測試機IP或網域>:19191` (請將其替換為您測試機的實際 IP)
  * 點選頁面中的 **早上計畫 (Feature 1)** 與 **下午計畫 (Feature 2)** 按鈕，確認內容是否能動態載入。
* 🔗 **Feature 1 API 節點**: `http://<測試機IP或網域>:19191/feature1`
  * 預期回應：`早上要看股票`
* 🔗 **Feature 2 API 節點**: `http://<測試機IP或網域>:19191/feature2`
  * 預期回應：`要找下午上班的公司`

---

## 2. 專案基本資訊 (Project Overview)
* **網頁框架**: Python Flask (v3.0+)
* **服務連接埠 (Port)**: `19191`
* **Docker 映像檔名稱**: `my-flask-app:latest`
* **容器名稱**: `my-flask-container`

---

## 3. 本機執行與審查步驟 (Optional: Local Run)

如果您需要在您自己的電腦上執行本機測試，請遵循以下步驟（需安裝 Docker Desktop）：

1. **在本機啟動 Docker 容器**：
   ```bash
   docker run -d -p 19191:19191 --name my-flask-container my-flask-app
   ```
2. **本機審查網址**：
   * 互動網頁: [http://localhost:19191](http://localhost:19191)
   * Feature 1: [http://localhost:19191/feature1](http://localhost:19191/feature1)
   * Feature 2: [http://localhost:19191/feature2](http://localhost:19191/feature2)

---

## 4. 單元測試驗證 (Unit Tests)
本專案已附帶自動化測試，並在建置前通過驗證：

```bash
python -m pytest
```
* 測試模組: `test/test_main.py`
* 目前狀態：**3項測試全部通過 (Passed)**

---

## 5. 測試機運維常用指令
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
