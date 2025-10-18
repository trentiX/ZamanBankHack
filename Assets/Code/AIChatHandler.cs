using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using TMPro;
using UnityEngine.UI;

public class AIChatHandler : MonoBehaviour
{
    [Header("UI Elements")]
    public TMP_InputField userInputField;
    public TextMeshProUGUI chatOutputText;
    public Button sendButton;

    [Header("Server Settings")]
    public string backendUrl = "http://127.0.0.1:8000/analyze"; // поменяй, если используешь ngrok или Render

    private void Start()
    {
        sendButton.onClick.AddListener(OnSendClicked);
    }

    private void OnSendClicked()
    {
        string userMessage = userInputField.text.Trim();
        if (string.IsNullOrEmpty(userMessage))
            return;

        AppendMessage($"<color=#00ff90><b>Вы:</b></color> {userMessage}");
        userInputField.text = "";
        StartCoroutine(SendQueryToBackend(userMessage));
    }

    private IEnumerator SendQueryToBackend(string message)
    {
        // Создаём JSON
        string json = JsonUtility.ToJson(new QueryData(message));
        byte[] body = System.Text.Encoding.UTF8.GetBytes(json);

        using (UnityWebRequest req = new UnityWebRequest(backendUrl, "POST"))
        {
            req.uploadHandler = new UploadHandlerRaw(body);
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/json");

            AppendMessage("<color=grey>ИИ думает...</color>");
            yield return req.SendWebRequest();

            if (req.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    BackendResponse response = JsonUtility.FromJson<BackendResponse>(req.downloadHandler.text);
                    AppendMessage($"<color=#ffcc00><b>ИИ:</b></color> {response.analysis}");
                }
                catch
                {
                    AppendMessage("<color=red>Ошибка чтения ответа.</color>");
                }
            }
            else
            {
                AppendMessage("<color=red>Ошибка подключения: " + req.error + "</color>");
            }
        }
    }

    private void AppendMessage(string msg)
    {
        chatOutputText.text += "\n" + msg;
    }

    [System.Serializable]
    public class QueryData
    {
        public string query;
        public QueryData(string q) { query = q; }
    }

    [System.Serializable]
    public class BackendResponse
    {
        public string analysis;
        public string goal_progress;
    }
}
