"""
Digital Twin Models for Infrastructure Assets
Defines base classes and specialized infrastructure types with material properties,
structural parameters, and climate stress calculations.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional
import math


class MaterialType(Enum):
    """Common construction materials with their properties"""
    STEEL = "steel"
    CONCRETE = "concrete"
    REINFORCED_CONCRETE = "reinforced_concrete"
    WOOD = "wood"
    MASONRY = "masonry"
    COMPOSITE = "composite"


class InfrastructureType(Enum):
    """Supported infrastructure asset types"""
    BRIDGE = "bridge"
    BUILDING = "building"
    ROAD = "road"


@dataclass
class MaterialProperties:
    """Physical properties of construction materials"""
    name: str
    tensile_strength: float  # MPa
    compressive_strength: float  # MPa
    thermal_expansion: float  # per °C
    corrosion_resistance: float  # 0-1 scale
    water_resistance: float  # 0-1 scale
    density: float  # kg/m³


# Material database
MATERIAL_DATABASE = {
    MaterialType.STEEL: MaterialProperties(
        name="Steel",
        tensile_strength=400,
        compressive_strength=400,
        thermal_expansion=1.2e-5,
        corrosion_resistance=0.4,
        water_resistance=0.3,
        density=7850
    ),
    MaterialType.CONCRETE: MaterialProperties(
        name="Concrete",
        tensile_strength=3,
        compressive_strength=30,
        thermal_expansion=1.0e-5,
        corrosion_resistance=0.7,
        water_resistance=0.6,
        density=2400
    ),
    MaterialType.REINFORCED_CONCRETE: MaterialProperties(
        name="Reinforced Concrete",
        tensile_strength=25,
        compressive_strength=40,
        thermal_expansion=1.0e-5,
        corrosion_resistance=0.6,
        water_resistance=0.7,
        density=2500
    ),
    MaterialType.WOOD: MaterialProperties(
        name="Wood",
        tensile_strength=100,
        compressive_strength=50,
        thermal_expansion=5.0e-6,
        corrosion_resistance=0.3,
        water_resistance=0.2,
        density=600
    ),
    MaterialType.MASONRY: MaterialProperties(
        name="Masonry",
        tensile_strength=2,
        compressive_strength=15,
        thermal_expansion=8.0e-6,
        corrosion_resistance=0.8,
        water_resistance=0.5,
        density=1800
    ),
    MaterialType.COMPOSITE: MaterialProperties(
        name="Composite",
        tensile_strength=600,
        compressive_strength=200,
        thermal_expansion=2.0e-6,
        corrosion_resistance=0.9,
        water_resistance=0.9,
        density=1600
    )
}


class InfrastructureAsset:
    """Base class for all infrastructure digital twins"""
    
    def __init__(
        self,
        asset_id: str,
        asset_type: InfrastructureType,
        material: MaterialType,
        age: int,  # years
        location: str,
        latitude: float = 0.0,
        longitude: float = 0.0
    ):
        self.asset_id = asset_id
        self.asset_type = asset_type
        self.material = material
        self.age = age
        self.location = location
        self.latitude = latitude
        self.longitude = longitude
        self.material_properties = MATERIAL_DATABASE[material]
        
    def calculate_age_degradation_factor(self) -> float:
        """Calculate structural degradation based on age (0-1 scale, 1 = no degradation)"""
        # Exponential decay model: degradation increases with age
        # 50-year half-life for typical infrastructure
        half_life = 50
        degradation_factor = math.exp(-0.693 * self.age / half_life)
        return max(0.3, degradation_factor)  # Minimum 30% capacity retained
    
    def calculate_baseline_integrity(self) -> float:
        """Calculate current structural integrity (0-100 scale)"""
        age_factor = self.calculate_age_degradation_factor()
        material_factor = (
            self.material_properties.corrosion_resistance * 0.4 +
            self.material_properties.water_resistance * 0.3 +
            0.3  # Base material quality
        )
        integrity = age_factor * material_factor * 100
        return round(integrity, 2)
    
    def get_info(self) -> Dict:
        """Return asset information as dictionary"""
        return {
            "asset_id": self.asset_id,
            "type": self.asset_type.value,
            "material": self.material.value,
            "age": self.age,
            "location": self.location,
            "baseline_integrity": self.calculate_baseline_integrity(),
            "age_degradation": round(self.calculate_age_degradation_factor(), 3)
        }


class Bridge(InfrastructureAsset):
    """Digital twin model for bridge infrastructure"""
    
    def __init__(
        self,
        asset_id: str,
        material: MaterialType,
        age: int,
        location: str,
        span_length: float,  # meters
        height_above_water: float,  # meters
        load_capacity: float,  # tons
        foundation_type: str = "pile",  # pile, spread, caisson
        latitude: float = 0.0,
        longitude: float = 0.0
    ):
        super().__init__(asset_id, InfrastructureType.BRIDGE, material, age, location, latitude, longitude)
        self.span_length = span_length
        self.height_above_water = height_above_water
        self.load_capacity = load_capacity
        self.foundation_type = foundation_type
    
    def calculate_flood_vulnerability(self, water_level: float) -> float:
        """Calculate vulnerability to flooding (0-1 scale, 1 = critical)"""
        # Water approaching or exceeding bridge height
        clearance = self.height_above_water - water_level
        
        if clearance <= 0:
            # Water above bridge deck
            vulnerability = 1.0
        elif clearance < 2:
            # Critical clearance zone
            vulnerability = 0.8 + (2 - clearance) * 0.1
        else:
            # Safe clearance
            vulnerability = min(0.8, 1 / clearance)
        
        # Foundation vulnerability
        if self.foundation_type == "pile":
            foundation_factor = 0.7  # More resistant to scour
        elif self.foundation_type == "spread":
            foundation_factor = 1.2  # Vulnerable to undermining
        else:
            foundation_factor = 1.0
        
        return min(1.0, vulnerability * foundation_factor)
    
    def calculate_wind_vulnerability(self, wind_speed: float) -> float:
        """Calculate vulnerability to high winds (0-1 scale)"""
        # Longer spans more vulnerable to wind
        span_factor = min(1.0, self.span_length / 500)  # Normalize to 500m
        
        # Critical wind speeds for bridges: 80+ km/h significant, 150+ km/h critical
        if wind_speed < 80:
            wind_factor = 0.1
        elif wind_speed < 120:
            wind_factor = 0.3 + (wind_speed - 80) / 80
        else:
            wind_factor = min(1.0, 0.8 + (wind_speed - 120) / 150)
        
        return span_factor * wind_factor
    
    def get_info(self) -> Dict:
        """Extended bridge information"""
        base_info = super().get_info()
        base_info.update({
            "span_length_m": self.span_length,
            "height_above_water_m": self.height_above_water,
            "load_capacity_tons": self.load_capacity,
            "foundation_type": self.foundation_type
        })
        return base_info


class Building(InfrastructureAsset):
    """Digital twin model for building infrastructure"""
    
    def __init__(
        self,
        asset_id: str,
        material: MaterialType,
        age: int,
        location: str,
        floors: int,
        height: float,  # meters
        floor_area: float,  # square meters
        foundation_depth: float,  # meters
        has_basement: bool = False,
        cooling_system: str = "mechanical",  # mechanical, natural, none
        latitude: float = 0.0,
        longitude: float = 0.0
    ):
        super().__init__(asset_id, InfrastructureType.BUILDING, material, age, location, latitude, longitude)
        self.floors = floors
        self.height = height
        self.floor_area = floor_area
        self.foundation_depth = foundation_depth
        self.has_basement = has_basement
        self.cooling_system = cooling_system
    
    def calculate_flood_vulnerability(self, water_level: float) -> float:
        """Calculate building flood vulnerability"""
        # Basement vulnerability
        if self.has_basement and water_level > 0:
            basement_vulnerability = min(1.0, water_level / 3)  # 3m critical depth
        else:
            basement_vulnerability = 0
        
        # Ground floor vulnerability
        if water_level > 0.5:
            ground_floor_vulnerability = min(1.0, water_level / 2)
        else:
            ground_floor_vulnerability = 0
        
        # Foundation undermining risk
        if water_level > self.foundation_depth:
            foundation_risk = 0.8
        else:
            foundation_risk = 0.2
        
        total_vulnerability = (
            basement_vulnerability * 0.3 +
            ground_floor_vulnerability * 0.4 +
            foundation_risk * 0.3
        )
        
        return min(1.0, total_vulnerability)
    
    def calculate_heat_vulnerability(self, temperature: float, duration_days: int) -> float:
        """Calculate vulnerability to extreme heat"""
        # Critical temperature thresholds
        if temperature < 35:
            temp_factor = 0.1
        elif temperature < 40:
            temp_factor = 0.3 + (temperature - 35) / 10
        else:
            temp_factor = min(1.0, 0.8 + (temperature - 40) / 20)
        
        # Duration amplifies impact
        duration_factor = min(1.0, 0.5 + duration_days / 20)
        
        # Cooling system mitigation
        cooling_factors = {
            "mechanical": 0.4,
            "natural": 0.7,
            "none": 1.0
        }
        cooling_factor = cooling_factors.get(self.cooling_system, 1.0)
        
        # Material thermal stress
        thermal_expansion = self.material_properties.thermal_expansion
        thermal_stress = min(1.0, thermal_expansion * 1e6)  # Normalize
        
        vulnerability = temp_factor * duration_factor * cooling_factor * thermal_stress
        return min(1.0, vulnerability)
    
    def calculate_wind_vulnerability(self, wind_speed: float) -> float:
        """Calculate building wind vulnerability"""
        # Height factor: taller buildings more vulnerable
        height_factor = min(1.0, self.height / 100)  # Normalize to 100m
        
        # Wind load calculation
        if wind_speed < 100:
            wind_factor = 0.1
        elif wind_speed < 150:
            wind_factor = 0.3 + (wind_speed - 100) / 100
        else:
            wind_factor = min(1.0, 0.8 + (wind_speed - 150) / 100)
        
        # Material structural rigidity
        material_factors = {
            MaterialType.STEEL: 0.5,
            MaterialType.REINFORCED_CONCRETE: 0.6,
            MaterialType.CONCRETE: 0.8,
            MaterialType.MASONRY: 1.0,
            MaterialType.WOOD: 0.9,
            MaterialType.COMPOSITE: 0.4
        }
        material_factor = material_factors.get(self.material, 0.7)
        
        return height_factor * wind_factor * material_factor
    
    def get_info(self) -> Dict:
        """Extended building information"""
        base_info = super().get_info()
        base_info.update({
            "floors": self.floors,
            "height_m": self.height,
            "floor_area_sqm": self.floor_area,
            "has_basement": self.has_basement,
            "cooling_system": self.cooling_system
        })
        return base_info


class Road(InfrastructureAsset):
    """Digital twin model for road infrastructure"""
    
    def __init__(
        self,
        asset_id: str,
        material: MaterialType,
        age: int,
        location: str,
        length: float,  # kilometers
        width: float,  # meters
        traffic_volume: int,  # vehicles per day
        drainage_quality: str = "good",  # excellent, good, fair, poor
        elevation: float = 0.0,  # meters above sea level
        latitude: float = 0.0,
        longitude: float = 0.0
    ):
        super().__init__(asset_id, InfrastructureType.ROAD, material, age, location, latitude, longitude)
        self.length = length
        self.width = width
        self.traffic_volume = traffic_volume
        self.drainage_quality = drainage_quality
        self.elevation = elevation
    
    def calculate_flood_vulnerability(self, water_level: float, rainfall_intensity: float) -> float:
        """Calculate road flood vulnerability"""
        # Drainage capacity
        drainage_factors = {
            "excellent": 0.3,
            "good": 0.6,
            "fair": 0.8,
            "poor": 1.0
        }
        drainage_factor = drainage_factors.get(self.drainage_quality, 0.8)
        
        # Water accumulation based on rainfall
        if rainfall_intensity < 20:
            rain_factor = 0.2
        elif rainfall_intensity < 50:
            rain_factor = 0.4 + (rainfall_intensity - 20) / 60
        else:
            rain_factor = min(1.0, 0.9 + (rainfall_intensity - 50) / 100)
        
        # Standing water depth vulnerability
        if water_level > 0.3:  # 30cm critical for vehicle passage
            water_factor = 1.0
        elif water_level > 0.15:
            water_factor = 0.7
        else:
            water_factor = 0.3
        
        vulnerability = rain_factor * drainage_factor * water_factor
        return min(1.0, vulnerability)
    
    def calculate_heat_vulnerability(self, temperature: float, duration_days: int) -> float:
        """Calculate road heat vulnerability (thermal expansion, rutting)"""
        # Asphalt is highly vulnerable to heat
        if self.material == MaterialType.CONCRETE:
            material_heat_factor = 0.5
        else:  # Asphalt or other
            material_heat_factor = 1.0
        
        # Temperature stress
        if temperature < 35:
            temp_factor = 0.1
        elif temperature < 45:
            temp_factor = 0.4 + (temperature - 35) / 25
        else:
            temp_factor = min(1.0, 0.8 + (temperature - 45) / 30)
        
        # Duration causes rutting and deformation
        duration_factor = min(1.0, 0.3 + duration_days / 15)
        
        # High traffic amplifies thermal damage
        if self.traffic_volume > 50000:
            traffic_factor = 1.2
        elif self.traffic_volume > 20000:
            traffic_factor = 1.0
        else:
            traffic_factor = 0.8
        
        vulnerability = material_heat_factor * temp_factor * duration_factor * traffic_factor
        return min(1.0, vulnerability)
    
    def get_info(self) -> Dict:
        """Extended road information"""
        base_info = super().get_info()
        base_info.update({
            "length_km": self.length,
            "width_m": self.width,
            "traffic_volume_vpd": self.traffic_volume,
            "drainage_quality": self.drainage_quality,
            "elevation_m": self.elevation
        })
        return base_info


# Factory function for creating infrastructure assets
def create_infrastructure_asset(asset_config: Dict) -> InfrastructureAsset:
    """
    Create infrastructure asset from configuration dictionary
    
    Args:
        asset_config: Dictionary with asset parameters
        
    Returns:
        InfrastructureAsset instance (Bridge, Building, or Road)
    """
    asset_type = InfrastructureType(asset_config["type"])
    material = MaterialType(asset_config["material"])
    
    if asset_type == InfrastructureType.BRIDGE:
        return Bridge(
            asset_id=asset_config["id"],
            material=material,
            age=asset_config["age"],
            location=asset_config["location"],
            span_length=asset_config.get("span_length", 100),
            height_above_water=asset_config.get("height_above_water", 10),
            load_capacity=asset_config.get("load_capacity", 50),
            foundation_type=asset_config.get("foundation_type", "pile"),
            latitude=asset_config.get("latitude", 0.0),
            longitude=asset_config.get("longitude", 0.0)
        )
    elif asset_type == InfrastructureType.BUILDING:
        return Building(
            asset_id=asset_config["id"],
            material=material,
            age=asset_config["age"],
            location=asset_config["location"],
            floors=asset_config.get("floors", 5),
            height=asset_config.get("height", 15),
            floor_area=asset_config.get("floor_area", 1000),
            foundation_depth=asset_config.get("foundation_depth", 3),
            has_basement=asset_config.get("has_basement", False),
            cooling_system=asset_config.get("cooling_system", "mechanical"),
            latitude=asset_config.get("latitude", 0.0),
            longitude=asset_config.get("longitude", 0.0)
        )
    elif asset_type == InfrastructureType.ROAD:
        return Road(
            asset_id=asset_config["id"],
            material=material,
            age=asset_config["age"],
            location=asset_config["location"],
            length=asset_config.get("length", 5),
            width=asset_config.get("width", 10),
            traffic_volume=asset_config.get("traffic_volume", 10000),
            drainage_quality=asset_config.get("drainage_quality", "good"),
            elevation=asset_config.get("elevation", 0),
            latitude=asset_config.get("latitude", 0.0),
            longitude=asset_config.get("longitude", 0.0)
        )
    else:
        raise ValueError(f"Unsupported asset type: {asset_type}")
