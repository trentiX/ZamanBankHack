using UnityEngine;

public class CameraFollow : MonoBehaviour
{
    [SerializeField] private Transform target; // Игрок
    [SerializeField] private Vector3 offset = new Vector3(0, 5, -7); // Смещение от игрока

    void LateUpdate()
    {
        if (target == null) return;

        transform.position = target.position + offset;
        transform.LookAt(target); // Камера всегда смотрит на игрока
    }
}
