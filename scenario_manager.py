"""
Scenario Management System
Enables what-if analysis by comparing multiple scenarios with different
climate intensities and infrastructure reinforcement strategies.
"""

from typing import Dict, List, Optional
from copy import deepcopy
from infrastructure_models import InfrastructureAsset, create_infrastructure_asset
from climate_simulator import ClimateEvent, create_climate_event
from stress_analyzer import StressAnalyzer, RecommendationEngine


class ReinforcementStrategy:
    """Represents infrastructure reinforcement/upgrade strategies"""
    
    def __init__(self, name: str, description: str, cost_factor: float = 1.0):
        self.name = name
        self.description = description
        self.cost_factor = cost_factor  # Relative cost multiplier
        self.modifications = {}
    
    def add_modification(self, parameter: str, value: float, operation: str = "multiply"):
        """
        Add a parameter modification
        
        Args:
            parameter: Parameter to modify (e.g., 'load_capacity', 'integrity_boost')
            value: Value to apply
            operation: 'multiply', 'add', or 'set'
        """
        self.modifications[parameter] = {"value": value, "operation": operation}
    
    def apply_to_asset(self, asset: InfrastructureAsset) -> Dict:
        """
        Apply reinforcement strategy to asset (simulated improvements)
        Returns modified parameters for stress calculation adjustment
        """
        adjustments = {}
        
        for param, mod in self.modifications.items():
            adjustments[param] = mod
        
        return adjustments


# Pre-defined reinforcement strategies
REINFORCEMENT_STRATEGIES = {
    # Bridge strategies
    "bridge_foundation_strengthening": ReinforcementStrategy(
        name="Foundation Strengthening",
        description="Add supplemental piling and scour protection",
        cost_factor=2.5
    ),
    "bridge_wind_bracing": ReinforcementStrategy(
        name="Wind Bracing Installation",
        description="Add cross-bracing and cable stays",
        cost_factor=1.8
    ),
    "bridge_deck_rehabilitation": ReinforcementStrategy(
        name="Deck Rehabilitation",
        description="Replace deteriorated deck and improve drainage",
        cost_factor=2.0
    ),
    
    # Building strategies
    "building_flood_barriers": ReinforcementStrategy(
        name="Flood Barrier System",
        description="Install removable flood panels and waterproofing",
        cost_factor=1.5
    ),
    "building_cooling_upgrade": ReinforcementStrategy(
        name="Enhanced Cooling System",
        description="Upgrade HVAC and install reflective coating",
        cost_factor=1.7
    ),
    "building_structural_reinforcement": ReinforcementStrategy(
        name="Structural Reinforcement",
        description="Strengthen connections and add wind bracing",
        cost_factor=2.2
    ),
    
    # Road strategies
    "road_drainage_improvement": ReinforcementStrategy(
        name="Drainage System Upgrade",
        description="Enhance storm drains and retention capacity",
        cost_factor=1.6
    ),
    "road_heat_resistant_surface": ReinforcementStrategy(
        name="Heat-Resistant Surfacing",
        description="Apply cool pavement treatment and polymer-modified asphalt",
        cost_factor=1.4
    ),
    "road_elevation": ReinforcementStrategy(
        name="Roadway Elevation",
        description="Raise critical sections above flood levels",
        cost_factor=3.0
    )
}

# Configure strategy modifications
REINFORCEMENT_STRATEGIES["bridge_foundation_strengthening"].add_modification("flood_resistance", 0.6, "multiply")
REINFORCEMENT_STRATEGIES["bridge_foundation_strengthening"].add_modification("integrity_boost", 15, "add")

REINFORCEMENT_STRATEGIES["bridge_wind_bracing"].add_modification("wind_resistance", 0.5, "multiply")
REINFORCEMENT_STRATEGIES["bridge_wind_bracing"].add_modification("integrity_boost", 10, "add")

REINFORCEMENT_STRATEGIES["bridge_deck_rehabilitation"].add_modification("overall_resistance", 0.7, "multiply")
REINFORCEMENT_STRATEGIES["bridge_deck_rehabilitation"].add_modification("integrity_boost", 20, "add")

REINFORCEMENT_STRATEGIES["building_flood_barriers"].add_modification("flood_resistance", 0.5, "multiply")
REINFORCEMENT_STRATEGIES["building_flood_barriers"].add_modification("integrity_boost", 12, "add")

REINFORCEMENT_STRATEGIES["building_cooling_upgrade"].add_modification("heat_resistance", 0.4, "multiply")
REINFORCEMENT_STRATEGIES["building_cooling_upgrade"].add_modification("integrity_boost", 8, "add")

REINFORCEMENT_STRATEGIES["building_structural_reinforcement"].add_modification("wind_resistance", 0.55, "multiply")
REINFORCEMENT_STRATEGIES["building_structural_reinforcement"].add_modification("integrity_boost", 15, "add")

REINFORCEMENT_STRATEGIES["road_drainage_improvement"].add_modification("flood_resistance", 0.45, "multiply")
REINFORCEMENT_STRATEGIES["road_drainage_improvement"].add_modification("integrity_boost", 10, "add")

REINFORCEMENT_STRATEGIES["road_heat_resistant_surface"].add_modification("heat_resistance", 0.5, "multiply")
REINFORCEMENT_STRATEGIES["road_heat_resistant_surface"].add_modification("integrity_boost", 10, "add")

REINFORCEMENT_STRATEGIES["road_elevation"].add_modification("flood_resistance", 0.3, "multiply")
REINFORCEMENT_STRATEGIES["road_elevation"].add_modification("integrity_boost", 18, "add")


class Scenario:
    """Represents a complete scenario: infrastructure + climate event + optional reinforcement"""
    
    def __init__(
        self,
        scenario_id: str,
        name: str,
        infrastructure_config: Dict,
        climate_event_config: Dict,
        reinforcement_strategies: Optional[List[str]] = None,
        description: str = ""
    ):
        self.scenario_id = scenario_id
        self.name = name
        self.description = description
        self.infrastructure_config = infrastructure_config
        self.climate_event_config = climate_event_config
        self.reinforcement_strategy_names = reinforcement_strategies or []
        
        # Create infrastructure and climate event objects
        self.infrastructure = create_infrastructure_asset(infrastructure_config)
        self.climate_event = create_climate_event(climate_event_config)
        
        # Apply reinforcement strategies
        self.applied_reinforcements = []
        if self.reinforcement_strategy_names:
            for strategy_name in self.reinforcement_strategy_names:
                if strategy_name in REINFORCEMENT_STRATEGIES:
                    self.applied_reinforcements.append(REINFORCEMENT_STRATEGIES[strategy_name])
        
        self.analysis_results = None
    
    def run_analysis(self) -> Dict:
        """Run stress analysis for this scenario"""
        # Create analyzer
        analyzer = StressAnalyzer(self.infrastructure, self.climate_event)
        
        # Get base analysis
        results = analyzer.analyze()
        
        # Apply reinforcement adjustments
        if self.applied_reinforcements:
            results = self._apply_reinforcement_benefits(results)
        
        # Generate recommendations
        rec_engine = RecommendationEngine(results)
        recommendations = rec_engine.generate_summary_report()
        
        results["recommendations_summary"] = recommendations
        results["scenario_info"] = {
            "scenario_id": self.scenario_id,
            "scenario_name": self.name,
            "description": self.description,
            "reinforcements_applied": [r.name for r in self.applied_reinforcements]
        }
        
        self.analysis_results = results
        return results
    
    def _apply_reinforcement_benefits(self, base_results: Dict) -> Dict:
        """Apply benefits from reinforcement strategies to analysis results"""
        results = deepcopy(base_results)
        
        # Calculate total stress reduction and integrity boost
        total_stress_reduction = 0
        total_integrity_boost = 0
        total_cost_factor = 0
        
        for strategy in self.applied_reinforcements:
            total_cost_factor += strategy.cost_factor
            
            # Apply modifications based on climate event type
            for param, mod in strategy.modifications.items():
                if param == "integrity_boost" and mod["operation"] == "add":
                    total_integrity_boost += mod["value"]
                elif "resistance" in param and mod["operation"] == "multiply":
                    # Resistance improvements reduce stress
                    total_stress_reduction += (1 - mod["value"]) * 20  # Scale to stress points
        
        # Apply stress reduction (cap at 40% reduction for realism)
        original_stress = base_results["analysis"]["stress_score"]
        stress_reduction_factor = min(0.4, total_stress_reduction / 100)
        adjusted_stress = original_stress * (1 - stress_reduction_factor)
        
        # Apply integrity boost
        original_integrity = base_results["infrastructure"]["baseline_integrity"]
        adjusted_integrity = min(100, original_integrity + total_integrity_boost)
        
        # Recalculate risk and failure probability
        results["analysis"]["stress_score_original"] = original_stress
        results["analysis"]["stress_score"] = round(adjusted_stress, 2)
        results["analysis"]["stress_reduction_percent"] = round(stress_reduction_factor * 100, 1)
        
        # Recalculate risk level
        analyzer = StressAnalyzer(self.infrastructure, self.climate_event)
        results["analysis"]["risk_level"] = analyzer.classify_risk_level(adjusted_stress)
        results["analysis"]["failure_probability"] = analyzer.estimate_failure_probability(adjusted_stress)
        results["analysis"]["failure_probability_percent"] = round(
            results["analysis"]["failure_probability"] * 100, 2
        )
        
        results["infrastructure"]["baseline_integrity_original"] = original_integrity
        results["infrastructure"]["baseline_integrity"] = adjusted_integrity
        
        results["reinforcement_impact"] = {
            "strategies_applied": len(self.applied_reinforcements),
            "estimated_cost_factor": round(total_cost_factor, 2),
            "stress_reduction": f"{stress_reduction_factor * 100:.1f}%",
            "integrity_improvement": f"+{total_integrity_boost} points"
        }
        
        return results


class ScenarioManager:
    """Manages multiple scenarios and enables comparison analysis"""
    
    def __init__(self):
        self.scenarios = {}
    
    def add_scenario(self, scenario: Scenario) -> None:
        """Add a scenario to the manager"""
        self.scenarios[scenario.scenario_id] = scenario
    
    def run_all_scenarios(self) -> Dict[str, Dict]:
        """Run analysis for all scenarios"""
        results = {}
        for scenario_id, scenario in self.scenarios.items():
            results[scenario_id] = scenario.run_analysis()
        return results
    
    def compare_scenarios(self, scenario_ids: Optional[List[str]] = None) -> Dict:
        """
        Compare multiple scenarios side-by-side
        
        Args:
            scenario_ids: List of scenario IDs to compare (None = all scenarios)
        
        Returns:
            Comparison report with key metrics
        """
        if scenario_ids is None:
            scenario_ids = list(self.scenarios.keys())
        
        # Run analysis for selected scenarios
        scenario_results = {}
        for sid in scenario_ids:
            if sid in self.scenarios:
                scenario_results[sid] = self.scenarios[sid].run_analysis()
        
        if not scenario_results:
            return {"error": "No valid scenarios to compare"}
        
        # Extract key metrics for comparison
        comparison = {
            "scenarios": [],
            "comparison_chart_data": {
                "scenario_names": [],
                "stress_scores": [],
                "failure_probabilities": [],
                "risk_levels": []
            },
            "best_scenario": None,
            "cost_benefit_analysis": []
        }
        
        for sid, results in scenario_results.items():
            scenario_info = {
                "scenario_id": sid,
                "scenario_name": results["scenario_info"]["scenario_name"],
                "stress_score": results["analysis"]["stress_score"],
                "risk_level": results["analysis"]["risk_level"],
                "failure_probability": results["analysis"]["failure_probability_percent"],
                "reinforcements": results["scenario_info"]["reinforcements_applied"],
                "cost_factor": results.get("reinforcement_impact", {}).get("estimated_cost_factor", 0)
            }
            
            comparison["scenarios"].append(scenario_info)
            comparison["comparison_chart_data"]["scenario_names"].append(scenario_info["scenario_name"])
            comparison["comparison_chart_data"]["stress_scores"].append(scenario_info["stress_score"])
            comparison["comparison_chart_data"]["failure_probabilities"].append(scenario_info["failure_probability"])
            comparison["comparison_chart_data"]["risk_levels"].append(scenario_info["risk_level"])
        
        # Identify best scenario (lowest stress score)
        best = min(comparison["scenarios"], key=lambda x: x["stress_score"])
        comparison["best_scenario"] = {
            "name": best["scenario_name"],
            "stress_score": best["stress_score"],
            "risk_level": best["risk_level"],
            "improvement_over_baseline": self._calculate_improvement(comparison["scenarios"], best)
        }
        
        # Cost-benefit analysis
        baseline = next((s for s in comparison["scenarios"] if not s["reinforcements"]), None)
        if baseline:
            for scenario in comparison["scenarios"]:
                if scenario["scenario_id"] != baseline["scenario_id"]:
                    risk_reduction = baseline["failure_probability"] - scenario["failure_probability"]
                    cost = scenario["cost_factor"]
                    cost_effectiveness = risk_reduction / cost if cost > 0 else 0
                    
                    comparison["cost_benefit_analysis"].append({
                        "scenario": scenario["scenario_name"],
                        "cost_factor": cost,
                        "risk_reduction_percent": round(risk_reduction, 2),
                        "cost_effectiveness_score": round(cost_effectiveness, 3)
                    })
        
        return comparison
    
    def _calculate_improvement(self, all_scenarios: List[Dict], best_scenario: Dict) -> str:
        """Calculate improvement of best scenario over baseline"""
        baseline = next((s for s in all_scenarios if not s["reinforcements"]), None)
        if not baseline:
            return "N/A"
        
        stress_improvement = baseline["stress_score"] - best_scenario["stress_score"]
        failure_improvement = baseline["failure_probability"] - best_scenario["failure_probability"]
        
        return f"{stress_improvement:.1f} stress points, {failure_improvement:.1f}% failure probability"
    
    def generate_comparison_summary(self, comparison_results: Dict) -> str:
        """Generate executive summary of scenario comparison"""
        if "error" in comparison_results:
            return comparison_results["error"]
        
        num_scenarios = len(comparison_results["scenarios"])
        best = comparison_results["best_scenario"]
        
        summary = f"Compared {num_scenarios} scenarios. "
        summary += f"Optimal scenario: '{best['name']}' with {best['stress_score']:.1f} stress score "
        summary += f"({best['risk_level'].upper()} risk). "
        
        if best["improvement_over_baseline"] != "N/A":
            summary += f"Improvements: {best['improvement_over_baseline']}."
        
        # Cost-effectiveness insight
        if comparison_results["cost_benefit_analysis"]:
            top_cost_effective = max(
                comparison_results["cost_benefit_analysis"],
                key=lambda x: x["cost_effectiveness_score"]
            )
            summary += f" Most cost-effective: '{top_cost_effective['scenario']}'."
        
        return summary
