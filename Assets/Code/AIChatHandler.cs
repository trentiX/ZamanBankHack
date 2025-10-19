using UnityEngine;
using UnityEngine.Networking;
using TMPro;
using UnityEngine.UI;
using System.Collections;
using Newtonsoft.Json;

public class AIChatHandler : MonoBehaviour
{
    [Header("Server Settings")]
    [SerializeField] private string backendUrl = "https://nonsubmissible-nondeflationary-aryanna.ngrok-free.dev/npc";

    [Header("UI Elements")]
    [SerializeField] private TMP_InputField userInputField;
    [SerializeField] private Button sendButton;
    [SerializeField] private Messenger messenger;
    
    [Header("Server URL Input (WebGL)")]
    [SerializeField] private TMP_InputField serverUrlInput;
    [SerializeField] private Button applyUrlButton;
    
    private GameObject thinkingMessage;

    private void Awake()
    {
        if (serverUrlInput != null)
        {
            serverUrlInput.text = backendUrl;
            Debug.Log("[Init] serverUrlInput установлено на: " + backendUrl);
        }

        if (applyUrlButton != null)
            applyUrlButton.onClick.AddListener(OnApplyUrlClicked);
    }

    private void Start()
    {
        if (sendButton != null)
            sendButton.onClick.AddListener(OnSendClicked);
    }

    private void OnApplyUrlClicked()
    {
        if (serverUrlInput == null)
        {
            Debug.LogWarning("[Apply] serverUrlInput не назначено!");
            return;
        }

        string url = serverUrlInput.text.Trim();
        Debug.Log("[Apply] Введён URL: " + url);

        if (string.IsNullOrEmpty(url))
        {
            Debug.LogWarning("[Apply] Пустой URL, установка отменена");
            return;
        }

        if (!IsValidHttpUrl(url))
        {
            Debug.LogWarning("[Apply] Некорректный URL. Должен начинаться с http:// или https://");
            return;
        }

        backendUrl = url;
        Debug.Log("[Apply] Backend URL обновлён: " + backendUrl);
    }

    public void OnSendClicked()
    {
        if (userInputField == null || string.IsNullOrEmpty(userInputField.text.Trim()))
        {
            Debug.LogWarning("[Send] Нет текста для отправки");
            return;
        }

        string userMessage = userInputField.text.Trim();
        userInputField.text = "";

        Debug.Log("[Send] Отправка сообщения: \"" + userMessage + "\" на URL: " + backendUrl);
        messenger?.AppendMessage($"<color=#00ff90><b>Вы:</b></color> {userMessage}", true);

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
                thinkingMessage = messenger.AppendMessage("<color=grey>ИИ думает...</color>", false);

            yield return req.SendWebRequest();

            if (req.result == UnityWebRequest.Result.Success)
            {
                string rawResponse = req.downloadHandler.text;
                Debug.Log("[Response] Получено с сервера: " + rawResponse);

                try
                {
                    ResponseData response = JsonConvert.DeserializeObject<ResponseData>(rawResponse);
                    string reply = !string.IsNullOrEmpty(response.reply) ? response.reply : response.analysis;

                    if (!string.IsNullOrEmpty(reply) && messenger != null && thinkingMessage != null)
                        messenger.ReplaceMessage(thinkingMessage, $"<color=#ffcc00><b>ИИ:</b></color> {reply}", false);
                    else if (messenger != null && thinkingMessage != null)
                        messenger.ReplaceMessage(thinkingMessage, "<color=red>Ошибка: сервер вернул пустой ответ.</color>", false);

                    Debug.Log("[Response] Ответ обработан: " + reply);
                }
                catch
                {
                    Debug.LogError("[Response] Ошибка при разборе ответа сервера");
                    if (messenger != null && thinkingMessage != null)
                        messenger.ReplaceMessage(thinkingMessage, "<color=red>Ошибка: не удалось прочитать ответ сервера.</color>", false);
                }
            }
            else
            {
                Debug.LogError("[Error] Ошибка запроса (" + req.responseCode + "): " + req.error);
                if (messenger != null && thinkingMessage != null)
                    messenger.ReplaceMessage(thinkingMessage, $"<color=red>Ошибка запроса ({req.responseCode}): {req.error}</color>", false);
            }

            thinkingMessage = null;
        }
    }

    private bool IsValidHttpUrl(string url)
    {
        return url.StartsWith("http://") || url.StartsWith("https://");
    }

    [System.Serializable]
    public class MessageData { public string text; }

    [System.Serializable]
    public class ResponseData { public string reply; public string analysis; }
}
