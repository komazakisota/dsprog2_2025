import flet as ft
import requests
import sqlite3
from datetime import datetime

# 定数
AREA_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_BASE_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/"
DB_NAME = "weather.db"
# ブラウザのふりをするためのヘッダー
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}

# --- データベース関連 ---
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        # 地域テーブル (Master Data)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS areas (
                code TEXT PRIMARY KEY,
                name TEXT
            )
        """)
        # 予報テーブル
        cur.execute("""
            CREATE TABLE IF NOT EXISTS forecasts (
                area_code TEXT,
                forecast_date TEXT,
                weather_text TEXT,
                updated_at DATETIME,
                PRIMARY KEY (area_code, forecast_date)
            )
        """)
        conn.commit()

def save_forecast(area_code, data):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # JSONから必要な部分を抽出
        time_series = data[0]["timeSeries"][0]
        areas_info = time_series["areas"][0]
        times = time_series["timeDefines"]
        weathers = areas_info["weathers"]

        for i in range(len(times)):
            # INSERT OR REPLACE を使うことで、既存データがあれば更新される（正規化の恩恵）
            cur.execute("""
                INSERT OR REPLACE INTO forecasts (area_code, forecast_date, weather_text, updated_at)
                VALUES (?, ?, ?, ?)
            """, (area_code, times[i][:10], weathers[i], now))
        conn.commit()

# --- アプリ本体 ---
def main(page: ft.Page):
    page.title = "気象庁 天気予報 DB版"
    page.theme_mode = ft.ThemeMode.LIGHT
    init_db()

    def get_areas_from_api():
        res = requests.get(AREA_URL, headers=HEADERS)
        offices = res.json().get("offices", {})
        # 地域情報をDBに保存
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            for code, info in offices.items():
                cur.execute("INSERT OR REPLACE INTO areas VALUES (?, ?)", (code, info["name"]))
            conn.commit()
        return offices

    def area_selected(e):
        area_code = e.control.data
        area_name = e.control.title.value
        
        # 1. APIから取得（HEADERSを追加してJSONエラーを回避）
        try:
            res = requests.get(f"{FORECAST_BASE_URL}{area_code}.json", headers=HEADERS)
            res.raise_for_status()
            forecast_json = res.json()
            
            # 2. DBに保存
            save_forecast(area_code, forecast_json)
            
            # 3. DBからデータを読み出して表示（課題の要件：表示にDBを使う）
            display_from_db(area_code, area_name)
            
        except Exception as ex:
            print(f"Error: {ex}")
            page.snack_bar = ft.SnackBar(ft.Text("データ取得に失敗しました"))
            page.snack_bar.open = True
            page.update()

    def display_from_db(area_code, area_name):
        weather_display.controls.clear()
        weather_display.controls.append(ft.Text(f"{area_name} の予報 (DB参照)", size=20, weight="bold"))

        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            cur.execute("SELECT forecast_date, weather_text FROM forecasts WHERE area_code = ? ORDER BY forecast_date", (area_code,))
            rows = cur.fetchall()

            for date, text in rows:
                weather_display.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.ListTile(
                                leading=ft.Icon(ft.Icons.WB_CLOUDY),
                                title=ft.Text(f"{date} の天気"),
                                subtitle=ft.Text(text)
                            ), padding=5
                        )
                    )
                )
        page.update()

    # --- UI構成 ---
    offices = get_areas_from_api()
    area_list = ft.ListView(expand=1, spacing=5)
    
    for code, info in offices.items():
        # 修正ポイント: .controls.append() を使う
        area_list.controls.append(
            ft.ListTile(
                title=ft.Text(info["name"]),
                data=code,
                on_click=area_selected
            )
        )

    weather_display = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

    page.add(
        ft.Row(
            [
                ft.Container(content=area_list, width=250, bgcolor=ft.Colors.GREY_50),
                ft.VerticalDivider(width=1),
                ft.Container(content=weather_display, expand=True, padding=20),
            ],
            expand=True,
        )
    )

ft.app(target=main)