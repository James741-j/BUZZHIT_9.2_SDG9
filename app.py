"""
Flask Backend API for Digital Twin Climate Simulator
Provides REST API endpoints for infrastructure digital twin creation,
climate event simulation, stress analysis, and scenario comparison.
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import json
from typing import Dict, List
import os

from infrastructure_models import create_infrastructure_asset, MaterialType, InfrastructureType
from climate_simulator import create_climate_event, CLIMATE_SCENARIOS
from stress_analyzer import StressAnalyzer, RecommendationEngine
from scenario_manager import Scenario, ScenarioManager, REINFORCEMENT_STRATEGIES

app = Flask(__name__, static_folder='static', template_folder='static')
CORS(app)  # Enable CORS for API access

# Global scenario manager
scenario_manager = ScenarioManager()


@app.route('/')
def index():
    """Serve the main dashboard"""
    return render_template('dashboard.html')


@app.route('/api/materials', methods=['GET'])
def get_materials():
    """Get list of available materials"""
    materials = [
        {
            "value": mat.value,
            "name": mat.value.replace('_', ' ').title(),
            "properties": {
                "tensile_strength": f"{mat.value} MPa",
                "corrosion_resistance": "rating"
            }
        }
        for mat in MaterialType
    ]
    return jsonify({"materials": materials})


@app.route('/api/infrastructure-types', methods=['GET'])
def get_infrastructure_types():
    """Get list of infrastructure types"""
    types = [
        {
            "value": itype.value,
            "name": itype.value.title(),
            "description": f"{itype.value.title()} infrastructure asset"
        }
        for itype in InfrastructureType
    ]
    return jsonify({"types": types})


@app.route('/api/climate-scenarios', methods=['GET'])
def get_climate_scenarios():
    """Get list of pre-configured climate scenarios"""
    scenarios = [
        {
            "id": key,
            "name": value["name"],
            "type": value["type"],
            "severity": value.get("severity", "moderate")
        }
        for key, value in CLIMATE_SCENARIOS.items()
    ]
    return jsonify({"scenarios": scenarios})


@app.route('/api/reinforcement-strategies', methods=['GET'])
def get_reinforcement_strategies():
    """Get list of available reinforcement strategies"""
    strategies = [
        {
            "id": key,
            "name": strategy.name,
            "description": strategy.description,
            "cost_factor": strategy.cost_factor
        }
        for key, strategy in REINFORCEMENT_STRATEGIES.items()
    ]
    return jsonify({"strategies": strategies})


@app.route('/api/create-twin', methods=['POST'])
def create_digital_twin():
    """
    Create a digital twin of infrastructure asset
    
    Request body:
    {
        "id": "asset-001",
        "type": "bridge",
        "material": "steel",
        "age": 40,
        "location": "Coastal City",
        ... (type-specific parameters)
    }
    """
    try:
        config = request.json
        
        # Validate required fields
        required_fields = ["id", "type", "material", "age", "location"]
        for field in required_fields:
            if field not in config:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create infrastructure asset
        asset = create_infrastructure_asset(config)
        
        # Return asset information
        return jsonify({
            "success": True,
            "asset": asset.get_info(),
            "message": f"Digital twin created successfully for {asset.asset_type.value}"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/simulate-event', methods=['POST'])
def simulate_climate_event():
    """
    Simulate climate event on infrastructure
    
    Request body:
    {
        "infrastructure": {...},
        "climate_event": {...}
    }
    """
    try:
        data = request.json
        
        # Create infrastructure and climate event
        infrastructure = create_infrastructure_asset(data["infrastructure"])
        climate_event = create_climate_event(data["climate_event"])
        
        # Run stress analysis
        analyzer = StressAnalyzer(infrastructure, climate_event)
        results = analyzer.analyze()
        
        # Generate recommendations
        rec_engine = RecommendationEngine(results)
        recommendations = rec_engine.generate_summary_report()
        
        # Combine results
        response = {
            "success": True,
            "analysis": results,
            "recommendations": recommendations
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/create-scenario', methods=['POST'])
def create_scenario():
    """
    Create a scenario for what-if analysis
    
    Request body:
    {
        "scenario_id": "scenario-1",
        "name": "Baseline",
        "infrastructure": {...},
        "climate_event": {...},
        "reinforcements": ["bridge_foundation_strengthening"]
    }
    """
    try:
        data = request.json
        
        scenario = Scenario(
            scenario_id=data["scenario_id"],
            name=data["name"],
            infrastructure_config=data["infrastructure"],
            climate_event_config=data["climate_event"],
            reinforcement_strategies=data.get("reinforcements", []),
            description=data.get("description", "")
        )
        
        # Add to scenario manager
        scenario_manager.add_scenario(scenario)
        
        # Run analysis
        results = scenario.run_analysis()
        
        return jsonify({
            "success": True,
            "scenario_id": data["scenario_id"],
            "results": results
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/compare-scenarios', methods=['POST'])
def compare_scenarios():
    """
    Compare multiple scenarios
    
    Request body:
    {
        "scenarios": [
            {"scenario_id": "baseline", ...},
            {"scenario_id": "reinforced", ...}
        ]
    }
    """
    try:
        data = request.json
        
        # Clear existing scenarios and add new ones
        scenario_manager.scenarios.clear()
        
        scenario_ids = []
        for scenario_data in data["scenarios"]:
            scenario = Scenario(
                scenario_id=scenario_data["scenario_id"],
                name=scenario_data["name"],
                infrastructure_config=scenario_data["infrastructure"],
                climate_event_config=scenario_data["climate_event"],
                reinforcement_strategies=scenario_data.get("reinforcements", []),
                description=scenario_data.get("description", "")
            )
            scenario_manager.add_scenario(scenario)
            scenario_ids.append(scenario_data["scenario_id"])
        
        # Run comparison
        comparison = scenario_manager.compare_scenarios(scenario_ids)
        summary = scenario_manager.generate_comparison_summary(comparison)
        
        return jsonify({
            "success": True,
            "comparison": comparison,
            "summary": summary
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/quick-analysis', methods=['POST'])
def quick_analysis():
    """
    Quick analysis endpoint combining twin creation and simulation
    Simplified API for rapid testing
    """
    try:
        data = request.json
        
        # Create infrastructure
        infrastructure = create_infrastructure_asset(data["infrastructure"])
        
        # Use pre-configured climate scenario if provided
        if "scenario_name" in data:
            scenario_name = data["scenario_name"]
            if scenario_name in CLIMATE_SCENARIOS:
                climate_config = CLIMATE_SCENARIOS[scenario_name]
            else:
                climate_config = data["climate_event"]
        else:
            climate_config = data["climate_event"]
        
        climate_event = create_climate_event(climate_config)
        
        # Run analysis
        analyzer = StressAnalyzer(infrastructure, climate_event)
        results = analyzer.analyze()
        
        # Generate recommendations
        rec_engine = RecommendationEngine(results)
        recommendations = rec_engine.generate_summary_report()
        
        response = {
            "success": True,
            "stress_score": results["analysis"]["stress_score"],
            "risk_level": results["analysis"]["risk_level"],
            "failure_probability": results["analysis"]["failure_probability_percent"],
            "insights": results["insights"],
            "recommendations": recommendations["recommendations"],
            "executive_summary": recommendations["executive_summary"],
            "full_analysis": results
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Digital Twin Climate Simulator API",
        "version": "1.0.0"
    })


if __name__ == '__main__':
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    
    print("=" * 60)
    print("🌍 CLIMATWIN - Digital Twin Climate Simulator")
    print("=" * 60)
    print("Server starting on:")
    print("  - http://localhost:5000")
    print("  - http://127.0.0.1:5000")
    print("  - http://0.0.0.0:5000")
    print("")
    print("API Documentation:")
    print("  - POST /api/create-twin - Create infrastructure digital twin")
    print("  - POST /api/simulate-event - Run climate stress simulation")
    print("  - POST /api/compare-scenarios - What-if scenario analysis")
    print("  - POST /api/quick-analysis - Simplified analysis endpoint")
    print("  - GET  /api/health - Health check")
    print("=" * 60)
    print("")
    print("✅ Server is ready! Open your browser to http://127.0.0.1:5000")
    print("")
    
    # Run without debug mode for production stability
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)

