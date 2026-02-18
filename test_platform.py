"""
Comprehensive test script for CLIMATWIN Digital Twin Platform
Tests all API endpoints and features
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:5000/api"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_health_check():
    """Test 1: Health Check"""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{API_BASE}/health")
        data = response.json()
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Service: {data['service']}")
        print(f"✅ Version: {data['version']}")
        print(f"✅ Status: {data['status']}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_quick_analysis_bridge_flood():
    """Test 2: Bridge + Flood Simulation"""
    print_section("TEST 2: Quick Analysis - 40-Year Steel Bridge in Extreme Flood")
    
    payload = {
        "infrastructure": {
            "id": "TEST-BRG-001",
            "type": "bridge",
            "material": "steel",
            "age": 40,
            "location": "Coastal City",
            "span_length": 150,
            "height_above_water": 12,
            "load_capacity": 80,
            "foundation_type": "pile"
        },
        "climate_event": {
            "type": "flood",
            "rainfall_intensity": 120,
            "water_level": 5,
            "duration": 24,
            "severity": "extreme",
            "name": "Extreme Coastal Flood"
        }
    }
    
    try:
        response = requests.post(f"{API_BASE}/quick-analysis", json=payload)
        data = response.json()
        
        if data.get("success"):
            print(f"✅ Analysis completed successfully!")
            print(f"\n📊 RESULTS:")
            print(f"   • Stress Score: {data['stress_score']:.1f} / 100")
            print(f"   • Risk Level: {data['risk_level'].upper()}")
            print(f"   • Failure Probability: {data['failure_probability']:.1f}%")
            
            print(f"\n💡 INSIGHTS ({len(data['insights'])} findings):")
            for i, insight in enumerate(data['insights'][:5], 1):
                print(f"   {i}. {insight}")
            
            print(f"\n🎯 RECOMMENDATIONS ({len(data['recommendations'])} actions):")
            for i, rec in enumerate(data['recommendations'][:3], 1):
                print(f"   {i}. [{rec['priority']}] {rec['action']}")
                print(f"      Timeline: {rec['timeline']} | Cost: {rec['estimated_cost']}")
            
            print(f"\n📋 EXECUTIVE SUMMARY:")
            print(f"   {data['executive_summary'][:200]}...")
            
            return data
        else:
            print(f"❌ Analysis failed: {data.get('error')}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_quick_analysis_building_heatwave():
    """Test 3: Building + Heatwave Simulation"""
    print_section("TEST 3: Quick Analysis - 60-Year Concrete Building in Extreme Heatwave")
    
    payload = {
        "infrastructure": {
            "id": "TEST-BLD-001",
            "type": "building",
            "material": "concrete",
            "age": 60,
            "location": "Desert City",
            "floors": 15,
            "height": 45,
            "floor_area": 3000,
            "foundation_depth": 5,
            "has_basement": True,
            "cooling_system": "natural"
        },
        "climate_event": {
            "type": "heatwave",
            "max_temperature": 48,
            "min_temperature": 35,
            "duration": 12,
            "humidity": 30,
            "severity": "extreme",
            "name": "Extreme Desert Heatwave"
        }
    }
    
    try:
        response = requests.post(f"{API_BASE}/quick-analysis", json=payload)
        data = response.json()
        
        if data.get("success"):
            print(f"✅ Analysis completed successfully!")
            print(f"\n📊 RESULTS:")
            print(f"   • Stress Score: {data['stress_score']:.1f} / 100")
            print(f"   • Risk Level: {data['risk_level'].upper()}")
            print(f"   • Failure Probability: {data['failure_probability']:.1f}%")
            
            print(f"\n💡 KEY INSIGHTS:")
            for insight in data['insights'][:3]:
                print(f"   • {insight}")
            
            print(f"\n🎯 TOP RECOMMENDATIONS:")
            for rec in data['recommendations'][:2]:
                print(f"   [{rec['priority']}] {rec['action']}")
            
            return data
        else:
            print(f"❌ Analysis failed: {data.get('error')}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_quick_analysis_road_wind():
    """Test 4: Road + High Wind Simulation"""
    print_section("TEST 4: Quick Analysis - 20-Year Asphalt Road in Hurricane")
    
    payload = {
        "infrastructure": {
            "id": "TEST-ROAD-001",
            "type": "road",
            "material": "composite",
            "age": 20,
            "location": "Coastal Highway",
            "length": 10,
            "width": 15,
            "traffic_volume": 50000,
            "drainage_quality": "good",
            "elevation": 2
        },
        "climate_event": {
            "type": "high_wind",
            "sustained_wind_speed": 150,
            "gust_speed": 190,
            "duration": 8,
            "storm_surge": 2.5,
            "severity": "extreme",
            "name": "Category 5 Hurricane"
        }
    }
    
    try:
        response = requests.post(f"{API_BASE}/quick-analysis", json=payload)
        data = response.json()
        
        if data.get("success"):
            print(f"✅ Analysis completed successfully!")
            print(f"\n📊 RESULTS:")
            print(f"   • Stress Score: {data['stress_score']:.1f} / 100")
            print(f"   • Risk Level: {data['risk_level'].upper()}")
            print(f"   • Failure Probability: {data['failure_probability']:.1f}%")
            
            return data
        else:
            print(f"❌ Analysis failed: {data.get('error')}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_scenario_comparison():
    """Test 5: Scenario Comparison"""
    print_section("TEST 5: Scenario Comparison - Baseline vs Reinforced Bridge")
    
    scenarios = {
        "scenarios": [
            {
                "scenario_id": "baseline",
                "name": "Baseline - No Reinforcement",
                "infrastructure": {
                    "id": "COMP-BRG-001",
                    "type": "bridge",
                    "material": "steel",
                    "age": 50,
                    "location": "Urban River",
                    "span_length": 200,
                    "height_above_water": 15,
                    "load_capacity": 100,
                    "foundation_type": "pile"
                },
                "climate_event": {
                    "type": "flood",
                    "rainfall_intensity": 100,
                    "water_level": 6,
                    "duration": 18,
                    "severity": "high"
                },
                "reinforcements": []
            },
            {
                "scenario_id": "reinforced",
                "name": "Reinforced - Foundation + Deck Upgrade",
                "infrastructure": {
                    "id": "COMP-BRG-002",
                    "type": "bridge",
                    "material": "steel",
                    "age": 50,
                    "location": "Urban River",
                    "span_length": 200,
                    "height_above_water": 15,
                    "load_capacity": 100,
                    "foundation_type": "pile"
                },
                "climate_event": {
                    "type": "flood",
                    "rainfall_intensity": 100,
                    "water_level": 6,
                    "duration": 18,
                    "severity": "high"
                },
                "reinforcements": ["bridge_foundation_strengthening", "bridge_deck_rehabilitation"]
            }
        ]
    }
    
    try:
        response = requests.post(f"{API_BASE}/compare-scenarios", json=scenarios)
        data = response.json()
        
        if data.get("success"):
            print(f"✅ Scenario comparison completed!")
            
            comparison = data['comparison']
            print(f"\n📊 COMPARISON RESULTS:")
            print(f"\n{'Scenario':<40} {'Stress':<12} {'Risk':<12} {'Failure %':<12}")
            print("-" * 76)
            
            for scenario in comparison['scenarios']:
                print(f"{scenario['scenario_name']:<40} "
                      f"{scenario['stress_score']:>8.1f}    "
                      f"{scenario['risk_level']:>8}    "
                      f"{scenario['failure_probability']:>8.1f}%")
            
            print(f"\n🏆 BEST SCENARIO: {comparison['best_scenario']['scenario_name']}")
            print(f"   Stress Score: {comparison['best_scenario']['stress_score']:.1f}")
            print(f"   Risk Level: {comparison['best_scenario']['risk_level'].upper()}")
            
            print(f"\n💰 COST-BENEFIT ANALYSIS:")
            for cb in comparison['cost_benefit_analysis']:
                print(f"   {cb['scenario_name']}: {cb['analysis']}")
            
            print(f"\n📝 SUMMARY:")
            print(f"   {data['summary']}")
            
            return data
        else:
            print(f"❌ Comparison failed: {data.get('error')}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_materials_endpoint():
    """Test 6: Materials Endpoint"""
    print_section("TEST 6: Available Materials")
    
    try:
        response = requests.get(f"{API_BASE}/materials")
        data = response.json()
        
        print(f"✅ Retrieved {len(data['materials'])} materials:")
        for mat in data['materials']:
            print(f"   • {mat['name']}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    """Run all platform tests"""
    print("\n" + "🌍" * 35)
    print("  CLIMATWIN DIGITAL TWIN PLATFORM - COMPREHENSIVE TEST SUITE")
    print("🌍" * 35)
    print(f"\nTest started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test 1: Health Check
    results['health'] = test_health_check()
    
    # Test 2: Bridge + Flood
    results['bridge_flood'] = test_quick_analysis_bridge_flood()
    
    # Test 3: Building + Heatwave
    results['building_heat'] = test_quick_analysis_building_heatwave()
    
    # Test 4: Road + Wind
    results['road_wind'] = test_quick_analysis_road_wind()
    
    # Test 5: Scenario Comparison
    results['scenario'] = test_scenario_comparison()
    
    # Test 6: Materials
    results['materials'] = test_materials_endpoint()
    
    # Summary
    print_section("TEST SUMMARY")
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    
    print(f"\n✅ Tests Passed: {passed_tests}/{total_tests}")
    print(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! CLIMATWIN platform is fully functional!")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) failed. Please review errors above.")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*70)

if __name__ == "__main__":
    run_all_tests()
