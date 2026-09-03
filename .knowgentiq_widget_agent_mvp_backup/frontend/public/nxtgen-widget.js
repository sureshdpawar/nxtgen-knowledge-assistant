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
    script.dataset.apiBase
    || "http://localhost:8000";

  if (!channelId) {
    return;
  }

  const prefix =
    `nxtgen-widget:${channelId}`;

  const sessionKey =
    `${prefix}:session`;

  const messagesKey =
    `${prefix}:messages`;

  const tokenKey =
    `${prefix}:token`;

  const expiryKey =
    `${prefix}:token-expiry`;

  let widgetConfig = null;

  let visitorToken =
    sessionStorage.getItem(
      tokenKey,
    );

  let tokenExpiresAt =
    Number(
      sessionStorage.getItem(
        expiryKey,
      )
      || 0,
    );

  let sessionId =
    sessionStorage.getItem(
      sessionKey,
    );

  let isOpen = false;
  let isSending = false;
  let isInitializing = false;
  let isStartingSession = false;


  const root =
    document.createElement(
      "div",
    );

  root.id =
    "nxtgen-chat-widget";

  document.body.appendChild(
    root,
  );


  const style =
    document.createElement(
      "style",
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
      min-width: 108px;
      height: 48px;
      border: none;
      border-radius: 999px;
      background: #475569;
      color: #fff;
      padding: 0 18px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
      box-shadow:
        0 10px 28px
        rgba(15, 23, 42, .18);
    }

    .nxtgen-panel {
      position: absolute;
      right: 0;
      bottom: 62px;
      width: 380px;
      height: 580px;
      background: #fff;
      border:
        1px solid
        #e2e8f0;
      border-radius: 18px;
      overflow: hidden;
      box-shadow:
        0 20px 60px
        rgba(15, 23, 42, .18);
      display: none;
      flex-direction: column;
    }

    .nxtgen-panel.open {
      display: flex;
    }

    .nxtgen-header {
      padding:
        15px
        18px;
      background:
        #475569;
      color:
        #fff;
      display:
        flex;
      align-items:
        center;
      justify-content:
        space-between;
      gap:
        12px;
    }

    .nxtgen-header-left {
      display:
        flex;
      align-items:
        center;
      gap:
        10px;
      min-width:
        0;
    }

    .nxtgen-header-icon {
      width:
        32px;
      height:
        32px;
      border-radius:
        10px;
      background:
        rgba(
          255,
          255,
          255,
          .12
        );
      display:
        grid;
      place-items:
        center;
    }

    .nxtgen-header-title {
      font-size:
        15px;
      font-weight:
        600;
    }

    .nxtgen-header-status {
      margin-top:
        2px;
      font-size:
        11px;
      color:
        #e2e8f0;
    }

    .nxtgen-close {
      width:
        32px;
      height:
        32px;
      border:
        none;
      background:
        transparent;
      color:
        #fff;
      font-size:
        21px;
      cursor:
        pointer;
    }

    .nxtgen-prechat {
      flex:
        1;
      min-height:
        0;
      overflow:
        auto;
      padding:
        22px
        18px;
      background:
        #f8fafc;
      display:
        none;
    }

    .nxtgen-prechat.visible {
      display:
        block;
    }

    .nxtgen-prechat-card {
      border:
        1px solid
        #e2e8f0;
      background:
        #fff;
      border-radius:
        16px;
      padding:
        18px;
    }

    .nxtgen-prechat-title {
      margin:
        0;
      font-size:
        18px;
      color:
        #0f172a;
    }

    .nxtgen-prechat-copy {
      margin:
        6px
        0
        16px;
      font-size:
        13px;
      color:
        #64748b;
      line-height:
        1.5;
    }

    .nxtgen-field {
      margin-top:
        12px;
    }

    .nxtgen-field label {
      display:
        block;
      margin-bottom:
        6px;
      font-size:
        12px;
      font-weight:
        600;
      color:
        #334155;
    }

    .nxtgen-field input {
      width:
        100%;
      height:
        42px;
      border:
        1px solid
        #cbd5e1;
      border-radius:
        10px;
      padding:
        0
        11px;
      font:
        inherit;
      font-size:
        14px;
    }

    .nxtgen-prechat-error {
      display:
        none;
      margin-top:
        12px;
      border:
        1px solid
        #fecaca;
      background:
        #fef2f2;
      color:
        #991b1b;
      border-radius:
        10px;
      padding:
        9px
        10px;
      font-size:
        12px;
    }

    .nxtgen-prechat-error.visible {
      display:
        block;
    }

    .nxtgen-prechat-submit {
      width:
        100%;
      height:
        42px;
      margin-top:
        16px;
      border:
        none;
      border-radius:
        10px;
      background:
        #475569;
      color:
        #fff;
      cursor:
        pointer;
      font-weight:
        600;
    }

    .nxtgen-prechat-submit:disabled {
      opacity:
        .5;
    }

    .nxtgen-chat {
      flex:
        1;
      min-height:
        0;
      display:
        none;
      flex-direction:
        column;
    }

    .nxtgen-chat.visible {
      display:
        flex;
    }

    .nxtgen-messages {
      flex:
        1;
      min-height:
        0;
      overflow:
        auto;
      padding:
        18px
        16px;
      background:
        #f8fafc;
    }

    .nxtgen-message {
      max-width:
        84%;
      padding:
        10px
        12px;
      margin-bottom:
        12px;
      border-radius:
        14px;
      white-space:
        pre-wrap;
      overflow-wrap:
        anywhere;
      line-height:
        1.5;
      font-size:
        14px;
    }

    .nxtgen-message.user {
      margin-left:
        auto;
      background:
        #64748b;
      color:
        #fff;
      border-bottom-right-radius:
        4px;
    }

    .nxtgen-message.assistant {
      margin-right:
        auto;
      background:
        #fff;
      color:
        #0f172a;
      border:
        1px solid
        #e2e8f0;
      border-bottom-left-radius:
        4px;
    }

    .nxtgen-message.error {
      margin-right:
        auto;
      background:
        #fef2f2;
      color:
        #991b1b;
      border:
        1px solid
        #fecaca;
    }

    .nxtgen-sources {
      margin-top:
        10px;
      padding-top:
        10px;
      border-top:
        1px solid
        #e2e8f0;
      font-size:
        12px;
      color:
        #64748b;
    }

    .nxtgen-composer {
      border-top:
        1px solid
        #e2e8f0;
      background:
        #fff;
    }

    .nxtgen-input-row {
      display:
        flex;
      gap:
        8px;
      padding:
        12px
        12px
        6px;
      align-items:
        flex-end;
    }

    .nxtgen-input {
      flex:
        1;
      min-height:
        42px;
      max-height:
        100px;
      resize:
        none;
      border:
        1px solid
        #cbd5e1;
      border-radius:
        12px;
      padding:
        10px
        12px;
      font:
        inherit;
      font-size:
        14px;
    }

    .nxtgen-send {
      min-width:
        64px;
      height:
        42px;
      border:
        none;
      border-radius:
        10px;
      background:
        #475569;
      color:
        #fff;
      cursor:
        pointer;
      font-weight:
        600;
    }

    .nxtgen-send:disabled {
      opacity:
        .45;
    }

    .nxtgen-powered-by {
      display:
        flex;
      align-items:
        center;
      justify-content:
        center;
      gap:
        5px;
      min-height:
        31px;
      padding:
        4px
        10px
        8px;
      color:
        #94a3b8;
      font-size:
        9px;
    }

    .nxtgen-powered-by strong {
      color:
        #64748b;
    }

    @media (
      max-width: 480px
    ) {
      #nxtgen-chat-widget {
        right:
          12px;
        bottom:
          12px;
      }

      .nxtgen-panel {
        position:
          fixed;
        left:
          12px;
        right:
          12px;
        top:
          12px;
        bottom:
          70px;
        width:
          auto;
        height:
          auto;
      }
    }
  `;

  document.head.appendChild(
    style,
  );


  root.innerHTML = `
    <div class="nxtgen-panel">
      <div class="nxtgen-header">
        <div class="nxtgen-header-left">
          <div class="nxtgen-header-icon">✦</div>
          <div>
            <div class="nxtgen-header-title">Assistant</div>
            <div class="nxtgen-header-status">AI-powered assistant</div>
          </div>
        </div>
        <button
          type="button"
          class="nxtgen-close"
        >×</button>
      </div>

      <div class="nxtgen-prechat">
        <div class="nxtgen-prechat-card">
          <h3 class="nxtgen-prechat-title">Before we start</h3>

          <p class="nxtgen-prechat-copy">
            Share your contact details to start the conversation.
          </p>

          <form class="nxtgen-prechat-form">
            <div class="nxtgen-prechat-fields"></div>
            <div class="nxtgen-prechat-error"></div>

            <button
              type="submit"
              class="nxtgen-prechat-submit"
            >
              Start chat
            </button>
          </form>
        </div>
      </div>

      <div class="nxtgen-chat">
        <div class="nxtgen-messages"></div>

        <div class="nxtgen-composer">
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

          <div class="nxtgen-powered-by">
            <strong>Knowgentiq</strong>
            <span>•</span>
            <span>
              A Product Of NXTGEN Innovate Technologies
            </span>
          </div>
        </div>
      </div>
    </div>

    <button
      type="button"
      class="nxtgen-launcher"
    >
      ✦ Ask AI
    </button>
  `;


  const panel =
    root.querySelector(
      ".nxtgen-panel",
    );

  const launcher =
    root.querySelector(
      ".nxtgen-launcher",
    );

  const closeButton =
    root.querySelector(
      ".nxtgen-close",
    );

  const titleElement =
    root.querySelector(
      ".nxtgen-header-title",
    );

  const preChatElement =
    root.querySelector(
      ".nxtgen-prechat",
    );

  const preChatForm =
    root.querySelector(
      ".nxtgen-prechat-form",
    );

  const preChatFields =
    root.querySelector(
      ".nxtgen-prechat-fields",
    );

  const preChatTitle =
    root.querySelector(
      ".nxtgen-prechat-title",
    );

  const preChatError =
    root.querySelector(
      ".nxtgen-prechat-error",
    );

  const preChatSubmit =
    root.querySelector(
      ".nxtgen-prechat-submit",
    );

  const chatElement =
    root.querySelector(
      ".nxtgen-chat",
    );

  const messagesElement =
    root.querySelector(
      ".nxtgen-messages",
    );

  const inputElement =
    root.querySelector(
      ".nxtgen-input",
    );

  const sendButton =
    root.querySelector(
      ".nxtgen-send",
    );


  function tokenIsValid() {
    return Boolean(
      visitorToken
      &&
      Date.now()
      <
      tokenExpiresAt
      - 30000,
    );
  }


  function persistToken(
    token,
    expiresIn,
  ) {
    visitorToken =
      token;

    tokenExpiresAt =
      Date.now()
      + (
        expiresIn
        * 1000
      );

    sessionStorage.setItem(
      tokenKey,
      visitorToken,
    );

    sessionStorage.setItem(
      expiryKey,
      String(
        tokenExpiresAt,
      ),
    );
  }


  function showChat() {
    preChatElement
      .classList
      .remove(
        "visible",
      );

    chatElement
      .classList
      .add(
        "visible",
      );

    setTimeout(
      () =>
        inputElement.focus(),
      0,
    );
  }


  function showPreChat() {
    chatElement
      .classList
      .remove(
        "visible",
      );

    preChatElement
      .classList
      .add(
        "visible",
      );
  }


  function scrollToBottom() {
    messagesElement.scrollTop =
      messagesElement.scrollHeight;
  }


  function persistMessages() {
    try {
      sessionStorage.setItem(
        messagesKey,
        messagesElement.innerHTML,
      );
    } catch {
      // storage may be blocked
    }
  }


  function restoreMessages() {
    try {
      const stored =
        sessionStorage.getItem(
          messagesKey,
        );

      if (!stored) {
        return false;
      }

      messagesElement.innerHTML =
        stored;

      scrollToBottom();

      return true;

    } catch {
      return false;
    }
  }


  function addMessage(
    role,
    text,
  ) {
    const message =
      document.createElement(
        "div",
      );

    message.className =
      `nxtgen-message ${role}`;

    message.textContent =
      text
      || "";

    messagesElement.appendChild(
      message,
    );

    persistMessages();
    scrollToBottom();

    return message;
  }


  function addSources(
    messageElement,
    sources,
  ) {
    if (
      !widgetConfig
      ||
      !widgetConfig.show_sources
      ||
      !Array.isArray(
        sources,
      )
      ||
      !sources.length
    ) {
      return;
    }

    const wrapper =
      document.createElement(
        "div",
      );

    wrapper.className =
      "nxtgen-sources";

    wrapper.textContent =
      "Sources";

    const seen =
      new Set();

    for (
      const source
      of sources
    ) {
      const key =
        source.document_id
        ||
        source.document_name
        ||
        source.knowledge_source_name;

      if (
        !key
        ||
        seen.has(
          key,
        )
      ) {
        continue;
      }

      seen.add(
        key,
      );

      const item =
        document.createElement(
          "div",
        );

      item.textContent =
        `• ${
          source.document_name
          ||
          source.knowledge_source_name
          ||
          "Source"
        }`;

      wrapper.appendChild(
        item,
      );
    }

    messageElement.appendChild(
      wrapper,
    );

    persistMessages();
  }


  function setPreChatError(
    message,
  ) {
    preChatError.textContent =
      message
      || "";

    preChatError
      .classList
      .toggle(
        "visible",
        Boolean(
          message,
        ),
      );
  }


  function renderPreChat() {
    const preChat =
      widgetConfig
      ?.pre_chat;

    preChatFields.innerHTML =
      "";

    preChatTitle.textContent =
      preChat?.title
      || "Before we start";

    preChatSubmit.textContent =
      preChat?.submit_label
      || "Start chat";

    for (
      const field
      of (
        preChat?.fields
        || []
      )
    ) {
      const wrapper =
        document.createElement(
          "div",
        );

      wrapper.className =
        "nxtgen-field";

      const label =
        document.createElement(
          "label",
        );

      label.textContent =
        field.required
          ? `${field.label} *`
          : field.label;

      const input =
        document.createElement(
          "input",
        );

      input.name =
        field.name;

      input.type =
        field.input_type
        || "text";

      input.required =
        Boolean(
          field.required,
        );

      input.placeholder =
        field.placeholder
        || "";

      wrapper.appendChild(
        label,
      );

      wrapper.appendChild(
        input,
      );

      preChatFields.appendChild(
        wrapper,
      );
    }
  }


  async function loadConfig() {
    const response =
      await fetch(
        `${apiBase}/public/v1/widget/config/${channelId}`,
        {
          method:
            "GET",
        },
      );

    if (!response.ok) {
      throw new Error(
        "Unable to load widget configuration.",
      );
    }

    widgetConfig =
      await response.json();

    titleElement.textContent =
      widgetConfig.widget_title;

    inputElement.placeholder =
      widgetConfig.placeholder;

    if (
      !restoreMessages()
      &&
      widgetConfig.welcome_message
    ) {
      addMessage(
        "assistant",
        widgetConfig.welcome_message,
      );
    }

    const requiresPreChat =
      widgetConfig.execution_mode
      === "AGENT"
      &&
      widgetConfig.pre_chat
        ?.enabled;

    if (
      requiresPreChat
      &&
      !tokenIsValid()
    ) {
      renderPreChat();
      showPreChat();

    } else {
      showChat();
    }
  }


  async function createSession(
    visitor,
  ) {
    const response =
      await fetch(
        `${apiBase}/public/v1/widget/session`,
        {
          method:
            "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body:
            JSON.stringify({
              channel_id:
                channelId,
              visitor:
                visitor
                || {},
            }),
        },
      );

    if (!response.ok) {
      let message =
        "Unable to start chat session.";

      try {
        const data =
          await response.json();

        message =
          data.detail
          || message;

      } catch {
        // use default
      }

      throw new Error(
        message,
      );
    }

    const data =
      await response.json();

    persistToken(
      data.token,
      data.expires_in,
    );

    if (
      widgetConfig
        ?.execution_mode
      === "AGENT"
      &&
      data.thread_id
    ) {
      sessionId =
        data.thread_id;

      sessionStorage.setItem(
        sessionKey,
        sessionId,
      );
    }

    return data;
  }


  async function ensureToken() {
    if (
      tokenIsValid()
    ) {
      return visitorToken;
    }

    const requiresPreChat =
      widgetConfig
        ?.execution_mode
      === "AGENT"
      &&
      widgetConfig
        ?.pre_chat
        ?.enabled;

    if (
      requiresPreChat
    ) {
      showPreChat();

      throw new Error(
        "Please complete your contact details before starting the chat.",
      );
    }

    await createSession(
      {},
    );

    return visitorToken;
  }


  function parseEventBlock(
    block,
  ) {
    let eventType =
      "message";

    const dataLines =
      [];

    for (
      const line
      of block.split(
        "\n",
      )
    ) {
      if (
        line.startsWith(
          "event:",
        )
      ) {
        eventType =
          line.slice(
            6,
          ).trim();

      } else if (
        line.startsWith(
          "data:",
        )
      ) {
        let value =
          line.slice(
            5,
          );

        if (
          value.startsWith(
            " ",
          )
        ) {
          value =
            value.slice(
              1,
            );
        }

        dataLines.push(
          value,
        );
      }
    }

    return {
      eventType,
      data:
        dataLines.join(
          "\n",
        ),
    };
  }


  async function sendMessage() {
    const text =
      inputElement
        .value
        .trim();

    if (
      !text
      ||
      isSending
    ) {
      return;
    }

    if (
      !widgetConfig
      &&
      !(
        await ensureInitialized()
      )
    ) {
      return;
    }

    isSending =
      true;

    sendButton.disabled =
      true;

    inputElement.disabled =
      true;

    addMessage(
      "user",
      text,
    );

    inputElement.value =
      "";

    const assistantMessage =
      addMessage(
        "assistant",
        "",
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
        &&
        widgetConfig
          ?.execution_mode
        === "KNOWLEDGE"
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
              Authorization:
                `Bearer ${token}`,

              "Content-Type":
                "application/json",
            },

            body:
              JSON.stringify(
                body,
              ),
          },
        );

      if (!response.ok) {
        throw new Error(
          await response.text(),
        );
      }

      if (!response.body) {
        throw new Error(
          "Streaming is not supported.",
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

      while (
        !finished
      ) {
        const {
          value,
          done,
        } =
          await reader.read();

        if (done) {
          buffer +=
            decoder.decode();

          break;
        }

        buffer +=
          decoder.decode(
            value,
            {
              stream:
                true,
            },
          );

        let separatorIndex;

        while (
          (
            separatorIndex =
              buffer.indexOf(
                "\n\n",
              )
          )
          !== -1
        ) {
          const block =
            buffer.slice(
              0,
              separatorIndex,
            );

          buffer =
            buffer.slice(
              separatorIndex
              + 2,
            );

          if (
            !block.trim()
          ) {
            continue;
          }

          const event =
            parseEventBlock(
              block,
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

            persistMessages();
            scrollToBottom();

          } else if (
            event.eventType
            === "metadata"
          ) {
            try {
              const metadata =
                JSON.parse(
                  event.data,
                );

              if (
                metadata.session_id
              ) {
                sessionId =
                  metadata.session_id;

                sessionStorage.setItem(
                  sessionKey,
                  sessionId,
                );
              }

              addSources(
                assistantMessage,
                metadata.sources,
              );

            } catch {
              // answer still renders
            }

          } else if (
            event.eventType
            === "error"
          ) {
            let message =
              "Something went wrong.";

            try {
              message =
                JSON.parse(
                  event.data,
                ).message
                || message;

            } catch {
              message =
                event.data
                || message;
            }

            throw new Error(
              message,
            );

          } else if (
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

        persistMessages();
      }

    } catch (
      error
    ) {
      assistantMessage
        .className =
          "nxtgen-message error";

      assistantMessage
        .textContent =
          error instanceof Error
            ? error.message
            : "Something went wrong.";

      persistMessages();

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

    if (
      await initialize()
    ) {
      return true;
    }

    chatElement
      .classList
      .add(
        "visible",
      );

    addMessage(
      "error",
      "Chat is temporarily unavailable.",
    );

    return false;
  }


  preChatForm.addEventListener(
    "submit",
    async (
      event,
    ) => {
      event.preventDefault();

      if (
        isStartingSession
      ) {
        return;
      }

      isStartingSession =
        true;

      preChatSubmit.disabled =
        true;

      setPreChatError(
        null,
      );

      try {
        const formData =
          new FormData(
            preChatForm,
          );

        const visitor =
          {};

        for (
          const field
          of (
            widgetConfig
              ?.pre_chat
              ?.fields
            || []
          )
        ) {
          visitor[
            field.name
          ] =
            String(
              formData.get(
                field.name,
              )
              || "",
            ).trim();
        }

        await createSession(
          visitor,
        );

        showChat();

      } catch (
        error
      ) {
        setPreChatError(
          error instanceof Error
            ? error.message
            : "Unable to start chat.",
        );

      } finally {
        isStartingSession =
          false;

        preChatSubmit.disabled =
          false;
      }
    },
  );


  launcher.addEventListener(
    "click",
    async () => {
      isOpen =
        !isOpen;

      panel
        .classList
        .toggle(
          "open",
          isOpen,
        );

      if (!isOpen) {
        return;
      }

      if (
        await ensureInitialized()
      ) {
        scrollToBottom();
      }
    },
  );


  closeButton.addEventListener(
    "click",
    () => {
      isOpen =
        false;

      panel
        .classList
        .remove(
          "open",
        );
    },
  );


  sendButton.addEventListener(
    "click",
    sendMessage,
  );


  inputElement.addEventListener(
    "keydown",
    (
      event,
    ) => {
      if (
        event.key
        === "Enter"
        &&
        !event.shiftKey
      ) {
        event.preventDefault();

        sendMessage();
      }
    },
  );


  initialize().catch(
    () => {},
  );
})();
