using System.Collections.Generic;
using UnityEngine;

namespace EarthExplorer
{
    [System.Serializable]
    public struct GeoLocationPreset
    {
        public string name;
        public double latitude;
        public double longitude;
        public double height;
    }

    /// <summary>
    /// Preset manager and bridge to teleport across famous global real-world locations.
    /// Works with CesiumGeoreference and Google Photorealistic 3D Tiles.
    /// </summary>
    public class CesiumGoogleEarthBridge : MonoBehaviour
    {
        [Header("Global Location Presets")]
        public List<GeoLocationPreset> presets = new List<GeoLocationPreset>()
        {
            new GeoLocationPreset { name = "San Francisco (Golden Gate)", latitude = 37.8199, longitude = -122.4783, height = 150.0 },
            new GeoLocationPreset { name = "New York (Manhattan)", latitude = 40.7484, longitude = -73.9857, height = 200.0 },
            new GeoLocationPreset { name = "Tokyo (Shibuya)", latitude = 35.6595, longitude = 139.7005, height = 120.0 },
            new GeoLocationPreset { name = "Paris (Eiffel Tower)", latitude = 48.8584, longitude = 2.2945, height = 180.0 },
            new GeoLocationPreset { name = "Dubai (Burj Khalifa)", latitude = 25.1972, longitude = 55.2744, height = 300.0 },
            new GeoLocationPreset { name = "Mount Everest Peak", latitude = 27.9881, longitude = 86.9250, height = 9000.0 }
        };

        [Header("Runtime Teleport Keys")]
        public KeyCode nextPresetKey = KeyCode.Alpha1;

        private int currentPresetIndex = 0;

        void Update()
        {
            if (Input.GetKeyDown(nextPresetKey))
            {
                CycleNextLocation();
            }
        }

        public void CycleNextLocation()
        {
            if (presets.Count == 0) return;
            currentPresetIndex = (currentPresetIndex + 1) % presets.Count;
            TeleportTo(presets[currentPresetIndex]);
        }

        public void TeleportTo(GeoLocationPreset loc)
        {
            Debug.Log($"[EarthExplorer] Teleporting to: {loc.name} ({loc.latitude}, {loc.longitude})");
            
            // If CesiumGeoreference component is attached, update its origin
            Component georef = GetComponent("CesiumGeoreference");
            if (georef != null)
            {
                var type = georef.GetType();
                var latProp = type.GetProperty("latitude");
                var lonProp = type.GetProperty("longitude");
                var heightProp = type.GetProperty("height");

                if (latProp != null) latProp.SetValue(georef, loc.latitude);
                if (lonProp != null) lonProp.SetValue(georef, loc.longitude);
                if (heightProp != null) heightProp.SetValue(georef, loc.height);
            }

            var hud = FindFirstObjectByType<GeoCoordinatesHUD>();
            if (hud != null)
            {
                hud.originLatitude = loc.latitude;
                hud.originLongitude = loc.longitude;
                hud.originAltitude = loc.height;
            }
        }
    }
}
