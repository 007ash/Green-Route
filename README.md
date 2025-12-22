# Green-Route
GreenRoute – Carbon Optimized Travel Planner

# Problem Statement
Traditional route planner optimize for shortest distance or time, not carbon emissions. The project aims to predict C02 emissions for different routes and recommend the most eco-friendly route. 
# Overview
This project is a web application designed to help users find the most carbon-efficient travel routes. It uses machine learning to predict CO₂ emissions based on various factors such as distance, vehicle type, speed, traffic conditions, weather, and temperature.

## Features
- Predicts CO₂ emissions for different travel routes.
- Provides a user-friendly interface for inputting travel parameters.
- Displays detailed route information and model input data.
- Recommends the most eco-friendly route based on predicted emissions in the map.

## Technologies Used
- Python
- Streamlit for the web interface
- Scikit-learn for machine learning
- Pandas for data manipulation
- Joblib for model serialization
- API integration for featching predictive data
- Geopy for geocoding
- HTML/CSS for custom styling

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/GreenRoute.git
   cd GreenRoute
   ```

```bash
pip install -r requirements.txt
```

```bash 
GreenRoute/FrontEnd> streamlit run app2.py
```

## Usage
1. Open your web browser and go to `http://localhost:8501`.
2. Input the required parameters such as origin, destination, vehicle type, speed, traffic conditions, weather, and temperature.
3. Click on "Predict Emission" to see the predicted CO₂ emissions for the specified route.
4. The application will display the predicted emissions along with the route details.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details

## Acknowledgements
This project was inspired by the need for sustainable travel solutions and aims to raise awareness about carbon emissions in transportation. Special thanks to the contributors and the open-source community for their invaluable resources and support.