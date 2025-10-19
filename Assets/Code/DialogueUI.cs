using UnityEngine;
using TMPro;

public class DialogueUI : MonoBehaviour
{
    [SerializeField] private GameObject dialoguePanel;
    [SerializeField] private TMP_InputField userInputField;
    [SerializeField] private Messenger messenger; // Ссылка на Messenger
    private System.Action onClose;

    private void Start()
    {
        if (dialoguePanel == null)
        {
            Debug.LogError("dialoguePanel is not assigned in DialogueUI. Please assign in the Inspector.", this);
        }
        if (userInputField == null)
        {
            Debug.LogError("userInputField is not assigned in DialogueUI. Please assign in the Inspector.", this);
        }
        if (messenger == null)
        {
            Debug.LogError("messenger is not assigned in DialogueUI. Please assign in the Inspector.", this);
        }
        if (dialoguePanel != null)
        {
            dialoguePanel.SetActive(false);
        }
    }

    private void Update()
    {
        if (dialoguePanel != null && dialoguePanel.activeSelf)
        {
            if (Input.GetKeyDown(KeyCode.Escape))
            {
                Debug.Log("Dialogue closed via Escape key");
                Close();
            }
            // Поддержка отправки сообщений по Enter
            if (Input.GetKeyDown(KeyCode.Return) && userInputField != null && userInputField.text.Trim() != "")
            {
                AIChatHandler chatHandler = GetComponent<AIChatHandler>();
                if (chatHandler != null)
                {
                    chatHandler.OnSendClicked();
                    Debug.Log("Message sent via Enter key");
                }
            }
        }
    }

    public void Show(System.Action onCloseCallback)
    {
        if (dialoguePanel == null || messenger == null)
        {
            Debug.LogError("Cannot show dialogue: dialoguePanel or messenger is null", this);
            return;
        }

        onClose = onCloseCallback;
        dialoguePanel.SetActive(true);
        // Очищаем сообщения при открытии диалога
        //messenger.ClearMessages();
        // Устанавливаем фокус на поле ввода
        if (userInputField != null)
        {
            userInputField.Select();
            userInputField.ActivateInputField();
        }
        Debug.Log("Dialogue UI shown");
    }

    public void Close()
    {
        if (dialoguePanel == null || messenger == null)
        {
            Debug.LogError("Cannot close dialogue: dialoguePanel or messenger is null", this);
            return;
        }

        dialoguePanel.SetActive(false);
        // Очищаем сообщения при закрытии
        messenger.ClearMessages();
        if (userInputField != null)
        {
            userInputField.text = "";
        }
        onClose?.Invoke();
        Debug.Log("Dialogue UI closed");
    }
}