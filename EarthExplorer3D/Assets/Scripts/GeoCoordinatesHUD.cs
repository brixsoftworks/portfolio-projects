using UnityEngine;

namespace EarthExplorer
{
    /// <summary>
    /// Displays real-time flight telemetry and GPS coordinates on-screen.
    /// </summary>
    public class GeoCoordinatesHUD : MonoBehaviour
    {
        [Header("References")]
        public PlayerFlightController flightController;
        
        [Header("Origin Geographic Coordinate")]
        [Tooltip("Center Latitude (e.g. 37.7749 for San Francisco, 40.7128 for NYC, 35.6762 for Tokyo)")]
        public double originLatitude = 37.7749;
        
        [Tooltip("Center Longitude (e.g. -122.4194 for SF, -74.0060 for NYC, 139.6503 for Tokyo)")]
        public double originLongitude = -122.4194;

        [Tooltip("Origin height above sea level in meters")]
        public double originAltitude = 50.0;

        private GUIStyle headerStyle;
        private GUIStyle bodyStyle;
        private GUIStyle boxStyle;

        void Start()
        {
            if (flightController == null)
            {
                flightController = FindFirstObjectByType<PlayerFlightController>();
            }
        }

        void OnGUI()
        {
            InitStyles();

            // Telemetry Box
            float panelWidth = 320f;
            float panelHeight = 220f;
            Rect panelRect = new Rect(20, 20, panelWidth, panelHeight);
            GUI.Box(panelRect, GUIContent.none, boxStyle);

            GUILayout.BeginArea(new Rect(30, 30, panelWidth - 20, panelHeight - 20));
            
            GUILayout.Label("🌍 Real-World Earth Flight HUD", headerStyle);
            GUILayout.Space(5);

            if (flightController != null)
            {
                Vector3 playerPos = flightController.transform.position;
                
                // Approximate degree conversion for display
                double currentLat = originLatitude + (playerPos.z / 111139.0);
                double currentLon = originLongitude + (playerPos.x / (111139.0 * Mathf.Cos((float)(originLatitude * Mathf.Deg2Rad))));
                double currentAlt = originAltitude + playerPos.y;

                GUILayout.Label(string.Format("Latitude:  {0:F6}°", currentLat), bodyStyle);
                GUILayout.Label(string.Format("Longitude: {0:F6}°", currentLon), bodyStyle);
                GUILayout.Label(string.Format("Altitude:  {0:F1} m ({1:F0} ft)", currentAlt, currentAlt * 3.28084), bodyStyle);
                GUILayout.Label(string.Format("Speed:     {0:F1} km/h", flightController.GetCurrentSpeedKmh()), bodyStyle);
            }

            GUILayout.Space(10);
            GUILayout.Label("Controls: W/S/A/D: Move | Space/Ctrl: Up/Down", bodyStyle);
            GUILayout.Label("Mouse: Look | Shift: Boost | Q/E: Roll", bodyStyle);

            GUILayout.EndArea();
        }

        private void InitStyles()
        {
            if (headerStyle == null)
            {
                headerStyle = new GUIStyle(GUI.skin.label)
                {
                    fontSize = 15,
                    fontStyle = FontStyle.Bold
                };
                headerStyle.normal.textColor = Color.cyan;
            }

            if (bodyStyle == null)
            {
                bodyStyle = new GUIStyle(GUI.skin.label)
                {
                    fontSize = 12,
                    fontStyle = FontStyle.Normal
                };
                bodyStyle.normal.textColor = Color.white;
            }

            if (boxStyle == null)
            {
                boxStyle = new GUIStyle(GUI.skin.box);
            }
        }
    }
}
