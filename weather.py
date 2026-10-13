import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
)
from PyQt5.QtCore import Qt

API_KEY = "3dea4f9d9766476f4cdf1e41584b9ecd"


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.city_label = QLabel("Enter city name:", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather", self)
        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Weather App")

        vbox = QVBoxLayout()
        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description_label)
        self.setLayout(vbox)

        for label in (self.city_label, self.city_input, self.temperature_label,
                      self.emoji_label, self.description_label):
            label.setAlignment(Qt.AlignCenter)

        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")

        self.setStyleSheet("""
            QLabel, QPushButton {
                font-family: calibri;
            }
            QLabel#city_label {
                font-size: 40px;
                font-style: italic;
            }
            QLineEdit#city_input {
                font-size: 40px;
            }
            QPushButton#get_weather_button {
                font-size: 30px;
                font-weight: bold;
            }
            QLabel#temperature_label {
                font-size: 75px;
            }
            QLabel#emoji_label {
                font-size: 100px;
                font-family: Segoe UI emoji;
            }
            QLabel#description_label {
                font-size: 50px;
            }
        """)

        self.get_weather_button.clicked.connect(self.get_weather)
        self.city_input.returnPressed.connect(self.get_weather)

    def get_weather(self):
        city = self.city_input.text().strip()
        if not city:
            self.display_error("Please enter a city")
            return

        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": API_KEY}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data["cod"] == 200:
                self.display_weather(data)

        except requests.exceptions.HTTPError:
            messages = {
                400: "Bad request:\nPlease check your input",
                401: "Unauthorized:\nInvalid API key",
                403: "Forbidden:\nAccess is denied",
                404: "Not found:\nCity not found",
                500: "Internal Server Error:\nPlease try again later",
                502: "Bad Gateway:\nInvalid response from the server",
                503: "Service Unavailable:\nServer is down",
                504: "Gateway Timeout:\nNo response from the server",
            }
            code = response.status_code
            self.display_error(messages.get(code, f"HTTP error occurred:\n{code}"))
        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error:\nCheck your internet connection")
        except requests.exceptions.Timeout:
            self.display_error("Timeout Error:\nThe request timed out")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many Redirects:\nCheck the URL")
        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Request Error:\n{req_error}")

    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 30px;")
        self.temperature_label.setText(message)
        self.emoji_label.clear()
        self.description_label.clear()

    def display_weather(self, data):
        self.temperature_label.setStyleSheet("font-size: 75px;")
        temperature_k = data["main"]["temp"]
        temperature_c = temperature_k - 273.15
        weather_id = data["weather"][0]["id"]
        weather_description = data["weather"][0]["description"]

        self.temperature_label.setText(f"{temperature_c:.0f}°C")
        self.emoji_label.setText(self.get_weather_emoji(weather_id))
        self.description_label.setText(weather_description.capitalize())

    @staticmethod
    def get_weather_emoji(weather_id):
        if 200 <= weather_id <= 232:
            return "⛈"   # thunderstorm
        elif 300 <= weather_id <= 321:
            return "🌦"   # drizzle
        elif 500 <= weather_id <= 531:
            return "🌧"   # rain
        elif 600 <= weather_id <= 622:
            return "❄"   # snow
        elif 701 <= weather_id <= 741:
            return "🌫"   # mist / fog
        elif weather_id == 762:
            return "🌋"   # volcanic ash
        elif weather_id == 771:
            return "💨"   # squall
        elif weather_id == 781:
            return "🌪"   # tornado
        elif weather_id == 800:
            return "☀"   # clear
        elif 801 <= weather_id <= 804:
            return "☁"   # clouds
        else:
            return ""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())