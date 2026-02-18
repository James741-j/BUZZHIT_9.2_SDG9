# CLIMATWIN - Digital Twin Simulator for Infrastructure Climate Stress-Testing

<div align="center">
🌍 **Making Climate Resilience Accessible to All** 🌍

[![UN SDG 9](https://img.shields.io/badge/SDG%209-Industry%2C%20Innovation%20%26%20Infrastructure-orange)](https://sdgs.un.org/goals/goal9)
[![UN SDG 11](https://img.shields.io/badge/SDG%2011-Sustainable%20Cities%20%26%20Communities-yellow)](https://sdgs.un.org/goals/goal11)
[![UN SDG 13](https://img.shields.io/badge/SDG%2013-Climate%20Action-green)](https://sdgs.un.org/goals/goal13)

</div>

## Overview

CLIMATWIN is a powerful yet accessible web-based platform that creates digital twins of infrastructure assets (bridges, buildings, roads) and simulates extreme climate events to assess structural resilience, compute risk scores, and provide actionable recommendations.

**Target Users**: Engineering firms, urban planners, and smart-city authorities

**Key Innovation**: Enterprise-level digital twin capabilities at $299-2,999/month (vs $50,000+/year for traditional platforms), with 10-minute analysis instead of weeks.

##Features

### 🏗️ Infrastructure Digital Twins
- **Simplified Inputs**: No CAD models required - just type, material, age, and location
- **Three Asset Types**: Bridges, Buildings, Roads
- **Material Database**: Steel, concrete, reinforced concrete, wood, masonry, composite
- **Age Degradation Modeling**: Automatic structural integrity calculation based on asset age

### 🌪️ Climate Event Simulation
- **Flood Events**: Rainfall intensity, water level, duration, erosion factors
- **Heatwave Events**: Temperature extremes, thermal expansion stress, duration
- **High-Wind Events**: Sustained wind, gusts, storm surge (coastal)
- **Pre-configured Scenarios**: 100-year flood, extreme heatwave, hurricane winds, etc.

### 📊 Stress Analysis & Risk Classification
- **Structural Stress Score**: 0-100 scale combining baseline integrity, climate severity, and vulnerability
- **Risk Levels**: Low (0-30), Medium (30-60), High (60-85), Critical (85-100)
- **Failure Probability**: Logistic regression-based estimation with material and age factors
- **Explainable Insights**: Transparent breakdown of stress components

### 🎯 Actionable Recommendations
- **Context-Aware**: Specific to infrastructure type and climate event combination
- **Prioritized**: CRITICAL / HIGH / MEDIUM with timeline and cost estimates
- **Examples**: "Install scour protection", "Upgrade cooling systems", "Reinforce foundations"

### 🔍 What-If Scenario Analysis
- **Scenario Builder**: Compare baseline vs reinforced configurations
- **Reinforcement Strategies**: Foundation strengthening, wind bracing, flood barriers, cooling upgrades
- **Cost-Benefit Analysis**: Stress reduction vs implementation cost
- **Visual Comparison**: Side-by-side charts and tables

### 💻 Interactive Dashboard
-**Modern UI**: Glassmorphism effects, vibrant gradients, smooth animations
- **Real-Time Sliders**: Adjust climate parameters and see instant updates
- **Chart Visualizations**: Stress gauge, scenario comparison bars, risk indicators
- **Responsive Design**: Desktop and tablet optimized

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone or navigate to the project directory**:
```bash
cd "C:\Users\joola\CIH 3.0"
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the Flask server**:
```bash
python app.py
```

4. **Open your browser**:
Navigate to `http://localhost:5000`

### Demo Usage

1. **Configure Infrastructure Asset**:
   - Select type: Bridge
   - Material: Steel
   - Age: 40 years
   - Location: Coastal City
   - Span: 150m, Height: 12m

2. **Configure Climate Event**:
   - Event: Flood
   - Rainfall: 100 mm/hr
   - Water Level: 4m
   - Duration: 18 hours

3. **Run Simulation**:
   - Click "Run Simulation"
   - View stress score, risk level, failure probability
   - Review insights and recommendations

4. **Scenario Comparison** (Optional):
   - Add baseline scenario
   - Create variations with reinforcement strategies
   - Compare results side-by-side

## API Endpoints

### `POST /api/quick-analysis`
Run complete stress analysis with simplified inputs.

**Request Body**:
```json
{
  "infrastructure": {
    "id": "BRG-001",
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
    "rainfall_intensity": 100,
    "water_level": 4,
    "duration": 18,
    "severity": "high"
  }
}
```

**Response**:
```json
{
  "success": true,
  "stress_score": 67.5,
  "risk_level": "high",
  "failure_probability": 42.3,
  "insights": ["⚠️ Asset age (40 years) significantly increases vulnerability", ...],
  "recommendations": [
    {
      "priority": "HIGH",
      "action": "Install scour protection",
      "description": "Add riprap or concrete aprons to prevent foundation undermining",
      "timeline": "3-6 months",
      "estimated_cost": "$$$"
    }
  ],
  "executive_summary": "Analysis reveals HIGH risk level with stress score of 67.5/100..."
}
```

### `POST /api/compare-scenarios`
Compare multiple scenarios with different configurations.

### `GET /api/health`
Health check endpoint.

## UN SDG Alignment

### SDG 9: Industry, Innovation & Infrastructure
- **Impact**: 25% reduction in unplanned infrastructure failures through proactive resilience planning
- **Metric**: 10,000+ infrastructure assets assessed by Year 3
- **Innovation**: Democratizing enterprise digital twin technology for mid-market organizations

### SDG 11: Sustainable Cities & Communities
- **Impact**: Empower 100+ cities with evidence-based climate adaptation strategies
- **Metric**: $500M+ in municipal climate resilience investments informed by platform analytics
- **Equity**: Prioritize infrastructure serving disadvantaged communities

### SDG 13: Climate Action
- **Impact**: Prevent $1B+ in climate damage costs through preventive measures
- **Metric**: 15-30% reduction in climate-related infrastructure economic losses
- **Integration**: Platform outputs support climate policy development and regulatory compliance

## Technology Stack

**Backend**:
- Python 3.8+
- Flask (Web framework)
- Custom stress analysis engine
- Climate simulation models

**Frontend**:
- HTML5, CSS3 (Glassmorphism, gradients)
- Vanilla JavaScript
- Chart.js (Visualizations)

**Data & ML**:
- Rule-based physics models
- Logistic regression for failure probability
- Synthetic training datasets

## Market Opportunity

- **Market Size**: $12.8B climate adaptation market by 2027 (CAGR 23.4%)
- **Pricing**: $299-2,999/month (vs $50,000+/year for enterprise platforms)
- **Target**: 50,000+ engineering firms, 10,000+ municipalities, 500+ smart city vendors globally

## Project Structure

```
CIH 3.0/
├── app.py                      # Flask backend API
├── infrastructure_models.py    # Digital twin asset classes
├── climate_simulator.py        # Climate event simulation engine
├── stress_analyzer.py          # Stress analysis & risk classification
├── scenario_manager.py         # What-if scenario comparison
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── docs/
│   ├── market_evaluation.md    # Market analysis & business model
│   └── SDG_alignment.md        # UN SDG impact framework
└── static/
    ├── dashboard.html          # Main web interface
    ├── css/
    │   └── styles.css          # Premium styling
    └── js/
        └── dashboard.js        # Interactive functionality
```

## Development Roadmap

### Phase 1: MVP (Current)
✅ Core infrastructure models (bridges, buildings, roads)  
✅ Climate event simulation (flood, heatwave, wind)  
✅ Stress analysis with risk classification  
✅ Interactive web dashboard  
✅ Scenario comparison

### Phase 2: Enhancements (Next 3 months)
- Real-time IoT sensor integration
- GIS/BIM software connectors
- Mobile app (iOS/Android)
- Multi-language support

### Phase 3: Scale (6-12 months)
- Portfolio management for city-scale deployments
- White-label platform for partners
- API marketplace for third-party integrations
- Machine learning model refinement with real-world data

## Contributing

We welcome contributions! Areas of interest:
- Additional infrastructure types (tunnels, dams, utilities)
- More climate scenarios (earthquakes, sea level rise, wildfires)
- ML model improvements
- Localization and internationalization
- Case study validation

## License

This project is proprietary software developed for climate resilience planning.

## Contact & Support

- **Website**: [Coming Soon]
- **Email**: info@climatwin.com
- **Demo**: http://localhost:5000 (when running locally)

## Acknowledgments

- UN Sustainable Development Goals framework
- IPCC Climate Assessment Reports
- Civil engineering and climate science communities
- Open-source JavaScript and Python ecosystems

---

<div align="center">

**CLIMATWIN** | Making Infrastructure Climate-Resilient, One Digital Twin at a Time 🌍

*Contributing to UN SDG 9, 11, and 13*

</div>
