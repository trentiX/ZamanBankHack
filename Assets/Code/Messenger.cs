using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;

public class Messenger : MonoBehaviour
{
    [Header("Messages")]
    [SerializeField] private GameObject messageTemplate; // Шаблон для сообщений ИИ (слева)
    [SerializeField] private GameObject responseTemplate; // Шаблон для сообщений игрока (справа)
    [SerializeField] private GameObject messageBox; // Контейнер для сообщений (с VerticalLayoutGroup)

    private List<GameObject> messageObjects = new List<GameObject>(); // Список всех сообщений

    private void Start()
    {
        // Проверка на null для всех сериализованных полей
        if (messageTemplate == null)
        {
            Debug.LogError("messageTemplate is not assigned in Messenger. Please assign a prefab from Assets/Prefabs.", this);
        }
        if (responseTemplate == null)
        {
            Debug.LogError("responseTemplate is not assigned in Messenger. Please assign a prefab from Assets/Prefabs.", this);
        }
        if (messageBox == null)
        {
            Debug.LogError("messageBox is not assigned in Messenger. Please assign a GameObject with VerticalLayoutGroup.", this);
        }
        else if (messageBox.GetComponent<VerticalLayoutGroup>() == null)
        {
            Debug.LogError("messageBox does not have a VerticalLayoutGroup component. Please add one.", messageBox);
        }
    }

    public GameObject AppendMessage(string message, bool isPlayer)
    {
        // Проверка на null перед созданием сообщения
        GameObject template = isPlayer ? responseTemplate : messageTemplate;
        if (template == null)
        {
            Debug.LogError($"Cannot append message: {(isPlayer ? "responseTemplate" : "messageTemplate")} is null", this);
            return null;
        }
        if (messageBox == null)
        {
            Debug.LogError("Cannot append message: messageBox is null", this);
            return null;
        }

        // Создаем сообщение
        GameObject newMessage = Instantiate(template, messageBox.transform);
        newMessage.SetActive(true);

        // Устанавливаем текст сообщения
        TextMeshProUGUI textComponent = newMessage.GetComponentInChildren<TextMeshProUGUI>();
        if (textComponent != null)
        {
            textComponent.text = message;
            // Настраиваем выравнивание: слева для ИИ, справа для игрока
            textComponent.alignment = isPlayer ? TextAlignmentOptions.Right : TextAlignmentOptions.Left;
        }
        else
        {
            Debug.LogError("TextMeshProUGUI component not found in message template", newMessage);
        }

        // Добавляем сообщение в список
        messageObjects.Add(newMessage);

        // Перестраиваем layout
        LayoutRebuilder.ForceRebuildLayoutImmediate(messageBox.GetComponent<RectTransform>());
        Debug.Log($"Message added: {message} (isPlayer: {isPlayer})");

        return newMessage; // Возвращаем созданный GameObject
    }

    public void ReplaceMessage(GameObject messageObject, string newMessage, bool isPlayer)
    {
        if (messageObject == null)
        {
            Debug.LogError("Cannot replace message: messageObject is null", this);
            return;
        }

        // Находим TextMeshProUGUI в сообщении
        TextMeshProUGUI textComponent = messageObject.GetComponentInChildren<TextMeshProUGUI>();
        if (textComponent != null)
        {
            textComponent.text = newMessage;
            // Обновляем выравнивание, если нужно
            textComponent.alignment = isPlayer ? TextAlignmentOptions.Right : TextAlignmentOptions.Left;
        }
        else
        {
            Debug.LogError("TextMeshProUGUI component not found in message object", messageObject);
        }

        // Перестраиваем layout
        if (messageBox != null)
        {
            LayoutRebuilder.ForceRebuildLayoutImmediate(messageBox.GetComponent<RectTransform>());
        }
        Debug.Log($"Message replaced: {newMessage} (isPlayer: {isPlayer})");
    }

    public void ClearMessages()
    {
        if (messageBox == null)
        {
            Debug.LogError("messageBox is null, cannot clear messages", this);
            return;
        }

        // Удаляем все сообщения из messageBox
        foreach (Transform child in messageBox.transform)
        {
            Debug.Log($"Destroying message child: {child.name}", child);
            Destroy(child.gameObject);
        }
        messageObjects.Clear(); // Очищаем список
        LayoutRebuilder.ForceRebuildLayoutImmediate(messageBox.GetComponent<RectTransform>());
        Debug.Log("Messages cleared");
    }
}