using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Stand : MonoBehaviour, IInteractable
{
    private bool isInteracting = false;

    private void OnTriggerStay(Collider other)
    {
        if (isInteracting) return;

        var interactor = other.GetComponent<IInteractor>();
        if (interactor != null)
        {
            StartCoroutine(Interact(interactor));
        }
    }

    public IEnumerator Interact(IInteractor interactor)
    {
        isInteracting = true;
        yield return interactor.InteractWith(this);
        isInteracting = false;
    }
}
