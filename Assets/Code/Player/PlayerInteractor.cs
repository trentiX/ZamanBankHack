using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlayerInteractor : MonoBehaviour, IInteractor
{
    [SerializeField] private List<GameObject> heldItems = new List<GameObject>();
    [SerializeField] private Animator animator;
    [SerializeField] private float interactCooldown = 0.5f;

    public int maxItemsInHands;
    private StateMachine stateMachine;
    private CharacterAnimator characterAnimator;
    private ICharacterState atCheckoutState;
    private ICharacterState pickingUpState;

    private bool isWorking = false;
    private bool hasItemInHands => heldItems.Count > 0;

    private void Awake()
    {
        characterAnimator = new CharacterAnimator(animator);
        stateMachine = GetComponent<StateMachine>();
        
        atCheckoutState = new AtCheckoutState(characterAnimator);
        pickingUpState = new PickingUpState(characterAnimator);
    }

    public IEnumerator InteractWith(IInteractable interactable)
    {
        yield return new WaitForSeconds(interactCooldown);
    }

    public bool GetIsWorkingBool() => isWorking;
    public bool GetHasItemInHandsBool() => hasItemInHands;
}
