"""
Cloud-Based AQI Predictor - Utility Functions
"""


def get_aqi_category(aqi: float) -> tuple[str, str]:
    """
    Determine the EPA AQI category and associated health advisory based on EPA standards.

    Breakpoints:
      * 0-50    : "Good" (Air quality is satisfactory)
      * 51-100  : "Moderate" (Acceptable air quality)
      * 101-150 : "Unhealthy for Sensitive Groups" (Sensitive individuals should reduce exertion)
      * 151-200 : "Unhealthy" (Everyone may begin to experience health effects)
      * 201-300 : "Very Unhealthy" (Health alert: serious risk)
      * 301+    : "Hazardous" (Emergency conditions: entire population affected)

    Parameters:
        aqi (float): The calculated or predicted Air Quality Index value.

    Returns:
        tuple[str, str]: (Category, Health Advisory)
    """
    if aqi <= 50:
        return "Good", "Air quality is satisfactory"
    elif aqi <= 100:
        return "Moderate", "Acceptable air quality"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "Sensitive individuals should reduce exertion"
    elif aqi <= 200:
        return "Unhealthy", "Everyone may begin to experience health effects"
    elif aqi <= 300:
        return "Very Unhealthy", "Health alert: serious risk"
    else:
        return "Hazardous", "Emergency conditions: entire population affected"
