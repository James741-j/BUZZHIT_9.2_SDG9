"""
Climate Event Simulation Engine
Simulates extreme climate events (floods, heatwaves, high winds) with parametric inputs
and generates stress factors for infrastructure vulnerability assessment.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional
import math


class ClimateEventType(Enum):
    """Supported extreme climate event types"""
    FLOOD = "flood"
    HEATWAVE = "heatwave"
    HIGH_WIND = "high_wind"


@dataclass
class ClimateEvent:
    """Base class for climate events"""
    event_type: ClimateEventType
    severity: str  # low, moderate, high, extreme
    duration: float  # hours or days depending on event
    
    def get_severity_multiplier(self) -> float:
        """Convert severity to numerical multiplier"""
        severity_map = {
            "low": 0.5,
            "moderate": 0.75,
            "high": 1.0,
            "extreme": 1.3
        }
        return severity_map.get(self.severity, 1.0)
    
    def calculate_stress_factor(self) -> float:
        """Calculate overall stress factor (to be overridden by subclasses)"""
        raise NotImplementedError


class FloodEvent(ClimateEvent):
    """Flood event simulation with rainfall and water level parameters"""
    
    def __init__(
        self,
        rainfall_intensity: float,  # mm/hour
        water_level: float,  # meters above normal
        duration: float,  # hours
        severity: str = "moderate",
        flow_velocity: Optional[float] = None,  # m/s (for erosion)
        event_name: str = "Flood Event"
    ):
        super().__init__(ClimateEventType.FLOOD, severity, duration)
        self.rainfall_intensity = rainfall_intensity
        self.water_level = water_level
        self.flow_velocity = flow_velocity or self.estimate_flow_velocity()
        self.event_name = event_name
    
    def estimate_flow_velocity(self) -> float:
        """Estimate flow velocity from water level (simplified model)"""
        # Manning's equation approximation: V ≈ sqrt(depth)
        return min(5.0, math.sqrt(max(0.1, self.water_level)))
    
    def calculate_rainfall_factor(self) -> float:
        """Calculate stress from rainfall intensity (0-1 scale)"""
        # Critical rainfall thresholds (mm/hr)
        # Light: <10, Moderate: 10-30, Heavy: 30-100, Extreme: 100+
        if self.rainfall_intensity < 10:
            return 0.2
        elif self.rainfall_intensity < 30:
            return 0.4 + (self.rainfall_intensity - 10) / 50
        elif self.rainfall_intensity < 100:
            return 0.7 + (self.rainfall_intensity - 30) / 200
        else:
            return min(1.0, 0.9 + (self.rainfall_intensity - 100) / 300)
    
    def calculate_water_level_factor(self) -> float:
        """Calculate stress from water level (0-1 scale)"""
        # Critical water levels (meters)
        # Minor: <1, Moderate: 1-3, Major: 3-5, Catastrophic: 5+
        if self.water_level < 1:
            return 0.3
        elif self.water_level < 3:
            return 0.5 + (self.water_level - 1) / 5
        elif self.water_level < 5:
            return 0.8 + (self.water_level - 3) / 10
        else:
            return min(1.0, 0.95)
    
    def calculate_erosion_factor(self) -> float:
        """Calculate erosion/scour risk from flow velocity"""
        # Critical velocities: <1 m/s safe, >3 m/s high erosion
        if self.flow_velocity < 1:
            return 0.2
        elif self.flow_velocity < 2:
            return 0.4 + (self.flow_velocity - 1) / 2.5
        else:
            return min(1.0, 0.7 + (self.flow_velocity - 2) / 5)
    
    def calculate_duration_factor(self) -> float:
        """Calculate stress amplification from event duration"""
        # Longer events cause cumulative damage
        # Short: <6 hrs, Medium: 6-24 hrs, Long: 24+ hrs
        if self.duration < 6:
            return 0.7
        elif self.duration < 24:
            return 0.85 + (self.duration - 6) / 60
        else:
            return min(1.0, 1.0 + (self.duration - 24) / 100)
    
    def calculate_stress_factor(self) -> float:
        """Calculate overall flood stress factor"""
        rainfall_stress = self.calculate_rainfall_factor()
        water_level_stress = self.calculate_water_level_factor()
        erosion_stress = self.calculate_erosion_factor()
        duration_amplifier = self.calculate_duration_factor()
        severity_multiplier = self.get_severity_multiplier()
        
        # Weighted combination
        base_stress = (
            rainfall_stress * 0.25 +
            water_level_stress * 0.45 +
            erosion_stress * 0.30
        )
        
        total_stress = base_stress * duration_amplifier * severity_multiplier
        return min(1.0, total_stress)
    
    def get_info(self) -> Dict:
        """Return flood event information"""
        return {
            "event_type": "flood",
            "event_name": self.event_name,
            "rainfall_intensity_mm_hr": self.rainfall_intensity,
            "water_level_m": self.water_level,
            "flow_velocity_m_s": round(self.flow_velocity, 2),
            "duration_hours": self.duration,
            "severity": self.severity,
            "stress_factor": round(self.calculate_stress_factor(), 3),
            "components": {
                "rainfall_stress": round(self.calculate_rainfall_factor(), 3),
                "water_level_stress": round(self.calculate_water_level_factor(), 3),
                "erosion_stress": round(self.calculate_erosion_factor(), 3),
                "duration_amplifier": round(self.calculate_duration_factor(), 3)
            }
        }


class HeatwaveEvent(ClimateEvent):
    """Heatwave event simulation with temperature and duration parameters"""
    
    def __init__(
        self,
        max_temperature: float,  # °C
        min_temperature: float,  # °C (nighttime)
        duration: float,  # days
        severity: str = "moderate",
        humidity: float = 50,  # percentage
        solar_radiation: Optional[float] = None,  # W/m²
        event_name: str = "Heatwave Event"
    ):
        super().__init__(ClimateEventType.HEATWAVE, severity, duration)
        self.max_temperature = max_temperature
        self.min_temperature = min_temperature
        self.humidity = humidity
        self.solar_radiation = solar_radiation or self.estimate_solar_radiation()
        self.event_name = event_name
    
    def estimate_solar_radiation(self) -> float:
        """Estimate peak solar radiation from temperature"""
        # Typical values: 800-1000 W/m² during heatwaves
        return min(1200, 700 + (self.max_temperature - 30) * 15)
    
    def calculate_temperature_stress(self) -> float:
        """Calculate thermal stress from temperature (0-1 scale)"""
        # Temperature thresholds
        # Moderate: 35-38°C, High: 38-42°C, Extreme: 42+°C
        if self.max_temperature < 35:
            return 0.2
        elif self.max_temperature < 38:
            return 0.4 + (self.max_temperature - 35) / 10
        elif self.max_temperature < 42:
            return 0.7 + (self.max_temperature - 38) / 15
        else:
            return min(1.0, 0.9 + (self.max_temperature - 42) / 20)
    
    def calculate_thermal_expansion_stress(self) -> float:
        """Calculate stress from thermal expansion cycles"""
        # Daily temperature range (thermal cycling)
        temp_range = self.max_temperature - self.min_temperature
        
        # Larger ranges cause more expansion/contraction stress
        if temp_range < 10:
            return 0.3
        elif temp_range < 20:
            return 0.5 + (temp_range - 10) / 30
        else:
            return min(1.0, 0.75 + (temp_range - 20) / 40)
    
    def calculate_duration_stress(self) -> float:
        """Calculate stress from prolonged heat exposure"""
        # Cumulative heat stress
        # Short: <3 days, Medium: 3-7 days, Long: 7+ days
        if self.duration < 3:
            return 0.6
        elif self.duration < 7:
            return 0.75 + (self.duration - 3) / 20
        else:
            return min(1.0, 0.9 + (self.duration - 7) / 30)
    
    def calculate_humidity_factor(self) -> float:
        """Calculate stress modification from humidity"""
        # High humidity increases heat stress on materials
        if self.humidity < 40:
            return 0.8
        elif self.humidity < 70:
            return 0.9 + (self.humidity - 40) / 300
        else:
            return 1.0 + (self.humidity - 70) / 100
    
    def calculate_stress_factor(self) -> float:
        """Calculate overall heatwave stress factor"""
        temp_stress = self.calculate_temperature_stress()
        expansion_stress = self.calculate_thermal_expansion_stress()
        duration_stress = self.calculate_duration_stress()
        humidity_modifier = self.calculate_humidity_factor()
        severity_multiplier = self.get_severity_multiplier()
        
        # Weighted combination
        base_stress = (
            temp_stress * 0.40 +
            expansion_stress * 0.30 +
            duration_stress * 0.30
        )
        
        total_stress = base_stress * humidity_modifier * severity_multiplier
        return min(1.0, total_stress)
    
    def get_info(self) -> Dict:
        """Return heatwave event information"""
        return {
            "event_type": "heatwave",
            "event_name": self.event_name,
            "max_temperature_c": self.max_temperature,
            "min_temperature_c": self.min_temperature,
            "duration_days": self.duration,
            "humidity_percent": self.humidity,
            "solar_radiation_w_m2": round(self.solar_radiation, 1),
            "severity": self.severity,
            "stress_factor": round(self.calculate_stress_factor(), 3),
            "components": {
                "temperature_stress": round(self.calculate_temperature_stress(), 3),
                "thermal_expansion_stress": round(self.calculate_thermal_expansion_stress(), 3),
                "duration_stress": round(self.calculate_duration_stress(), 3),
                "humidity_modifier": round(self.calculate_humidity_factor(), 3)
            }
        }


class HighWindEvent(ClimateEvent):
    """High wind event simulation with wind speed and gust parameters"""
    
    def __init__(
        self,
        sustained_wind_speed: float,  # km/h
        gust_speed: float,  # km/h
        duration: float,  # hours
        severity: str = "moderate",
        wind_direction: str = "variable",  # N, S, E, W, variable
        storm_surge: float = 0,  # meters (for coastal areas)
        event_name: str = "High Wind Event"
    ):
        super().__init__(ClimateEventType.HIGH_WIND, severity, duration)
        self.sustained_wind_speed = sustained_wind_speed
        self.gust_speed = gust_speed
        self.wind_direction = wind_direction
        self.storm_surge = storm_surge
        self.event_name = event_name
    
    def calculate_sustained_wind_stress(self) -> float:
        """Calculate stress from sustained wind speed (0-1 scale)"""
        # Wind speed thresholds (km/h)
        # Moderate: 50-80, High: 80-120, Very high: 120-150, Extreme: 150+
        if self.sustained_wind_speed < 50:
            return 0.2
        elif self.sustained_wind_speed < 80:
            return 0.3 + (self.sustained_wind_speed - 50) / 100
        elif self.sustained_wind_speed < 120:
            return 0.6 + (self.sustained_wind_speed - 80) / 150
        elif self.sustained_wind_speed < 150:
            return 0.85 + (self.sustained_wind_speed - 120) / 200
        else:
            return min(1.0, 1.0)
    
    def calculate_gust_stress(self) -> float:
        """Calculate stress from wind gusts"""
        # Gusts cause dynamic loading and fatigue
        # Critical gust speeds: 100+ km/h significant structural stress
        if self.gust_speed < 80:
            return 0.3
        elif self.gust_speed < 120:
            return 0.5 + (self.gust_speed - 80) / 100
        elif self.gust_speed < 160:
            return 0.75 + (self.gust_speed - 120) / 200
        else:
            return min(1.0, 0.95)
    
    def calculate_duration_factor(self) -> float:
        """Calculate stress from wind event duration"""
        # Fatigue accumulates with time
        # Short: <6 hrs, Medium: 6-24 hrs, Long: 24+ hrs
        if self.duration < 6:
            return 0.75
        elif self.duration < 24:
            return 0.85 + (self.duration - 6) / 60
        else:
            return min(1.0, 0.95 + (self.duration - 24) / 200)
    
    def calculate_storm_surge_factor(self) -> float:
        """Calculate additional stress from storm surge (coastal)"""
        if self.storm_surge < 0.5:
            return 1.0  # No significant surge
        elif self.storm_surge < 2:
            return 1.1 + (self.storm_surge - 0.5) / 10
        else:
            return min(1.3, 1.2 + (self.storm_surge - 2) / 20)
    
    def calculate_stress_factor(self) -> float:
        """Calculate overall wind stress factor"""
        sustained_stress = self.calculate_sustained_wind_stress()
        gust_stress = self.calculate_gust_stress()
        duration_factor = self.calculate_duration_factor()
        surge_factor = self.calculate_storm_surge_factor()
        severity_multiplier = self.get_severity_multiplier()
        
        # Weighted combination
        base_stress = (
            sustained_stress * 0.45 +
            gust_stress * 0.55
        )
        
        total_stress = base_stress * duration_factor * surge_factor * severity_multiplier
        return min(1.0, total_stress)
    
    def get_info(self) -> Dict:
        """Return wind event information"""
        return {
            "event_type": "high_wind",
            "event_name": self.event_name,
            "sustained_wind_speed_kmh": self.sustained_wind_speed,
            "gust_speed_kmh": self.gust_speed,
            "duration_hours": self.duration,
            "wind_direction": self.wind_direction,
            "storm_surge_m": self.storm_surge,
            "severity": self.severity,
            "stress_factor": round(self.calculate_stress_factor(), 3),
            "components": {
                "sustained_wind_stress": round(self.calculate_sustained_wind_stress(), 3),
                "gust_stress": round(self.calculate_gust_stress(), 3),
                "duration_factor": round(self.calculate_duration_factor(), 3),
                "storm_surge_factor": round(self.calculate_storm_surge_factor(), 3)
            }
        }


# Factory function for creating climate events
def create_climate_event(event_config: Dict) -> ClimateEvent:
    """
    Create climate event from configuration dictionary
    
    Args:
        event_config: Dictionary with event parameters
        
    Returns:
        ClimateEvent instance (FloodEvent, HeatwaveEvent, or HighWindEvent)
    """
    event_type = ClimateEventType(event_config["type"])
    
    if event_type == ClimateEventType.FLOOD:
        return FloodEvent(
            rainfall_intensity=event_config.get("rainfall_intensity", 50),
            water_level=event_config.get("water_level", 2),
            duration=event_config.get("duration", 12),
            severity=event_config.get("severity", "moderate"),
            flow_velocity=event_config.get("flow_velocity"),
            event_name=event_config.get("name", "Flood Event")
        )
    elif event_type == ClimateEventType.HEATWAVE:
        return HeatwaveEvent(
            max_temperature=event_config.get("max_temperature", 40),
            min_temperature=event_config.get("min_temperature", 28),
            duration=event_config.get("duration", 5),
            severity=event_config.get("severity", "moderate"),
            humidity=event_config.get("humidity", 50),
            solar_radiation=event_config.get("solar_radiation"),
            event_name=event_config.get("name", "Heatwave Event")
        )
    elif event_type == ClimateEventType.HIGH_WIND:
        return HighWindEvent(
            sustained_wind_speed=event_config.get("sustained_wind_speed", 100),
            gust_speed=event_config.get("gust_speed", 130),
            duration=event_config.get("duration", 8),
            severity=event_config.get("severity", "moderate"),
            wind_direction=event_config.get("wind_direction", "variable"),
            storm_surge=event_config.get("storm_surge", 0),
            event_name=event_config.get("name", "High Wind Event")
        )
    else:
        raise ValueError(f"Unsupported event type: {event_type}")


# Pre-configured scenario templates
CLIMATE_SCENARIOS = {
    "100year_flood": {
        "type": "flood",
        "name": "100-Year Flood",
        "rainfall_intensity": 120,
        "water_level": 4.5,
        "duration": 24,
        "severity": "extreme",
        "flow_velocity": 3.5
    },
    "moderate_flood": {
        "type": "flood",
        "name": "Moderate Flooding",
        "rainfall_intensity": 40,
        "water_level": 1.5,
        "duration": 8,
        "severity": "moderate"
    },
    "extreme_heatwave": {
        "type": "heatwave",
        "name": "Extreme Heatwave",
        "max_temperature": 45,
        "min_temperature": 32,
        "duration": 10,
        "severity": "extreme",
        "humidity": 40
    },
    "moderate_heatwave": {
        "type": "heatwave",
        "name": "Moderate Heatwave",
        "max_temperature": 38,
        "min_temperature": 28,
        "duration": 5,
        "severity": "moderate",
        "humidity": 55
    },
    "hurricane_winds": {
        "type": "high_wind",
        "name": "Hurricane-Force Winds",
        "sustained_wind_speed": 150,
        "gust_speed": 200,
        "duration": 12,
        "severity": "extreme",
        "storm_surge": 3.0
    },
    "severe_storm": {
        "type": "high_wind",
        "name": "Severe Storm",
        "sustained_wind_speed": 90,
        "gust_speed": 120,
        "duration": 6,
        "severity": "high",
        "storm_surge": 0.5
    }
}
