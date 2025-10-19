using UnityEngine;

[RequireComponent(typeof(Animator))]
public class NPCMovementController : MonoBehaviour
{
    [SerializeField] private Animator animator;
    [SerializeField] private bool hasItemInHands = false; // Публичное поле для управления анимацией

    private StateMachine stateMachine;
    private CharacterAnimator characterAnimator;

    private ICharacterState idleState;
    private ICharacterState idleWithItemState;

    private void Awake()
    {
        stateMachine = GetComponent<StateMachine>();
        if (animator == null) animator = GetComponent<Animator>();

        // Проверка на null
        if (stateMachine == null || animator == null)
        {
            Debug.LogError("Required components missing in NPCMovementController", this);
            return;
        }

        characterAnimator = new CharacterAnimator(animator);

        // Инициализация состояний
        idleState = new IdleState(characterAnimator);
        idleWithItemState = new IdleWithItemsState(characterAnimator);
    }

    private void Update()
    {
        UpdateState();
    }

    private void UpdateState()
    {
        // Устанавливаем состояние простоя в зависимости от наличия предмета
        stateMachine.ChangeState(hasItemInHands ? idleWithItemState : idleState);
        Debug.Log($"NPC state set to: {(hasItemInHands ? "IdleWithItems" : "Idle")}");
    }

    // Публичный метод для управления состоянием предметов
    public void SetHasItemInHands(bool hasItems)
    {
        hasItemInHands = hasItems;
        Debug.Log($"NPC hasItemInHands set to: {hasItemInHands}");
    }
}