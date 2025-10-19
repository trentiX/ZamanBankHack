using UnityEngine;

public class NPCInteractor : MonoBehaviour
{
    [SerializeField] private CameraFollow cameraFollow;
    [SerializeField] private Transform npcTransform;
    [SerializeField] private Transform playerTransform;
    [SerializeField] private DialogueUI dialogueUI;
    [SerializeField] private PlayerMovementController playerMovement;
    [SerializeField] private float dialogueCooldown = 0.5f; // Cooldown in seconds

    private bool isTalking = false;
    private bool canTalk = true;
    private float cooldownTimer = 0f;

    private void Start()
    {
        if (!cameraFollow || !npcTransform || !playerTransform || !dialogueUI || !playerMovement)
        {
            Debug.LogError("One or more serialized fields not assigned in NPCInteractor", this);
        }
    }

    private void Update()
    {
        // Update cooldown timer
        if (!canTalk)
        {
            cooldownTimer -= Time.deltaTime;
            if (cooldownTimer <= 0f)
            {
                canTalk = true;
            }
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player") && canTalk && !isTalking)
        {
            Debug.Log("Player entered NPC trigger, starting dialogue");
            StartDialogue();
        }
    }

    private void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("Player") && isTalking)
        {
            if (canTalk)
            {
                Debug.Log("Player exited NPC trigger, closing dialogue");
                dialogueUI.Close();
                StartCooldown();
            }
            else
            {
                Debug.Log("Dialogue close blocked by cooldown");
            }
        }
    }

    private void StartDialogue()
    {
        isTalking = true;
        canTalk = false;
        cooldownTimer = dialogueCooldown;

        playerMovement.EnterDialogue();
        playerTransform.LookAt(npcTransform);
        npcTransform.LookAt(playerTransform);

        cameraFollow.FocusOnDialogue(playerTransform, npcTransform);
        dialogueUI.Show(OnDialogueClosed);
    }

    private void OnDialogueClosed()
    {
        isTalking = false;
        playerMovement.ExitDialogue();
        cameraFollow.FocusOnPlayer();
        StartCooldown();
        Debug.Log("Dialogue closed, unblocking player movement");
    }

    private void StartCooldown()
    {
        canTalk = false;
        cooldownTimer = dialogueCooldown;
    }
}