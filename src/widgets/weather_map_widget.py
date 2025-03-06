"""
Weather Map Widget Module
------------------
This module provides the WeatherMapWidget class for displaying weather maps in the Weather & Alarm application.
"""
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QFrame, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import QUrl, pyqtSignal, Qt
from PyQt5.QtGui import QFont
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
except ImportError:
    # Show a helpful error message if PyQtWebEngine is not installed
    import sys
    from PyQt5.QtWidgets import QApplication, QMessageBox
    app = QApplication.instance() or QApplication(sys.argv)
    QMessageBox.critical(
        None, 
        "Missing Dependency", 
        "PyQtWebEngine is required for the Weather Map feature.\n"
        "Please install it using: pip install PyQtWebEngine>=5.15.0"
    )
    logging.error("PyQtWebEngine is not installed. Weather Map feature will not work.")
    # Create a dummy QWebEngineView class to prevent crashes
    class QWebEngineView(QWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            label = QLabel("PyQtWebEngine is not installed.\nPlease install it to use the Weather Map feature.", self)
            label.setAlignment(Qt.AlignCenter)
            layout = QVBoxLayout(self)
            layout.addWidget(label)
        
        def setHtml(self, *args, **kwargs):
            pass

from ..config import API_KEY

# Configure logging
logger = logging.getLogger(__name__)

class WeatherMapWidget(QWidget):
    """Widget for displaying weather maps."""
    
    # Signal emitted when the map is updated
    map_updated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """
        Initialize the weather map widget.
        
        Args:
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        
        # Initialize variables
        self.lat = None
        self.lon = None
        self.city = None
        self.map_type = "clouds_new"  # Default map type
        self.zoom_level = 10  # Default zoom level
        
        # Initialize UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Add title
        title_label = QLabel("Weather Map")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Add controls
        controls_layout = QHBoxLayout()
        
        # Map type selector
        map_type_label = QLabel("Map Type:")
        self.map_type_combo = QComboBox()
        self.map_type_combo.addItems([
            "Clouds", "Precipitation", "Pressure", "Wind Speed", 
            "Temperature", "Snow"
        ])
        self.map_type_combo.currentIndexChanged.connect(self.on_map_type_changed)
        
        # Zoom controls
        zoom_label = QLabel("Zoom:")
        zoom_in_button = QPushButton("+")
        zoom_in_button.setMaximumWidth(30)
        zoom_in_button.clicked.connect(self.zoom_in)
        
        zoom_out_button = QPushButton("-")
        zoom_out_button.setMaximumWidth(30)
        zoom_out_button.clicked.connect(self.zoom_out)
        
        # Add controls to layout
        controls_layout.addWidget(map_type_label)
        controls_layout.addWidget(self.map_type_combo)
        controls_layout.addStretch()
        controls_layout.addWidget(zoom_label)
        controls_layout.addWidget(zoom_out_button)
        controls_layout.addWidget(zoom_in_button)
        
        main_layout.addLayout(controls_layout)
        
        # Create map frame
        map_frame = QFrame()
        map_frame.setFrameShape(QFrame.StyledPanel)
        map_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.8);
            }
        """)
        
        map_layout = QVBoxLayout(map_frame)
        
        # Create web view for the map
        self.map_view = QWebEngineView()
        self.map_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.map_view.setMinimumHeight(400)
        map_layout.addWidget(self.map_view)
        
        # Add map frame to main layout
        main_layout.addWidget(map_frame)
        
        # Add status label
        self.status_label = QLabel("Please search for a location in the Weather tab to display the map.")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
    
    def on_map_type_changed(self, index):
        """
        Handle map type changed event.
        
        Args:
            index (int): Selected index
        """
        map_types = {
            0: "clouds_new",
            1: "precipitation_new",
            2: "pressure_new",
            3: "wind_new",
            4: "temp_new",
            5: "snow_new"
        }
        
        self.map_type = map_types.get(index, "clouds_new")
        self.update_map()
    
    def zoom_in(self):
        """Increase the zoom level."""
        if self.zoom_level < 18:
            self.zoom_level += 1
            self.update_map()
    
    def zoom_out(self):
        """Decrease the zoom level."""
        if self.zoom_level > 3:
            self.zoom_level -= 1
            self.update_map()
    
    def set_location(self, lat, lon, city=None):
        """
        Set the map location.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            city (str, optional): City name
        """
        self.lat = lat
        self.lon = lon
        self.city = city
        
        # Update status label
        if city:
            self.status_label.setText(f"Showing weather map for {city}")
        else:
            self.status_label.setText(f"Showing weather map for coordinates: {lat:.4f}, {lon:.4f}")
        
        # Update the map
        self.update_map()
    
    def update_map(self):
        """Update the weather map."""
        if not self.lat or not self.lon:
            QMessageBox.information(
                self,
                "No Location",
                "Please search for a location in the Weather tab first."
            )
            return
        
        if not API_KEY:
            QMessageBox.warning(
                self,
                "API Key Missing",
                "OpenWeatherMap API key is missing. Please set it in the settings."
            )
            return
        
        # Build the OpenWeatherMap URL
        # Using OpenLayers to display the map with OpenWeatherMap tiles
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Weather Map</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/openlayers/openlayers.github.io@master/en/v6.5.0/css/ol.css" type="text/css">
            <style>
                html, body, #map {{
                    width: 100%;
                    height: 100%;
                    margin: 0;
                    padding: 0;
                }}
            </style>
            <script src="https://cdn.jsdelivr.net/gh/openlayers/openlayers.github.io@master/en/v6.5.0/build/ol.js"></script>
        </head>
        <body>
            <div id="map"></div>
            <script>
                // Create the map
                var map = new ol.Map({{
                    target: 'map',
                    layers: [
                        // Base layer (OpenStreetMap)
                        new ol.layer.Tile({{
                            source: new ol.source.OSM()
                        }}),
                        // Weather layer
                        new ol.layer.Tile({{
                            source: new ol.source.XYZ({{
                                url: 'https://tile.openweathermap.org/map/{self.map_type}/{{z}}/{{x}}/{{y}}.png?appid={API_KEY}',
                                attributions: 'Weather data © OpenWeatherMap'
                            }}),
                            opacity: 0.7
                        }})
                    ],
                    view: new ol.View({{
                        center: ol.proj.fromLonLat([{self.lon}, {self.lat}]),
                        zoom: {self.zoom_level}
                    }})
                }});
                
                // Add a marker for the location
                var marker = new ol.Feature({{
                    geometry: new ol.geom.Point(ol.proj.fromLonLat([{self.lon}, {self.lat}]))
                }});
                
                var markerStyle = new ol.style.Style({{
                    image: new ol.style.Circle({{
                        radius: 6,
                        fill: new ol.style.Fill({{
                            color: '#ff0000'
                        }}),
                        stroke: new ol.style.Stroke({{
                            color: '#ffffff',
                            width: 2
                        }})
                    }})
                }});
                
                marker.setStyle(markerStyle);
                
                var vectorSource = new ol.source.Vector({{
                    features: [marker]
                }});
                
                var markerLayer = new ol.layer.Vector({{
                    source: vectorSource
                }});
                
                map.addLayer(markerLayer);
            </script>
        </body>
        </html>
        """
        
        # Load the HTML
        self.map_view.setHtml(html)
        
        # Emit map updated signal
        self.map_updated.emit({
            'lat': self.lat,
            'lon': self.lon,
            'city': self.city,
            'map_type': self.map_type,
            'zoom_level': self.zoom_level
        })
        
        logger.info(f"Weather map updated for {self.city or f'lat:{self.lat}, lon:{self.lon}'} with map type {self.map_type}") 