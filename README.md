# PEOPLE 名人問答

使用 `people.sql` 中的人物資料與預先計算的語意向量，讓使用者以姓氏、人物名稱或自然語言問題查詢人物簡介。Gradio 和 Streamlit 介面共用同一套檢索邏輯。

## 本機執行 Gradio

```powershell
uv sync
uv run python main.py
```

## 本機執行 Streamlit

```powershell
uv sync
uv run streamlit run streamlit_app.py
```

首次啟動會下載 `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` 向量模型。模型會在程序中載入一次，後續提問會將問題轉成向量，再與 `people.sql` 內的資料向量比對，回覆內容以資料集為準。

## 部署到 Streamlit Community Cloud

將此專案推送到 GitHub，建立 Streamlit app 時將入口檔設定為 `streamlit_app.py`。根目錄的 `pyproject.toml` 和 `uv.lock` 用來安裝相依套件；`people.sql` 也需一併提交。Streamlit Cloud 會以新環境執行應用程式，因此首次啟動需要網路下載模型。
