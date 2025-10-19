using TMPro;
using UnityEngine;

public class GoalUI : MonoBehaviour
{
    [SerializeField] private TMP_Text goalNameText;
    [SerializeField] private TMP_Text goalProgressText;

    public void SetGoal(string name, int value)
    {
        goalNameText.text = name;
        goalProgressText.text = $"0 / {value}";
    }
}
