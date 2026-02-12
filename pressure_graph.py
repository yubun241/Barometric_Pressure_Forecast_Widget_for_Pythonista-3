import requests
import matplotlib.pyplot as plt
import io
import ui
import location
from datetime import datetime

def get_current_location():
    """iPhoneのGPSから現在地を取得"""
    location.start_updates()
    loc = location.get_location()
    location.stop_updates()
    if loc:
        return loc['latitude'], loc['longitude']
    else:
        # 取得失敗時のデフォルト（東京）
        return 35.6341, 139.7184

def get_weather_data():
    """Open-Meteo APIから気圧データを取得"""
    lat, lon = get_current_location()
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "surface_pressure",
        "timezone": "Asia/Tokyo"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        now_idx = datetime.now().hour
        times_raw = data['hourly']['time']
        pressures = data['hourly']['surface_pressure']
        
        # 現在から12時間分を抽出
        display_times = [t.split('T')[1] for t in times_raw[now_idx : now_idx+13]]
        display_pressures = pressures[now_idx : now_idx+13]
        
        return display_times, display_pressures
    except Exception as e:
        return None, None

def create_plot(times, pressures):
    """Matplotlibでグラフ画像を作成"""
    plt.figure(figsize=(6, 4))
    plt.plot(times, pressures, marker='o', linestyle='-', color='#007AFF', linewidth=2)
    plt.fill_between(times, pressures, min(pressures)-1, color='#007AFF', alpha=0.1)
    
    plt.title("Barometric Pressure (Next 12h)", fontsize=12)
    plt.ylabel("hPa")
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png', dpi=120)
    plt.close()
    return ui.Image.from_data(img_data.getvalue())

class PressureView(ui.View):
    """UI表示用のメインクラス"""
    def __init__(self):
        self.background_color = '#f0f0f7'
        self.name = "気圧予報"
        
        times, pressures = get_weather_data()
        
        if times:
            img = create_plot(times, pressures)
            iv = ui.ImageView(frame=(0, 50, self.width, self.height-50))
            iv.flex = 'WH'
            iv.content_mode = ui.CONTENT_SCALE_ASPECT_FIT
            iv.image = img
            self.add_subview(iv)
            
            current_label = ui.Label(frame=(0, 10, self.width, 40))
            current_label.flex = 'W'
            current_label.text = f"現在: {pressures[0]} hPa"
            current_label.text_color = '#cf2d2d'
            current_label.font = ('<system-bold>', 24)
            current_label.alignment = ui.ALIGN_CENTER
            self.add_subview(current_label)
        else:
            label = ui.Label(frame=self.bounds)
            label.text = "Failed to load data"
            label.alignment = ui.ALIGN_CENTER
            self.add_subview(label)

if __name__ == '__main__':
    v = PressureView()
    # ウィジェットとして実行されているかチェック
    import canvas
    if ui.get_screen_size()[0] >= 768: # iPadなどの場合
        v.present('sheet')
    else:
        v.present('sheet')
