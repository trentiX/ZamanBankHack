using UnityEngine;

public class CameraFollow : MonoBehaviour
{
    [SerializeField] private Transform target; // Игрок
    [SerializeField] private Vector3 normalOffset = new Vector3(0, 5, -7);
    [SerializeField] private float normalSmooth = 5f;
    [SerializeField] private Vector3 dialogueOffset = new Vector3(0, 3, -4);
    [SerializeField] private float dialogueSmooth = 2f;

    private bool inDialogue = false;
    private Transform npc;
    private Transform player;

    private void Start()
    {
        if (!target)
        {
            Debug.LogError("Target not assigned in CameraFollow", this);
        }
    }

    private void LateUpdate()
    {
        if (inDialogue)
        {
            if (npc == null || player == null) return;

            Vector3 middle = (npc.position + player.position) / 2f;
            Vector3 targetPos = middle + dialogueOffset;
            transform.position = Vector3.Lerp(transform.position, targetPos, Time.deltaTime * dialogueSmooth);
            transform.rotation = Quaternion.Lerp(transform.rotation, Quaternion.LookRotation(middle - transform.position), Time.deltaTime * 5f);
        }
        else if (target != null)
        {
            Vector3 targetPos = target.position + normalOffset;
            transform.position = Vector3.Lerp(transform.position, targetPos, Time.deltaTime * normalSmooth);
            transform.LookAt(target);
        }
    }

    public void FocusOnDialogue(Transform playerTransform, Transform npcTransform)
    {
        inDialogue = true;
        player = playerTransform;
        npc = npcTransform;
    }

    public void FocusOnPlayer()
    {
        inDialogue = false;
        player = null;
        npc = null;
    }
}