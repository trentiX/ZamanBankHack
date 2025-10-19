using UnityEngine;
using UnityEngine.Networking;
using TMPro;
using UnityEngine.UI;
using System.Collections;
using Newtonsoft.Json;

public class AIChatHandler : MonoBehaviour
{
    [Header("Server Settings")]
    [SerializeField] private string backendUrl = "http://127.0.0.1:8000/chat"; // Эндпоинт FastAPI

    [Header("UI Elements")]
    [SerializeField] private TMP_InputField userInputField;
    [SerializeField] private Button sendButton;
    [SerializeField] private Messenger messenger; // Ссылка на Messenger

    private GameObject thinkingMessage; // Хранит сообщение "ИИ думает..."

    private void Start()
    {
        if (userInputField == null)
        {
            Debug.LogError("userInputField is not assigned in AIChatHandler. Please assign in the Inspector.", this);
        }
        if (sendButton == null)
        {
            Debug.LogError("sendButton is not assigned in AIChatHandler. Please assign in the Inspector.", this);
        }
        if (messenger == null)
        {
            Debug.LogError("messenger is not assigned in AIChatHandler. Please assign in the Inspector.", this);
        }

        // Настраиваем кнопку отправки
        if (sendButton != null)
        {
            sendButton.onClick.AddListener(OnSendClicked);
        }
    }

    public void OnSendClicked()
    {
        if (userInputField == null || string.IsNullOrEmpty(userInputField.text.Trim()))
        {
            Debug.LogWarning("No input or userInputField is null, cannot send message");
            return;
        }

        string userMessage = userInputField.text.Trim();
        // Добавляем сообщение игрока в Messenger
        if (messenger != null)
        {
            messenger.AppendMessage($"<color=#00ff90><b>Вы:</b></color> {userMessage}", true);
        }
        userInputField.text = "";

        StartCoroutine(SendMessageToBackend(userMessage));
    }

    private IEnumerator SendMessageToBackend(string message)
    {
        var payload = new MessageData { text = message };
        string json = JsonConvert.SerializeObject(payload);
        byte[] body = System.Text.Encoding.UTF8.GetBytes(json);

        using (UnityWebRequest req = new UnityWebRequest(backendUrl, "POST"))
        {
            req.uploadHandler = new UploadHandlerRaw(body);
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/json");

            if (messenger != null)
            {
                thinkingMessage = messenger.AppendMessage("<color=grey>ИИ думает...</color>", false);
            }
            yield return req.SendWebRequest();

            if (req.result == UnityWebRequest.Result.Success)
            {
                string rawResponse = req.downloadHandler.text;
                Debug.Log("Ответ сервера: " + rawResponse);

                try
                {
                    ResponseData response = JsonConvert.DeserializeObject<ResponseData>(rawResponse);
                    string reply = !string.IsNullOrEmpty(response.reply) ? response.reply : response.analysis;
                    if (!string.IsNullOrEmpty(reply) && messenger != null && thinkingMessage != null)
                    {
                        messenger.ReplaceMessage(thinkingMessage, $"<color=#ffcc00><b>ИИ:</b></color> {reply}", false);
                    }
                    else if (messenger != null)
                    {
                        if (thinkingMessage != null)
                        {
                            messenger.ReplaceMessage(thinkingMessage, "<color=red>Ошибка: сервер вернул пустой ответ.</color>", false);
                        }
                        else
                        {
                            messenger.AppendMessage("<color=red>Ошибка: сервер вернул пустой ответ.</color>", false);
                        }
                    }
                }
                catch
                {
                    if (messenger != null && thinkingMessage != null)
                    {
                        messenger.ReplaceMessage(thinkingMessage, "<color=red>Ошибка: не удалось прочитать ответ сервера.</color>", false);
                    }
                    else if (messenger != null)
                    {
                        messenger.AppendMessage("<color=red>Ошибка: не удалось прочитать ответ сервера.</color>", false);
                    }
                }
            }
            else
            {
                if (messenger != null && thinkingMessage != null)
                {
                    messenger.ReplaceMessage(thinkingMessage, $"<color=red>Ошибка запроса ({req.responseCode}): {req.error}</color>", false);
                }
                else if (messenger != null)
                {
                    messenger.AppendMessage($"<color=red>Ошибка запроса ({req.responseCode}): {req.error}</color>", false);
                }
            }

            thinkingMessage = null; // Сбрасываем ссылку после обработки
        }
    }

    [System.Serializable]
    public class MessageData
    {
        public string text;
    }

    [System.Serializable]
    public class ResponseData
    {
        public string reply;     // Основной ответ
        public string analysis;  // Если сервер шлёт analysis
    }
}