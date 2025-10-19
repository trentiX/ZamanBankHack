using UnityEngine;
using UnityEngine.AI;
using TMPro;
using UnityEngine.EventSystems;

public class PlayerMovementController : MonoBehaviour
{
    [SerializeField] private float speed = 5.0f;
    [SerializeField] private float rotationSpeed = 10f;
    [SerializeField] private float kMinInput = 0.01f;
    [SerializeField] private float kMinMoveDistance = 0.01f;
    [SerializeField] private float kMaxDistFromNavMesh = 3f;
    [SerializeField] private Animator animator;
    
    [Header("Obstacle Detection")]
    [SerializeField] private LayerMask obstacleLayer = -1;
    [SerializeField] private float obstacleCheckDistance = 0.6f;
    [SerializeField] private float obstacleCheckRadius = 0.3f;

    [Header("Input Field")]
    [SerializeField] private TMP_InputField[] inputFields; // Массив полей ввода

    private IMovementInputProvider inputProvider;
    private StateMachine stateMachine;
    private CharacterAnimator characterAnimator;
    private PlayerInteractor playerInteractor;

    private ICharacterState idleState;
    private ICharacterState idleWithItemState;
    private ICharacterState walkState;
    private ICharacterState walkWithItemState;

    private bool isInDialogue = false;

    private void Awake()
    {
        inputProvider = GetComponent<IMovementInputProvider>();
        stateMachine = GetComponent<StateMachine>();
        playerInteractor = GetComponent<PlayerInteractor>();

        if (animator == null) animator = GetComponent<Animator>();
        if (inputProvider == null || stateMachine == null || playerInteractor == null)
        {
            Debug.LogError("Required components missing in PlayerMovementController", this);
        }

        characterAnimator = new CharacterAnimator(animator);
        idleState = new IdleState(characterAnimator);
        idleWithItemState = new IdleWithItemsState(characterAnimator);
        walkState = new WalkWithoutItemsState(characterAnimator);
        walkWithItemState = new WalkWithItemsState(characterAnimator);

        // Проверка EventSystem
        if (FindObjectOfType<EventSystem>() == null)
        {
            Debug.LogError("EventSystem отсутствует в сцене! Добавьте EventSystem для работы TMP_InputField.");
        }
    }

    private void Update()
    {
        if (inputProvider == null || stateMachine == null) return;

        // Проверка активности поля ввода
        bool isInputFieldActive = IsAnyInputFieldFocused();
        if (isInputFieldActive)
        {
            ICharacterState targetState = playerInteractor.GetHasItemInHandsBool() ? idleWithItemState : idleState;
            stateMachine.ChangeState(targetState);
            Debug.Log($"Input field active, state set to: {(playerInteractor.GetHasItemInHandsBool() ? "IdleWithItems" : "Idle")}");
            return;
        }

        // Если в диалоге
        if (isInDialogue)
        {
            ICharacterState targetState = playerInteractor.GetHasItemInHandsBool() ? idleWithItemState : idleState;
            stateMachine.ChangeState(targetState);
            Debug.Log($"In dialogue, state set to: {(playerInteractor.GetHasItemInHandsBool() ? "IdleWithItems" : "Idle")}");
            return;
        }

        Vector3 inputMoveDirection = inputProvider.GetMoveDirection();
        bool isMoving = inputMoveDirection.magnitude > 0.1f;

        if (isMoving)
        {
            stateMachine.ChangeState(playerInteractor.GetHasItemInHandsBool() ? walkWithItemState : walkState);
            Debug.Log($"Moving, state set to: {(playerInteractor.GetHasItemInHandsBool() ? "WalkWithItems" : "Walk")}");
        }
        else if (playerInteractor.GetIsWorkingBool())
        {
            Debug.Log("Player is working, no state change");
            return;
        }
        else
        {
            stateMachine.ChangeState(playerInteractor.GetHasItemInHandsBool() ? idleWithItemState : idleState);
            Debug.Log($"Not moving, state set to: {(playerInteractor.GetHasItemInHandsBool() ? "IdleWithItems" : "Idle")}");
        }

        TryMove(inputMoveDirection);
    }

    private void TryMove(Vector3 inputMoveDirection)
    {
        // Блокировка движения при активном поле ввода или диалоге
        if (IsAnyInputFieldFocused() || isInDialogue)
        {
            Debug.Log($"Movement blocked: {(IsAnyInputFieldFocused() ? "Input field active" : "In dialogue")}");
            return;
        }

        if (inputMoveDirection.sqrMagnitude > kMinInput)
        {
            if (IsObstacleInFront(inputMoveDirection))
            {
                Debug.Log("Movement blocked: Obstacle detected");
                return;
            }
            
            Vector3 inputMoveDelta = inputMoveDirection * Time.deltaTime * speed;
            Vector3 desiredPosition = transform.position + inputMoveDelta;

            if (NavMesh.SamplePosition(desiredPosition, out NavMeshHit hit, kMaxDistFromNavMesh, NavMesh.AllAreas))
            {
                if (Vector3.Distance(transform.position, hit.position) > kMinMoveDistance)
                {
                    transform.position = hit.position;
                    Quaternion targetRotation = Quaternion.LookRotation(inputMoveDirection);
                    transform.rotation = Quaternion.Slerp(transform.rotation, targetRotation, rotationSpeed * Time.deltaTime);
                    Debug.Log("Player moved to: " + hit.position);
                }
            }
        }
    }

    private bool IsObstacleInFront(Vector3 moveDirection)
    {
        Vector3 rayOrigin = transform.position + Vector3.up * 0.1f;
        bool isObstacle = Physics.SphereCast(
            rayOrigin, 
            obstacleCheckRadius, 
            moveDirection, 
            out RaycastHit hit, 
            obstacleCheckDistance, 
            obstacleLayer
        );
        if (isObstacle)
        {
            Debug.Log("Obstacle detected in front: " + hit.collider.name);
        }
        return isObstacle;
    }

    private bool IsAnyInputFieldFocused()
    {
        // Проверяем все TMP_InputField в сцене
        foreach (var inputField in FindObjectsOfType<TMP_InputField>())
        {
            if (inputField != null && inputField.isFocused)
            {
                Debug.Log($"Input field {inputField.name} is focused");
                return true;
            }
        }

        // Проверяем указанные в инспекторе поля ввода
        if (inputFields != null && inputFields.Length > 0)
        {
            foreach (var inputField in inputFields)
            {
                if (inputField != null && inputField.isFocused)
                {
                    Debug.Log($"Assigned input field {inputField.name} is focused");
                    return true;
                }
            }
        }

        return false;
    }

    public void EnterDialogue()
    {
        isInDialogue = true;
        Debug.Log("Entered dialogue mode");
        stateMachine.ChangeState(playerInteractor.GetHasItemInHandsBool() ? idleWithItemState : idleState);
    }

    public void ExitDialogue()
    {
        isInDialogue = false;
        Debug.Log("Exited dialogue mode");
    }

    private void OnDrawGizmosSelected()
    {
        if (inputProvider != null)
        {
            Vector3 moveDirection = inputProvider.GetMoveDirection();
            if (moveDirection.magnitude > 0.1f)
            {
                Vector3 rayOrigin = transform.position + Vector3.up * 0.1f;
                Gizmos.color = IsObstacleInFront(moveDirection) ? Color.red : Color.green;
                Gizmos.DrawWireSphere(rayOrigin + moveDirection * obstacleCheckDistance, obstacleCheckRadius);
                Gizmos.DrawLine(rayOrigin, rayOrigin + moveDirection * obstacleCheckDistance);
            }
        }
    }
}