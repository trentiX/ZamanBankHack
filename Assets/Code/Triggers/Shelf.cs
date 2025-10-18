using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Shelf : MonoBehaviour, IInteractable
{
    private bool isInteracting = false;
    public System.Action<Shelf> OnShelfEmpty;

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
