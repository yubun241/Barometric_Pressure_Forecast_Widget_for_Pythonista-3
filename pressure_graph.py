import requests
import matplotlib.pyplot as plt
import io
import ui
import location
from datetime import datetime

def get_current_location():
    """Get current GPS coordinates from iPhone"""
    location.start_updates()
    loc = location.get_location()
    location.stop_updates()
    if loc:
        return loc['latitude'], loc['longitude']
    else:
        # Default to Tokyo if location fails
        return 35.6341, 139.7184

def get_weather_data():
    """Fetch pressure data from Open-Meteo API"""
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
        
        # Extract next 12 hours
        display_times = [t.split('T')[1] for t in times_raw[now_idx : now_idx+13]]
        display_pressures = pressures[now_idx : now_idx+13]
        
        return display_times, display_pressures
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def create_plot(times, pressures):
    """Create graph image using Matplotlib"""
    plt.figure(figsize=(6, 4))
    plt.plot(times, pressures, marker='o', linestyle='-', color='#007AFF', linewidth=2)
    plt.fill_between(times, pressures, min(pressures)-1, color='#007AFF', alpha=0.1)
    
    # Text labels in English to avoid encoding issues
    plt.title("Pressure Forecast (Next 12h)", fontsize=12)
    plt.xlabel("Time (HH:MM)")
    plt.ylabel("hPa")
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png', dpi=120)
    plt.close()
    return ui.Image.from_data(img_data.getvalue())

class PressureView(ui.View):
    """Main UI View class"""
    def __init__(self):
        self.background_color = '#f0f0f7'
        self.name = "Pressure Forecast"
        
        times, pressures = get_weather_data()
        
        if times:
            # Display Graph
            img = create_plot(times, pressures)
            iv = ui.ImageView(frame=(0, 60, self.width, self.height-60))
            iv.flex = 'WH'
            iv.content_mode = ui.CONTENT_SCALE_ASPECT_FIT
            iv.image = img
            self.add_subview(iv)
            
            # Display Current Value
            current_label = ui.Label(frame=(0, 10, self.width, 40))
            current_label.flex = 'W'
            current_label.text = f"Current: {pressures[0]} hPa"
            current_label.text_color = '#cf2d2d'
            current_label.font = ('<system-bold>', 22)
            current_label.alignment = ui.ALIGN_CENTER
            self.add_subview(current_label)
        else:
            error_label = ui.Label(frame=self.bounds)
            error_label.text = "Data Update Failed"
            error_label.alignment = ui.ALIGN_CENTER
            self.add_subview(error_label)

if __name__ == '__main__':
    v = PressureView()
    v.present('sheet')
