from .models import Edge

# Illustrative sample data. Values are simulated and are not live travel estimates.
SAMPLE_EDGES = [
    Edge("Delhi", "Agra", 233, 3.5, 1400),
    Edge("Delhi", "Jaipur", 281, 5.0, 1600),
    Edge("Delhi", "Chandigarh", 245, 4.5, 1500),
    Edge("Delhi", "Lucknow", 555, 8.0, 1700),
    Edge("Agra", "Jaipur", 240, 4.0, 1800),
    Edge("Agra", "Bhopal", 550, 8.0, 1900),
    Edge("Jaipur", "Udaipur", 393, 6.0, 2200),
    Edge("Jaipur", "Ahmedabad", 670, 10.0, 2600),
    Edge("Chandigarh", "Shimla", 114, 3.5, 900),
    Edge("Chandigarh", "Amritsar", 230, 4.0, 1300),
    Edge("Lucknow", "Varanasi", 320, 5.0, 1700),
    Edge("Varanasi", "Patna", 250, 4.0, 1400),
    Edge("Patna", "Kolkata", 580, 9.0, 3000),
    Edge("Bhopal", "Indore", 195, 3.5, 1200),
    Edge("Bhopal", "Mumbai", 775, 12.0, 2800),
    Edge("Indore", "Ahmedabad", 400, 7.0, 2100),
    Edge("Ahmedabad", "Mumbai", 525, 8.0, 2700),
    Edge("Mumbai", "Pune", 150, 3.0, 950),
    Edge("Udaipur", "Ahmedabad", 260, 4.5, 1500),
    Edge("Agra", "Delhi", 233, 3.5, 1400),
]
