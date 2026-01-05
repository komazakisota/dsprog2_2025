import flet as ft
import requests

# 定数
AREA_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_BASE_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/"

def main(page: ft.Page):
    page.title = "気象庁 天気予報"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 800
    page.window_height = 600

    # --- データ取得関数 ---
    def get_areas():
        """地域リストを取得"""
        response = requests.get(AREA_URL)
        data = response.json()
        # 'offices' が都道府県単位のコードリスト
        return data.get("offices", {})

    def get_forecast(area_code):
        """特定の地域の天気予報を取得"""
        url = f"{FORECAST_BASE_URL}{area_code}.json"
        response = requests.get(url)
        return response.json()

    # --- イベントハンドラ ---
    def area_selected(e):
        """地域がクリックされた時の処理"""
        area_code = e.control.data
        area_name = e.control.title.value
        
        # 予報データの取得
        forecast_data = get_forecast(area_code)
        
        # 表示エリアの更新
        weather_display.controls.clear()
        weather_display.controls.append(ft.Text(f"{area_name} の予報", size=20, weight="bold"))

        # 近々の予報（data[0]）をExpansionTileで表示
        time_series = forecast_data[0]["timeSeries"][0]
        areas_info = time_series["areas"][0]
        times = time_series["timeDefines"]

        for i in range(len(times)):
            date_str = times[i][:10] # 日付部分を抽出
            weather_text = areas_info["weathers"][i]
            
            # ExpansionTile を使用して詳細（今回は天気文字列のみ）を表示
            weather_display.controls.append(
                ft.ExpansionTile(
                    title=ft.Text(f"{date_str} の予報"),
                    subtitle=ft.Text(weather_text),
                    controls=[
                        ft.ListTile(title=ft.Text(f"詳細情報: {weather_text}"))
                    ]
                )
            )
        page.update()

    # --- UIコンポーネント ---
    
    # 1. 地域リスト (ListTile を並べる)
    areas = get_areas()
    area_list = ft.ListView(expand=1, spacing=10, padding=10)
    for code, info in areas.items():
        area_list.controls.append(
            ft.ListTile(
                title=ft.Text(info["name"]),
                subtitle=ft.Text(f"Code: {code}"),
                data=code, # 後で取得するためにコードを隠し持たせる
                on_click=area_selected
            )
        )

    # 2. 右側の表示エリア
    weather_display = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

    # 3. NavigationRail
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.HOME, label="ホーム"),
            ft.NavigationRailDestination(icon=ft.Icons.SETTINGS, label="設定"),
        ],
    )

    # --- レイアウト配置 ---
    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                ft.Container(content=area_list, width=250),
                ft.VerticalDivider(width=1),
                ft.Container(content=weather_display, expand=True, padding=20),
            ],
            expand=True,
        )
    )

ft.app(target=main)