using UnityEngine;

public class Billboard : MonoBehaviour
{
    private Camera mainCam;

    void Start()
    {
        mainCam = Camera.main;
    }

    void LateUpdate()
    {
        if (mainCam == null) return;

        // Способ 1 — всегда лицом к камере
        transform.LookAt(transform.position + mainCam.transform.rotation * Vector3.forward,
                         mainCam.transform.rotation * Vector3.up);

        // если картинка "зеркалится" (текст наоборот), можно заменить на:
        // transform.forward = mainCam.transform.forward;
    }
}
