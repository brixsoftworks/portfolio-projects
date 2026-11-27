using UnityEngine;

namespace EarthExplorer
{
    /// <summary>
    /// Smooth 6-DOF Flight and Drone Controller for exploring Real-World 3D Tiles.
    /// Handles pitch, roll, yaw, throttle, boost, and ground collision prevention.
    /// </summary>
    [RequireComponent(typeof(Rigidbody))]
    public class PlayerFlightController : MonoBehaviour
    {
        [Header("Flight Dynamics")]
        [Tooltip("Forward cruise speed in meters/second")]
        public float forwardSpeed = 50.0f;
        
        [Tooltip("Multiplier when holding Shift (Boost)")]
        public float boostMultiplier = 3.0f;

        [Tooltip("Strafe / Vertical ascension speed")]
        public float strafeSpeed = 25.0f;

        [Header("Rotational Sensitivity")]
        public float pitchRate = 45.0f;
        public float yawRate = 45.0f;
        public float rollRate = 60.0f;
        public float responsiveness = 5.0f;

        [Header("Camera & View")]
        public Camera playerCamera;
        public float mouseSensitivity = 2.0f;

        private Rigidbody rb;
        private float currentSpeed;
        private Vector3 targetVelocity;

        void Awake()
        {
            rb = GetComponent<Rigidbody>();
            rb.useGravity = false;
            rb.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
            rb.interpolation = RigidbodyInterpolation.Interpolate;

            if (playerCamera == null)
            {
                playerCamera = GetComponentInChildren<Camera>();
            }
        }

        void Update()
        {
            HandleInputs();
        }

        void FixedUpdate()
        {
            ApplyMovement();
        }

        private void HandleInputs()
        {
            // Boost state
            float boost = Input.GetKey(KeyCode.LeftShift) ? boostMultiplier : 1.0f;
            currentSpeed = forwardSpeed * boost;

            // Pitch & Yaw via Mouse or Arrow keys
            float pitch = -Input.GetAxis("Mouse Y") * mouseSensitivity;
            float yaw = Input.GetAxis("Mouse X") * mouseSensitivity;

            // Roll via Q / E
            float roll = 0f;
            if (Input.GetKey(KeyCode.Q)) roll += rollRate;
            if (Input.GetKey(KeyCode.E)) roll -= rollRate;

            // Apply rotation torque/transform
            if (Input.GetMouseButton(1) || Input.GetMouseButton(0)) // While holding mouse button or free look
            {
                transform.Rotate(Vector3.up, yaw, Space.World);
                transform.Rotate(Vector3.right, pitch, Space.Self);
            }

            if (Mathf.Abs(roll) > 0.01f)
            {
                transform.Rotate(Vector3.forward, roll * Time.deltaTime, Space.Self);
            }

            // Directional translation
            float moveForward = Input.GetAxis("Vertical");   // W / S
            float moveStrafe = Input.GetAxis("Horizontal");  // A / D
            float moveVertical = 0f;

            if (Input.GetKey(KeyCode.Space)) moveVertical += 1.0f;     // Ascend
            if (Input.GetKey(KeyCode.LeftControl)) moveVertical -= 1.0f; // Descend

            Vector3 moveDirection = (transform.forward * moveForward) +
                                    (transform.right * moveStrafe) +
                                    (transform.up * moveVertical);

            targetVelocity = moveDirection.normalized * currentSpeed;
        }

        private void ApplyMovement()
        {
            // Smooth acceleration
            rb.linearVelocity = Vector3.Lerp(rb.linearVelocity, targetVelocity, Time.fixedDeltaTime * responsiveness);
        }

        public float GetCurrentSpeedKmh()
        {
            return rb.linearVelocity.magnitude * 3.6f;
        }
    }
}
