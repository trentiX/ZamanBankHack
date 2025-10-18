using UnityEngine;
using UnityEngine.AI;

public class PlayerMovementController : MonoBehaviour
{
    [SerializeField] private float speed = 5.0f;
    [SerializeField] private float rotationSpeed = 10f;
    [SerializeField] private float kMinInput = 0.01f;
    [SerializeField] private float kMinMoveDistance = 0.01f;
    [SerializeField] private float kMaxDistFromNavMesh = 3f;
    [SerializeField] private Animator animator;
    
    [Header("Obstacle Detection")]
    [SerializeField] private LayerMask obstacleLayer = -1; // Слой препятствий
    [SerializeField] private float obstacleCheckDistance = 0.6f; // Дистанция проверки препятствий
    [SerializeField] private float obstacleCheckRadius = 0.3f; // Радиус проверки (для SphereCast)

    private IMovementInputProvider inputProvider;
    private StateMachine stateMachine;
    private CharacterAnimator characterAnimator;
    private PlayerInteractor playerInteractor;

    private ICharacterState idleState;
    private ICharacterState idleWithItemState;
    private ICharacterState walkState;
    private ICharacterState walkWithItemState;

    private void Awake()
    {
        inputProvider = GetComponent<IMovementInputProvider>();
        stateMachine = GetComponent<StateMachine>();
        playerInteractor = GetComponent<PlayerInteractor>();

        if (animator == null) animator = GetComponent<Animator>();
        characterAnimator = new CharacterAnimator(animator);

        idleState = new IdleState(characterAnimator);
        idleWithItemState = new IdleWithItemsState(characterAnimator);
        walkState = new WalkWithoutItemsState(characterAnimator);
        walkWithItemState = new WalkWithItemsState(characterAnimator);
    }

    void Update()
    {
        if (inputProvider == null || stateMachine == null) return;

        Vector3 inputMoveDirection = inputProvider.GetMoveDirection();
        bool isMoving = inputMoveDirection.magnitude > 0.1f;

        if (isMoving)
        {
            stateMachine.ChangeState(playerInteractor.GetHasItemInHandsBool() ? walkWithItemState : walkState);
        }
        else if (playerInteractor.GetIsWorkingBool())
        {
            return; // Do not change state if the player is working
        }
        else
        {
            stateMachine.ChangeState(playerInteractor.GetHasItemInHandsBool() ? idleWithItemState : idleState);
        }

        TryMove(inputMoveDirection);
    }

    private void TryMove(Vector3 inputMoveDirection)
    {
        if (inputMoveDirection.sqrMagnitude > kMinInput)
        {
            // Проверяем препятствия перед движением
            if (IsObstacleInFront(inputMoveDirection))
            {
                return; // Не двигаемся, если впереди препятствие
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
                }
            }
        }
    }
    
    private bool IsObstacleInFront(Vector3 moveDirection)
    {
        Vector3 rayOrigin = transform.position + Vector3.up * 0.1f; // Немного поднимаем луч
        
        // Используем SphereCast для более надежной проверки
        return Physics.SphereCast(
            rayOrigin, 
            obstacleCheckRadius, 
            moveDirection, 
            out RaycastHit hit, 
            obstacleCheckDistance, 
            obstacleLayer
        );
    }
    
    // Для дебага - показывает область проверки препятствий
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