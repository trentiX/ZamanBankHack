using UnityEngine;

public class CharacterAnimator
{
    private Animator animator;

    public CharacterAnimator(Animator animator)
    {
        this.animator = animator;
    }

    public void SetOnlyThisState(string trueParam)
    {
        // Сброс всех булов
        animator.SetBool("IsIdle", false);
        animator.SetBool("IsWalkingWithoutItems", false);
        animator.SetBool("IsWalkingWithItems", false);
        animator.SetBool("IsPickingUp", false);
        animator.SetBool("IsAtCheckout", false);
        animator.SetBool("IsIdleWithItems", false);

        // Включаем нужный
        animator.SetBool(trueParam, true);

        // Триггер перехода
        animator.SetTrigger("OnStateChanged");
    }
}
