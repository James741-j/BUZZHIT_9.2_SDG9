"""
Stress Analysis and Risk Classification Engine
Combines infrastructure digital twins with climate event simulations to compute
structural stress scores, classify risk levels, and estimate failure probabilities.
"""

from typing import Dict, List, Optional, Tuple
from infrastructure_models import InfrastructureAsset, Bridge, Building, Road, InfrastructureType
from climate_simulator import ClimateEvent, FloodEvent, HeatwaveEvent, HighWindEvent, ClimateEventType


class RiskLevel:
    """Risk classification levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StressAnalyzer:
    """Analyzes infrastructure stress under climate events"""
    
    def __init__(self, infrastructure: InfrastructureAsset, climate_event: ClimateEvent):
        self.infrastructure = infrastructure
        self.climate_event = climate_event
        self.stress_score = 0.0
        self.risk_level = RiskLevel.LOW
        self.failure_probability = 0.0
        self.stress_components = {}
        
    def calculate_infrastructure_vulnerability(self) -> float:
        """
        Calculate infrastructure-specific vulnerability to the climate event
        Returns value 0-1 (0 = not vulnerable, 1 = critically vulnerable)
        """
        vulnerability = 0.0
        
        # Match infrastructure type with climate event type
        if isinstance(self.climate_event, FloodEvent):
            if isinstance(self.infrastructure, Bridge):
                vulnerability = self.infrastructure.calculate_flood_vulnerability(
                    self.climate_event.water_level
                )
            elif isinstance(self.infrastructure, Building):
                vulnerability = self.infrastructure.calculate_flood_vulnerability(
                    self.climate_event.water_level
                )
            elif isinstance(self.infrastructure, Road):
                vulnerability = self.infrastructure.calculate_flood_vulnerability(
                    self.climate_event.water_level,
                    self.climate_event.rainfall_intensity
                )
                
        elif isinstance(self.climate_event, HeatwaveEvent):
            if isinstance(self.infrastructure, Building):
                vulnerability = self.infrastructure.calculate_heat_vulnerability(
                    self.climate_event.max_temperature,
                    int(self.climate_event.duration)
                )
            elif isinstance(self.infrastructure, Road):
                vulnerability = self.infrastructure.calculate_heat_vulnerability(
                    self.climate_event.max_temperature,
                    int(self.climate_event.duration)
                )
            else:
                # Bridges less affected by heat but still thermal expansion stress
                temp_factor = min(1.0, (self.climate_event.max_temperature - 30) / 30)
                vulnerability = temp_factor * 0.4
                
        elif isinstance(self.climate_event, HighWindEvent):
            if isinstance(self.infrastructure, Bridge):
                vulnerability = self.infrastructure.calculate_wind_vulnerability(
                    self.climate_event.sustained_wind_speed
                )
            elif isinstance(self.infrastructure, Building):
                vulnerability = self.infrastructure.calculate_wind_vulnerability(
                    self.climate_event.sustained_wind_speed
                )
            else:
                # Roads less affected by wind except debris and visibility
                vulnerability = min(0.3, self.climate_event.sustained_wind_speed / 400)
        
        return min(1.0, vulnerability)
    
    def calculate_structural_stress_score(self) -> float:
        """
        Calculate overall structural stress score (0-100 scale)
        Combines baseline integrity, climate stress, and asset vulnerability
        """
        # Get baseline structural integrity (0-100, higher is better)
        baseline_integrity = self.infrastructure.calculate_baseline_integrity()
        integrity_factor = 1.0 - (baseline_integrity / 100)  # Convert to stress (inverse)
        
        # Get climate event stress factor (0-1)
        climate_stress = self.climate_event.calculate_stress_factor()
        
        # Get asset-specific vulnerability (0-1)
        asset_vulnerability = self.calculate_infrastructure_vulnerability()
        
        # Age amplification (older assets more vulnerable)
        age_factor = 1.0 / (1.0 + (self.infrastructure.age / 100))  # Normalize
        age_amplifier = 1.0 + (1.0 - age_factor) * 0.5  # Up to 50% amplification
        
        # Combined stress calculation
        # Formula: Base stress × Climate severity × Asset vulnerability × Age amplifier
        base_stress = (
            integrity_factor * 0.3 +  # Current condition
            climate_stress * 0.4 +     # Event severity
            asset_vulnerability * 0.3   # Asset-specific vulnerability
        )
        
        stress_score = base_stress * age_amplifier * 100
        
        # Store components for transparency
        self.stress_components = {
            "baseline_integrity": round(baseline_integrity, 2),
            "integrity_stress_factor": round(integrity_factor, 3),
            "climate_stress_factor": round(climate_stress, 3),
            "asset_vulnerability": round(asset_vulnerability, 3),
            "age_amplifier": round(age_amplifier, 3),
            "base_stress": round(base_stress, 3)
        }
        
        return min(100.0, round(stress_score, 2))
    
    def classify_risk_level(self, stress_score: float) -> str:
        """
        Classify risk level based on stress score
        
        Risk Levels:
        - Low: 0-30 (minor damage possible, normal operation)
        - Medium: 30-60 (moderate damage, reduced capacity)
        - High: 60-85 (major damage, safety concerns)
        - Critical: 85-100 (structural failure likely, immediate action)
        """
        if stress_score < 30:
            return RiskLevel.LOW
        elif stress_score < 60:
            return RiskLevel.MEDIUM
        elif stress_score < 85:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def estimate_failure_probability(self, stress_score: float) -> float:
        """
        Estimate probability of structural failure (0-1 scale)
        Uses logistic function for realistic probability curve
        """
        # Logistic function: P(failure) = 1 / (1 + e^(-k(x - x0)))
        # Where x = stress_score, x0 = midpoint (50), k = steepness (0.08)
        
        import math
        k = 0.08  # Steepness parameter
        x0 = 50   # Midpoint (50% probability at stress score of 50)
        
        # Shift midpoint based on infrastructure age
        # Older infrastructure fails at lower stress levels
        age_penalty = min(30, self.infrastructure.age / 3)  # Up to 30 points penalty
        adjusted_x0 = x0 - age_penalty
        
        probability = 1 / (1 + math.exp(-k * (stress_score - adjusted_x0)))
        
        # Apply material quality modifier
        material_reliability = (
            self.infrastructure.material_properties.corrosion_resistance * 0.5 +
            self.infrastructure.material_properties.water_resistance * 0.5
        )
        adjusted_probability = probability / material_reliability
        
        return min(1.0, round(adjusted_probability, 4))
    
    def generate_stress_insights(self) -> List[str]:
        """Generate human-readable insights about stress factors"""
        insights = []
        
        # Asset age insights
        if self.infrastructure.age > 50:
            insights.append(
                f"⚠️ Asset age ({self.infrastructure.age} years) significantly increases vulnerability"
            )
        elif self.infrastructure.age > 30:
            insights.append(
                f"Asset age ({self.infrastructure.age} years) moderately increases risk"
            )
        
        # Climate event severity insights
        climate_stress = self.climate_event.calculate_stress_factor()
        if climate_stress > 0.8:
            insights.append(
                f"🌪️ Extreme climate event severity (factor: {climate_stress:.2f})"
            )
        elif climate_stress > 0.6:
            insights.append(
                f"⚡ High climate event severity (factor: {climate_stress:.2f})"
            )
        
        # Asset vulnerability insights
        vulnerability = self.calculate_infrastructure_vulnerability()
        if vulnerability > 0.7:
            insights.append(
                f"🏗️ High structural vulnerability to this event type (factor: {vulnerability:.2f})"
            )
        
        # Material-specific insights
        mat_props = self.infrastructure.material_properties
        if isinstance(self.climate_event, FloodEvent):
            if mat_props.water_resistance < 0.5:
                insights.append(
                    f"💧 {mat_props.name} has low water resistance, increasing flood damage risk"
                )
        elif isinstance(self.climate_event, HeatwaveEvent):
            if mat_props.thermal_expansion > 1e-5:
                insights.append(
                    f"🌡️ {mat_props.name} has high thermal expansion, risk of deformation"
                )
        
        # Baseline integrity insights
        integrity = self.infrastructure.calculate_baseline_integrity()
        if integrity < 60:
            insights.append(
                f"🔧 Existing structural condition is degraded (integrity: {integrity:.1f}%)"
            )
        
        return insights
    
    def analyze(self) -> Dict:
        """
        Perform complete stress analysis
        Returns comprehensive analysis results
        """
        # Calculate stress score
        self.stress_score = self.calculate_structural_stress_score()
        
        # Classify risk
        self.risk_level = self.classify_risk_level(self.stress_score)
        
        # Estimate failure probability
        self.failure_probability = self.estimate_failure_probability(self.stress_score)
        
        # Generate insights
        insights = self.generate_stress_insights()
        
        # Compile results
        results = {
            "infrastructure": self.infrastructure.get_info(),
            "climate_event": self.climate_event.get_info(),
            "analysis": {
                "stress_score": self.stress_score,
                "risk_level": self.risk_level,
                "failure_probability": self.failure_probability,
                "failure_probability_percent": round(self.failure_probability * 100, 2)
            },
            "stress_components": self.stress_components,
            "insights": insights,
            "timestamp": self._get_timestamp()
        }
        
        return results
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class RecommendationEngine:
    """Generates actionable recommendations based on stress analysis"""
    
    def __init__(self, analysis_results: Dict):
        self.results = analysis_results
        self.infrastructure_type = analysis_results["infrastructure"]["type"]
        self.climate_event_type = analysis_results["climate_event"]["event_type"]
        self.risk_level = analysis_results["analysis"]["risk_level"]
        self.stress_score = analysis_results["analysis"]["stress_score"]
    
    def generate_recommendations(self) -> List[Dict]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        # Emergency actions for critical risk
        if self.risk_level == RiskLevel.CRITICAL:
            recommendations.append({
                "priority": "CRITICAL",
                "action": "Immediate structural inspection required",
                "description": "Engage certified structural engineers for emergency assessment",
                "timeline": "Within 24 hours",
                "estimated_cost": "$$$$"
            })
            recommendations.append({
                "priority": "CRITICAL",
                "action": "Consider temporary closure/restrictions",
                "description": "Restrict access until safety can be verified",
                "timeline": "Immediate",
                "estimated_cost": "$"
            })
        
        # Asset and event-specific recommendations
        if self.infrastructure_type == "bridge":
            recommendations.extend(self._bridge_recommendations())
        elif self.infrastructure_type == "building":
            recommendations.extend(self._building_recommendations())
        elif self.infrastructure_type == "road":
            recommendations.extend(self._road_recommendations())
        
        # Monitoring recommendations
        if self.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append({
                "priority": "HIGH",
                "action": "Install structural health monitoring system",
                "description": "Deploy sensors to track stress, vibration, and deformation in real-time",
                "timeline": "1-2 months",
                "estimated_cost": "$$$"
            })
        
        return recommendations
    
    def _bridge_recommendations(self) -> List[Dict]:
        """Bridge-specific recommendations"""
        recs = []
        
        if self.climate_event_type == "flood":
            recs.append({
                "priority": "HIGH",
                "action": "Install scour protection",
                "description": "Add riprap or concrete aprons to prevent foundation undermining",
                "timeline": "3-6 months",
                "estimated_cost": "$$$"
            })
            recs.append({
                "priority": "MEDIUM",
                "action": "Improve drainage systems",
                "description": "Enhance deck drainage to prevent water accumulation",
                "timeline": "2-4 months",
                "estimated_cost": "$$"
            })
            if self.stress_score > 70:
                recs.append({
                    "priority": "HIGH",
                    "action": "Strengthen foundation",
                    "description": "Add supplemental piling or extend foundation depth",
                    "timeline": "6-12 months",
                    "estimated_cost": "$$$$"
                })
        
        elif self.climate_event_type == "high_wind":
            recs.append({
                "priority": "HIGH",
                "action": "Add wind bracing",
                "description": "Install cross-bracing and cable stays to reduce wind-induced vibration",
                "timeline": "4-8 months",
                "estimated_cost": "$$$"
            })
            recs.append({
                "priority": "MEDIUM",
                "action": "Aerodynamic modifications",
                "description": "Install wind fairings or modify deck profile",
                "timeline": "6-10 months",
                "estimated_cost": "$$$$"
            })
        
        return recs
    
    def _building_recommendations(self) -> List[Dict]:
        """Building-specific recommendations"""
        recs = []
        
        if self.climate_event_type == "flood":
            recs.append({
                "priority": "HIGH",
                "action": "Install flood barriers",
                "description": "Deploy removable flood panels or permanent water barriers",
                "timeline": "1-3 months",
                "estimated_cost": "$$"
            })
            recs.append({
                "priority": "MEDIUM",
                "action": "Waterproof basement",
                "description": "Apply waterproofing membranes and sealants to foundation",
                "timeline": "2-4 months",
                "estimated_cost": "$$"
            })
            recs.append({
                "priority": "MEDIUM",
                "action": "Elevate critical systems",
                "description": "Move electrical, HVAC equipment above flood level",
                "timeline": "3-6 months",
                "estimated_cost": "$$$"
            })
        
        elif self.climate_event_type == "heatwave":
            recs.append({
                "priority": "HIGH",
                "action": "Upgrade cooling systems",
                "description": "Install or enhance mechanical cooling capacity",
                "timeline": "2-4 months",
                "estimated_cost": "$$$"
            })
            recs.append({
                "priority": "MEDIUM",
                "action": "Apply reflective coating",
                "description": "Cool roof coating to reduce solar heat absorption",
                "timeline": "1-2 months",
                "estimated_cost": "$$"
            })
            recs.append({
                "priority": "MEDIUM",
                "action": "Install thermal insulation",
                "description": "Improve envelope insulation to reduce thermal stress",
                "timeline": "3-5 months",
                "estimated_cost": "$$$"
            })
        
        elif self.climate_event_type == "high_wind":
            recs.append({
                "priority": "HIGH",
                "action": "Reinforce structural connections",
                "description": "Strengthen roof-to-wall and wall-to-foundation connections",
                "timeline": "3-6 months",
                "estimated_cost": "$$$"
            })
            recs.append({
                "priority": "MEDIUM",
                "action": "Install impact-resistant windows",
                "description": "Replace with hurricane-rated glazing systems",
                "timeline": "2-4 months",
                "estimated_cost": "$$$$"
            })
        
        return recs
    
    def _road_recommendations(self) -> List[Dict]:
        """Road-specific recommendations"""
        recs = []
        
        if self.climate_event_type == "flood":
            recs.append({
                "priority": "HIGH",
                "action": "Improve drainage infrastructure",
                "description": "Upgrade storm drains, culverts, and retention basins",
                "timeline": "4-8 months",
                "estimated_cost": "$$$"
            })
            recs.append({
                "priority": "MEDIUM",
                "action": "Elevate roadway sections",
                "description": "Raise critical sections above projected flood levels",
                "timeline": "6-12 months",
                "estimated_cost": "$$$$"
            })
            recs.append({
                "priority": "MEDIUM",
                "action": "Install flood warning systems",
                "description": "Deploy water level sensors and automated signage",
                "timeline": "2-3 months",
                "estimated_cost": "$$"
            })
        
        elif self.climate_event_type == "heatwave":
            recs.append({
                "priority": "HIGH",
                "action": "Apply cool pavement treatment",
                "description": "Use reflective sealants or light-colored aggregates",
                "timeline": "3-5 months",
                "estimated_cost": "$$"
            })
            recs.append({
                "priority": "MEDIUM",
                "action": "Resurface with heat-resistant materials",
                "description": "Use polymer-modified or heat-resistant asphalt mixes",
                "timeline": "6-10 months",
                "estimated_cost": "$$$"
            })
        
        return recs
    
    def estimate_total_cost(self, recommendations: List[Dict]) -> str:
        """Estimate total implementation cost range"""
        cost_map = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
        total_cost_level = sum(cost_map.get(r["estimated_cost"], 2) for r in recommendations)
        
        if total_cost_level < 5:
            return "$10,000 - $50,000"
        elif total_cost_level < 10:
            return "$50,000 - $250,000"
        elif total_cost_level < 15:
            return "$250,000 - $1,000,000"
        else:
            return "$1,000,000+"
    
    def generate_summary_report(self) -> Dict:
        """Generate executive summary with recommendations"""
        recommendations = self.generate_recommendations()
        
        return {
            "asset_id": self.results["infrastructure"]["asset_id"],
            "risk_level": self.risk_level,
            "stress_score": self.stress_score,
            "failure_probability": self.results["analysis"]["failure_probability_percent"],
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "estimated_total_cost": self.estimate_total_cost(recommendations),
            "executive_summary": self._generate_executive_summary()
        }
    
    def _generate_executive_summary(self) -> str:
        """Generate concise executive summary"""
        risk_descriptions = {
            RiskLevel.LOW: "minimal structural concerns",
            RiskLevel.MEDIUM: "moderate vulnerability requiring preventive measures",
            RiskLevel.HIGH: "significant structural risk requiring urgent intervention",
            RiskLevel.CRITICAL: "critical failure risk demanding immediate action"
        }
        
        description = risk_descriptions.get(self.risk_level, "assessment complete")
        
        return (
            f"Analysis reveals {self.risk_level.upper()} risk level with stress score of {self.stress_score:.1f}/100 "
            f"and {self.results['analysis']['failure_probability_percent']:.1f}% failure probability. "
            f"Assessment indicates {description}."
        )
