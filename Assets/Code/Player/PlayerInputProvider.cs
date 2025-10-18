using UnityEngine;

public class PlayerInputProvider : MonoBehaviour, IMovementInputProvider
{
    [SerializeField] private Transform cameraTransform;

    public Vector3 GetMoveDirection()
    {
        float horizontal = Input.GetAxisRaw("Horizontal");
        float vertical = Input.GetAxisRaw("Vertical");

        // Берём направление по камере
        Vector3 forward = cameraTransform.forward;
        Vector3 right = cameraTransform.right;

        // Обнуляем Y, чтобы движение было только по плоскости XZ
        forward.y = 0f;
        right.y = 0f;
        forward.Normalize();
        right.Normalize();

        Vector3 moveDirection = (forward * vertical + right * horizontal).normalized;
        return moveDirection;
    }
}
