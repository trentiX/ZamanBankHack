using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public interface IMovementInputProvider
{
    Vector3 GetMoveDirection();
}
