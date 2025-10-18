using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;

public class StateMachine : MonoBehaviour
{
    private ICharacterState currentState;

    public void ChangeState(ICharacterState newState)
    {
        if (currentState == newState) return;

        currentState?.Exit();
        currentState = newState;
        currentState?.Enter();
    }

    private void Update()
    {
        currentState?.Tick();
    }
}




public class IdleState : ICharacterState
{
    private readonly CharacterAnimator characterAnimator;

    public IdleState(CharacterAnimator animator)
    {
        characterAnimator = animator;
    }

    public void Enter()
    {
        characterAnimator.SetOnlyThisState("IsIdle");
    }

    public void Exit() { }
    public void Tick() { }
}

public class WalkWithoutItemsState : ICharacterState
{
    private readonly CharacterAnimator characterAnimator;

    public WalkWithoutItemsState(CharacterAnimator animator)
    {
        characterAnimator = animator;
    }

    public void Enter()
    {
        characterAnimator.SetOnlyThisState("IsWalkingWithoutItems");
    }

    public void Exit() { }
    public void Tick() { }
}

public class WalkWithItemsState : ICharacterState
{
    private readonly CharacterAnimator characterAnimator;

    public WalkWithItemsState(CharacterAnimator animator)
    {
        characterAnimator = animator;
    }

    public void Enter()
    {
        characterAnimator.SetOnlyThisState("IsWalkingWithItems");
    }

    public void Exit() { }
    public void Tick() { }
}

public class PickingUpState : ICharacterState
{
    private readonly CharacterAnimator characterAnimator;

    public PickingUpState(CharacterAnimator animator)
    {
        characterAnimator = animator;
    }

    public void Enter()
    {
        characterAnimator.SetOnlyThisState("IsPickingUp");
    }

    public void Exit() { }
    public void Tick() { }
}

public class AtCheckoutState : ICharacterState
{
    private readonly CharacterAnimator characterAnimator;

    public AtCheckoutState(CharacterAnimator animator)
    {
        characterAnimator = animator;
    }

    public void Enter()
    {
        characterAnimator.SetOnlyThisState("IsAtCheckout");
    }

    public void Exit() { }
    public void Tick() { }
}

public class IdleWithItemsState : ICharacterState
{
    private readonly CharacterAnimator characterAnimator;

    public IdleWithItemsState(CharacterAnimator animator)
    {
        characterAnimator = animator;
    }

    public void Enter()
    {
        characterAnimator.SetOnlyThisState("IsIdleWithItems");
    }

    public void Exit() { }
    public void Tick() { }
}

public class WalkToTargetState : ICharacterState
{
    private readonly NavMeshAgent agent;
    private readonly Transform target;
    private readonly CharacterAnimator animator;
    private readonly System.Action onReached;

    public WalkToTargetState(NavMeshAgent agent, Transform target, CharacterAnimator animator, System.Action onReached)
    {
        this.agent = agent;
        this.target = target;
        this.animator = animator;
        this.onReached = onReached;
    }

    public void Enter()
    {
        agent.isStopped = false;
        agent.SetDestination(target.position);
        animator.SetOnlyThisState("IsWalkingWithoutItems");
    }

    public void Exit()
    {
        agent.isStopped = true;
    }

    public void Tick()
    {
        if (!agent.pathPending && agent.remainingDistance < 0.3f)
        {
            onReached?.Invoke(); // Сообщить NPCBrain, что цель достигнута
        }
    }
}

public class WalkToTargetStateWithItems : ICharacterState
{
    private readonly NavMeshAgent agent;
    private readonly Transform target;
    private readonly CharacterAnimator animator;
    private readonly System.Action onReached;

    public WalkToTargetStateWithItems(NavMeshAgent agent, Transform target, CharacterAnimator animator, System.Action onReached)
    {
        this.agent = agent;
        this.target = target;
        this.animator = animator;
        this.onReached = onReached;
    }

    public void Enter()
    {
        agent.isStopped = false;
        agent.SetDestination(target.position);
        animator.SetOnlyThisState("IsWalkingWithItems");
    }

    public void Exit()
    {
        agent.isStopped = true;
    }

    public void Tick()
    {
        if (!agent.pathPending && agent.remainingDistance < 0.3f)
        {
            onReached?.Invoke(); // Сообщить NPCBrain, что цель достигнута
        }
    }
}
