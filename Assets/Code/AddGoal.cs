using UnityEngine;
using TMPro;
using UnityEngine.UI;

public class AddGoal : MonoBehaviour
{
    [SerializeField] private GameObject goalWindow;        // Панель ввода
    [SerializeField] private TMP_InputField nameInput;     // Поле названия
    [SerializeField] private TMP_InputField valueInput;    // Поле значения
    [SerializeField] private Button submitButton;          // Кнопка
    [SerializeField] private GameObject goalTemplate;      // Префаб цели
    [SerializeField] private Transform goalParent;         // Родитель для целей

    private void Start()
    {
        if (submitButton == null)
        {
            Debug.LogError("Кнопка не назначена!");
            return;
        }
        submitButton.onClick.AddListener(OnSubmitGoal);
    }

    public void OpenGoalWindow()
    {
        if (goalWindow != null)
            goalWindow.SetActive(true);
        else
            Debug.LogError("Окно цели не назначено!");
    }

    private void OnSubmitGoal()
    {
        // Проверка полей ввода
        if (nameInput == null || valueInput == null)
        {
            Debug.LogError("Поля ввода не назначены!");
            return;
        }

        string goalName = nameInput.text;
        if (string.IsNullOrEmpty(goalName))
        {
            Debug.LogWarning("Введите название цели!");
            return;
        }

        if (!int.TryParse(valueInput.text, out int goalValue))
        {
            Debug.LogWarning("Введите корректное число!");
            return;
        }

        // Проверка префаба и родителя
        if (goalTemplate == null || goalParent == null)
        {
            Debug.LogError("Префаб или родитель не назначены!");
            return;
        }

        // Создание объекта
        GameObject newGoal = Instantiate(goalTemplate, goalParent);
        newGoal.SetActive(true);

        // Поиск текстовых полей
        TMP_Text goalNameText = newGoal.transform.Find("GoalName")?.GetComponent<TMP_Text>();
        TMP_Text goalProgressText = newGoal.transform.Find("GoalProgress")?.GetComponent<TMP_Text>();

        if (goalNameText == null || goalProgressText == null)
        {
            Debug.LogError("Не найдены GoalName или GoalProgress в префабе!");
            return;
        }

        // Обновление текста
        goalNameText.text = goalName;
        goalProgressText.text = $"0 / {goalValue}";

        // Закрытие окна и очистка полей
        goalWindow.SetActive(false);
        nameInput.text = "";
        valueInput.text = "";
    }
}