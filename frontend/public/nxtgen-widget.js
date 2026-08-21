(function () {
  "use strict";

  const script =
    document.currentScript;

  if (!script) {
    return;
  }

  const channelId =
    script.dataset.channelId;

  const apiBase =
    script.dataset.apiBase ||
    "http://localhost:8000";

  if (!channelId) {
    return;
  }

  const storagePrefix =
    `nxtgen-widget:${channelId}`;

  const sessionKey =
    `${storagePrefix}:session`;

  let widgetConfig = null;
  let visitorToken = null;
  let tokenExpiresAt = 0;

  let sessionId =
    sessionStorage.getItem(
      sessionKey
    );

  let isOpen = false;
  let isSending = false;
  let isInitializing = false;

  const root =
    document.createElement(
      "div"
    );

  root.id =
    "nxtgen-chat-widget";

  document.body.appendChild(
    root
  );

  const style =
    document.createElement(
      "style"
    );

  style.textContent = `
    #nxtgen-chat-widget {
      position: fixed;
      right: 24px;
      bottom: 24px;
      z-index: 2147483000;
      font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
    }

    #nxtgen-chat-widget * {
      box-sizing: border-box;
    }

    .nxtgen-launcher {
      width: 56px;
      height: 56px;
      border: none;
      border-radius: 999px;
      background: #111827;
      color: #ffffff;
      cursor: pointer;
      font-size: 24px;
      box-shadow:
        0 12px 30px
        rgba(0, 0, 0, 0.22);
    }

    .nxtgen-panel {
      position: absolute;
      right: 0;
      bottom: 72px;
      width: 380px;
      height: 560px;
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-radius: 18px;
      overflow: hidden;
      box-shadow:
        0 20px 60px
        rgba(0, 0, 0, 0.22);
      display: none;
      flex-direction: column;
    }

    .nxtgen-panel.open {
      display: flex;
    }

    .nxtgen-header {
      padding: 16px 18px;
      background: #111827;
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .nxtgen-header-title {
      font-size: 15px;
      font-weight: 600;
      min-width: 0;
      overflow-wrap: anywhere;
      word-break: break-word;
    }

    .nxtgen-close {
      border: none;
      background: transparent;
      color: #ffffff;
      cursor: pointer;
      font-size: 20px;
      flex-shrink: 0;
    }

    .nxtgen-messages {
      flex: 1;
      min-width: 0;
      overflow-y: auto;
      overflow-x: hidden;
      padding: 16px;
      background: #f9fafb;
    }

    .nxtgen-message {
      max-width: 82%;
      min-width: 0;
      padding: 10px 12px;
      margin-bottom: 12px;
      border-radius: 14px;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      word-break: break-word;
      line-height: 1.45;
      font-size: 14px;
    }

    .nxtgen-message.user {
      margin-left: auto;
      background: #111827;
      color: #ffffff;
      border-bottom-right-radius: 4px;
    }

    .nxtgen-message.assistant {
      margin-right: auto;
      background: #ffffff;
      color: #111827;
      border: 1px solid #e5e7eb;
      border-bottom-left-radius: 4px;
    }

    .nxtgen-message.error {
      margin-right: auto;
      background: #fef2f2;
      color: #991b1b;
      border: 1px solid #fecaca;
    }

    .nxtgen-sources {
      width: 100%;
      max-width: 100%;
      min-width: 0;
      margin-top: 10px;
      padding-top: 10px;
      border-top: 1px solid #e5e7eb;
      font-size: 12px;
      line-height: 1.4;
      color: #6b7280;
      overflow: hidden;
    }

    .nxtgen-sources-title {
      font-weight: 600;
      color: #4b5563;
      margin-bottom: 4px;
    }

    .nxtgen-source {
      width: 100%;
      max-width: 100%;
      min-width: 0;
      margin-top: 6px;
      overflow-wrap: anywhere;
      word-break: break-word;
      white-space: normal;
    }

    .nxtgen-input-row {
      display: flex;
      gap: 8px;
      padding: 12px;
      border-top: 1px solid #e5e7eb;
      background: #ffffff;
    }

    .nxtgen-input {
      flex: 1;
      min-width: 0;
      resize: none;
      min-height: 42px;
      max-height: 100px;
      border: 1px solid #d1d5db;
      border-radius: 10px;
      padding: 10px 12px;
      font: inherit;
      outline: none;
    }

    .nxtgen-input:focus {
      border-color: #111827;
    }

    .nxtgen-send {
      border: none;
      border-radius: 10px;
      background: #111827;
      color: #ffffff;
      padding: 0 16px;
      cursor: pointer;
      font-weight: 600;
      flex-shrink: 0;
    }

    .nxtgen-send:disabled {
      opacity: 0.5;
      cursor: default;
    }

    @media (max-width: 480px) {
      #nxtgen-chat-widget {
        right: 12px;
        bottom: 12px;
      }

      .nxtgen-panel {
        position: fixed;
        left: 12px;
        right: 12px;
        top: 12px;
        bottom: 80px;
        width: auto;
        height: auto;
      }
    }
  `;

  document.head.appendChild(
    style
  );

  root.innerHTML = `
    <div class="nxtgen-panel">
      <div class="nxtgen-header">
        <div class="nxtgen-header-title">
          Assistant
        </div>

        <button
          type="button"
          class="nxtgen-close"
          aria-label="Close chat"
        >
          ×
        </button>
      </div>

      <div class="nxtgen-messages">
      </div>

      <div class="nxtgen-input-row">
        <textarea
          class="nxtgen-input"
          rows="1"
          placeholder="Ask a question..."
        ></textarea>

        <button
          type="button"
          class="nxtgen-send"
        >
          Send
        </button>
      </div>
    </div>

    <button
      type="button"
      class="nxtgen-launcher"
      aria-label="Open chat"
    >
      ✦
    </button>
  `;

  const panel =
    root.querySelector(
      ".nxtgen-panel"
    );

  const launcher =
    root.querySelector(
      ".nxtgen-launcher"
    );

  const closeButton =
    root.querySelector(
      ".nxtgen-close"
    );

  const titleElement =
    root.querySelector(
      ".nxtgen-header-title"
    );

  const messagesElement =
    root.querySelector(
      ".nxtgen-messages"
    );

  const inputElement =
    root.querySelector(
      ".nxtgen-input"
    );

  const sendButton =
    root.querySelector(
      ".nxtgen-send"
    );

  function scrollToBottom() {
    messagesElement.scrollTop =
      messagesElement.scrollHeight;
  }

  function addMessage(
    role,
    text
  ) {
    const message =
      document.createElement(
        "div"
      );

    message.className =
      `nxtgen-message ${role}`;

    message.textContent =
      text || "";

    messagesElement.appendChild(
      message
    );

    scrollToBottom();

    return message;
  }

  function addSources(
    messageElement,
    sources
  ) {
    if (
      !widgetConfig ||
      !widgetConfig.show_sources ||
      !sources ||
      !sources.length
    ) {
      return;
    }

    const wrapper =
      document.createElement(
        "div"
      );

    wrapper.className =
      "nxtgen-sources";

    const title =
      document.createElement(
        "div"
      );

    title.className =
      "nxtgen-sources-title";

    title.textContent =
      "Sources";

    wrapper.appendChild(
      title
    );

    const seen =
      new Set();

    for (
      const source
      of sources
    ) {
      const key =
        source.document_id ||
        source.document_name ||
        source.knowledge_source_name;

      if (
        !key ||
        seen.has(key)
      ) {
        continue;
      }

      seen.add(
        key
      );

      const item =
        document.createElement(
          "div"
        );

      item.className =
        "nxtgen-source";

      const sourceName =
        source.document_name ||
        source.knowledge_source_name ||
        "Source";

      item.textContent =
        `• ${sourceName}`;

      wrapper.appendChild(
        item
      );
    }

    messageElement.appendChild(
      wrapper
    );

    scrollToBottom();
  }

  function clearMessages() {
    messagesElement.innerHTML =
      "";
  }

  async function loadConfig() {
    const response =
      await fetch(
        `${apiBase}/public/v1/widget/config/${channelId}`,
        {
          method: "GET",
        }
      );

    if (!response.ok) {
      throw new Error(
        "Unable to load widget configuration."
      );
    }

    widgetConfig =
      await response.json();

    titleElement.textContent =
      widgetConfig.widget_title;

    inputElement.placeholder =
      widgetConfig.placeholder;

    if (
      widgetConfig.welcome_message
    ) {
      clearMessages();

      addMessage(
        "assistant",
        widgetConfig.welcome_message
      );
    }
  }

  function tokenIsValid() {
    return (
      visitorToken &&
      Date.now()
        < tokenExpiresAt
        - 30000
    );
  }

  async function ensureToken() {
    if (
      tokenIsValid()
    ) {
      return visitorToken;
    }

    const response =
      await fetch(
        `${apiBase}/public/v1/widget/session`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body:
            JSON.stringify({
              channel_id:
                channelId,
            }),
        }
      );

    if (!response.ok) {
      throw new Error(
        "Unable to start chat session."
      );
    }

    const data =
      await response.json();

    visitorToken =
      data.token;

    tokenExpiresAt =
      Date.now()
      + (
        data.expires_in
        * 1000
      );

    return visitorToken;
  }

  function parseEventBlock(
    block
  ) {
    let eventType =
      "message";

    const dataLines = [];

    for (
      const line
      of block.split("\n")
    ) {
      if (
        line.startsWith(
          "event:"
        )
      ) {
        eventType =
          line
          .slice(6)
          .trim();

        continue;
      }

      if (
        line.startsWith(
          "data:"
        )
      ) {
        dataLines.push(
          line.slice(5)
        );
      }
    }

    return {
      eventType,
      data:
        dataLines.join(
          "\n"
        ),
    };
  }

  async function sendMessage() {
    const text =
      inputElement
      .value
      .trim();

    if (
      !text ||
      isSending
    ) {
      return;
    }

    if (!widgetConfig) {
      const ready =
        await ensureInitialized();

      if (!ready) {
        return;
      }
    }

    isSending = true;

    sendButton.disabled =
      true;

    inputElement.disabled =
      true;

    addMessage(
      "user",
      text
    );

    inputElement.value =
      "";

    const assistantMessage =
      addMessage(
        "assistant",
        ""
      );

    try {
      const token =
        await ensureToken();

      const body = {
        message:
          text,
      };

      if (
        sessionId
      ) {
        body.session_id =
          sessionId;
      }

      const response =
        await fetch(
          `${apiBase}/public/v1/widget/chat/stream`,
          {
            method:
              "POST",

            headers: {
              "Authorization":
                `Bearer ${token}`,

              "Content-Type":
                "application/json",
            },

            body:
              JSON.stringify(
                body
              ),
          }
        );

      if (!response.ok) {
        const errorBody =
          await response.text();

        throw new Error(
          errorBody ||
          "Chat request failed."
        );
      }

      if (!response.body) {
        throw new Error(
          "Streaming is not supported."
        );
      }

      const reader =
        response.body
        .getReader();

      const decoder =
        new TextDecoder();

      let buffer =
        "";

      let answer =
        "";

      let finished =
        false;

      while (!finished) {
        const {
          value,
          done,
        } = await reader.read();

        if (done) {
          break;
        }

        buffer +=
          decoder.decode(
            value,
            {
              stream: true,
            }
          );

        let separatorIndex;

        while (
          (
            separatorIndex =
              buffer.indexOf(
                "\n\n"
              )
          )
          !== -1
        ) {
          const block =
            buffer
            .slice(
              0,
              separatorIndex
            );

          buffer =
            buffer.slice(
              separatorIndex
              + 2
            );

          if (!block.trim()) {
            continue;
          }

          const event =
            parseEventBlock(
              block
            );

          if (
            event.eventType
            === "message"
          ) {
            answer +=
              event.data;

            assistantMessage
              .textContent =
                answer;

            scrollToBottom();

            continue;
          }

          if (
            event.eventType
            === "metadata"
          ) {
            try {
              const metadata =
                JSON.parse(
                  event.data
                );

              if (
                metadata.session_id
              ) {
                sessionId =
                  metadata.session_id;

                sessionStorage
                  .setItem(
                    sessionKey,
                    sessionId
                  );
              }

              addSources(
                assistantMessage,
                metadata.sources
              );
            } catch {
              // Ignore malformed metadata.
            }

            continue;
          }

          if (
            event.eventType
            === "error"
          ) {
            let message =
              "Something went wrong.";

            try {
              const data =
                JSON.parse(
                  event.data
                );

              message =
                data.message
                || message;
            } catch {
              message =
                event.data
                || message;
            }

            throw new Error(
              message
            );
          }

          if (
            event.eventType
            === "done"
          ) {
            finished =
              true;

            break;
          }
        }
      }

      if (!answer) {
        assistantMessage
          .textContent =
            "No response received.";
      }
    } catch (error) {
      assistantMessage
        .className =
          "nxtgen-message error";

      assistantMessage
        .textContent =
          error instanceof Error
            ? error.message
            : (
              "Something went wrong."
            );
    } finally {
      isSending =
        false;

      sendButton.disabled =
        false;

      inputElement.disabled =
        false;

      inputElement.focus();

      scrollToBottom();
    }
  }

  async function initialize() {
    if (
      widgetConfig
    ) {
      return true;
    }

    if (
      isInitializing
    ) {
      return false;
    }

    isInitializing =
      true;

    try {
      await loadConfig();

      return true;
    } catch {
      return false;
    } finally {
      isInitializing =
        false;
    }
  }

  async function ensureInitialized() {
    if (
      widgetConfig
    ) {
      return true;
    }

    const initialized =
      await initialize();

    if (
      initialized
    ) {
      return true;
    }

    clearMessages();

    titleElement.textContent =
      "Assistant";

    addMessage(
      "error",
      "Chat is temporarily unavailable."
    );

    return false;
  }

  launcher.addEventListener(
    "click",
    async function () {
      isOpen =
        !isOpen;

      panel.classList.toggle(
        "open",
        isOpen
      );

      if (
        !isOpen
      ) {
        return;
      }

      const ready =
        await ensureInitialized();

      if (
        ready
      ) {
        inputElement.focus();
      }
    }
  );

  closeButton.addEventListener(
    "click",
    function () {
      isOpen =
        false;

      panel.classList.remove(
        "open"
      );
    }
  );

  sendButton.addEventListener(
    "click",
    sendMessage
  );

  inputElement.addEventListener(
    "keydown",
    function (event) {
      if (
        event.key
        === "Enter"
        && !event.shiftKey
      ) {
        event.preventDefault();

        sendMessage();
      }
    }
  );

  /*
   * Silent warm-up.
   *
   * If the API is unavailable while the
   * frontend is starting, nothing is logged
   * and nothing alarming is shown.
   *
   * Opening the widget retries initialization.
   */
  initialize().catch(
    function () {
      // Intentionally silent.
    }
  );
})();