(function () {
  "use strict";

  const script = document.currentScript;

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

  /*
   * Storage is scoped by ChatChannel.
   *
   * sessionStorage gives us:
   *
   * - navigation in same tab -> retained
   * - refresh -> retained
   * - new tab -> new conversation
   * - closing tab -> conversation removed
   */
  const storagePrefix =
    `nxtgen-widget:${channelId}`;

  const sessionKey =
    `${storagePrefix}:session`;

  const messagesKey =
    `${storagePrefix}:messages`;

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


    /*
     * ======================================================
     * Launcher
     * ======================================================
     */

    .nxtgen-launcher {
      min-width: 108px;
      height: 48px;

      border: none;
      border-radius: 999px;

      background: #475569;
      color: #ffffff;

      cursor: pointer;

      padding: 0 18px;

      display: flex;
      align-items: center;
      justify-content: center;

      gap: 8px;

      font-size: 14px;
      font-weight: 600;

      letter-spacing: 0.01em;

      box-shadow:
        0 10px 28px
        rgba(15, 23, 42, 0.18);

      transition:
        background 0.2s ease,
        transform 0.2s ease,
        box-shadow 0.2s ease;
    }

    .nxtgen-launcher:hover {
      background: #334155;

      transform:
        translateY(-1px);

      box-shadow:
        0 14px 32px
        rgba(15, 23, 42, 0.22);
    }

    .nxtgen-launcher:active {
      transform:
        translateY(0);
    }

    .nxtgen-launcher-icon {
      display: inline-flex;
      align-items: center;
      justify-content: center;

      font-size: 16px;
      line-height: 1;
    }


    /*
     * ======================================================
     * Main Panel
     * ======================================================
     */

    .nxtgen-panel {
      position: absolute;

      right: 0;
      bottom: 62px;

      width: 380px;
      height: 560px;

      background: #ffffff;

      border:
        1px solid #e2e8f0;

      border-radius: 18px;

      overflow: hidden;

      box-shadow:
        0 20px 60px
        rgba(15, 23, 42, 0.18);

      display: none;
      flex-direction: column;
    }

    .nxtgen-panel.open {
      display: flex;
    }


    /*
     * ======================================================
     * Header
     * ======================================================
     */

    .nxtgen-header {
      padding:
        15px
        18px;

      background: #475569;
      color: #ffffff;

      display: flex;
      align-items: center;
      justify-content: space-between;

      gap: 12px;

      flex-shrink: 0;
    }

    .nxtgen-header-left {
      display: flex;
      align-items: center;

      gap: 10px;

      min-width: 0;
    }

    .nxtgen-header-icon {
      width: 32px;
      height: 32px;

      border-radius: 10px;

      background:
        rgba(
          255,
          255,
          255,
          0.12
        );

      display: flex;
      align-items: center;
      justify-content: center;

      flex-shrink: 0;

      font-size: 15px;
    }

    .nxtgen-header-text {
      min-width: 0;
    }

    .nxtgen-header-title {
      font-size: 15px;
      font-weight: 600;

      line-height: 1.25;

      min-width: 0;

      overflow-wrap: anywhere;
      word-break: break-word;
    }

    .nxtgen-header-status {
      margin-top: 2px;

      font-size: 11px;

      color: #e2e8f0;
    }

    .nxtgen-close {
      width: 32px;
      height: 32px;

      border: none;
      border-radius: 8px;

      background: transparent;
      color: #ffffff;

      cursor: pointer;

      font-size: 21px;
      line-height: 1;

      display: flex;
      align-items: center;
      justify-content: center;

      flex-shrink: 0;

      transition:
        background 0.2s ease;
    }

    .nxtgen-close:hover {
      background:
        rgba(
          255,
          255,
          255,
          0.12
        );
    }


    /*
     * ======================================================
     * Messages
     * ======================================================
     */

    .nxtgen-messages {
      flex: 1;

      min-width: 0;
      min-height: 0;

      overflow-y: auto;
      overflow-x: hidden;

      padding:
        18px
        16px;

      background: #f8fafc;

      scroll-behavior: smooth;
    }

    .nxtgen-message {
      max-width: 84%;
      min-width: 0;

      padding:
        10px
        12px;

      margin-bottom: 12px;

      border-radius: 14px;

      white-space: pre-wrap;

      overflow-wrap: anywhere;
      word-break: break-word;

      line-height: 1.5;

      font-size: 14px;
    }

    .nxtgen-message.user {
      margin-left: auto;

      background: #64748b;
      color: #ffffff;

      border-bottom-right-radius: 4px;

      box-shadow:
        0 2px 6px
        rgba(15, 23, 42, 0.08);
    }

    .nxtgen-message.assistant {
      margin-right: auto;

      background: #ffffff;
      color: #0f172a;

      border:
        1px solid #e2e8f0;

      border-bottom-left-radius: 4px;

      box-shadow:
        0 1px 3px
        rgba(15, 23, 42, 0.04);
    }

    .nxtgen-message.error {
      margin-right: auto;

      background: #fef2f2;
      color: #991b1b;

      border:
        1px solid #fecaca;

      border-bottom-left-radius: 4px;
    }


    /*
     * ======================================================
     * Sources
     * ======================================================
     */

    .nxtgen-sources {
      width: 100%;
      max-width: 100%;
      min-width: 0;

      margin-top: 10px;
      padding-top: 10px;

      border-top:
        1px solid #e2e8f0;

      font-size: 12px;
      line-height: 1.4;

      color: #64748b;

      overflow: hidden;
    }

    .nxtgen-sources-title {
      font-weight: 600;

      color: #475569;

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


    /*
     * ======================================================
     * Composer
     * ======================================================
     */

    .nxtgen-composer {
      flex-shrink: 0;

      background: #ffffff;

      border-top:
        1px solid #e2e8f0;
    }

    .nxtgen-input-row {
      display: flex;

      gap: 8px;

      padding:
        12px
        12px
        6px;

      background: #ffffff;

      align-items: flex-end;
    }

    .nxtgen-input {
      flex: 1;

      min-width: 0;

      resize: none;

      min-height: 42px;
      max-height: 100px;

      border:
        1px solid #cbd5e1;

      border-radius: 12px;

      padding:
        10px
        12px;

      font: inherit;
      font-size: 14px;

      line-height: 1.4;

      color: #0f172a;

      background: #ffffff;

      outline: none;

      transition:
        border-color 0.2s ease,
        box-shadow 0.2s ease;
    }

    .nxtgen-input::placeholder {
      color: #94a3b8;
    }

    .nxtgen-input:focus {
      border-color: #64748b;

      box-shadow:
        0 0 0 2px
        rgba(
          100,
          116,
          139,
          0.12
        );
    }

    .nxtgen-input:disabled {
      background: #f8fafc;

      cursor: not-allowed;
    }

    .nxtgen-send {
      min-width: 64px;
      height: 42px;

      border: none;
      border-radius: 10px;

      background: #475569;
      color: #ffffff;

      padding:
        0
        14px;

      cursor: pointer;

      font-weight: 600;
      font-size: 13px;

      flex-shrink: 0;

      transition:
        background 0.2s ease;
    }

    .nxtgen-send:hover:not(:disabled) {
      background: #334155;
    }

    .nxtgen-send:disabled {
      opacity: 0.45;

      cursor: default;
    }


    /*
     * ======================================================
     * Knowgentiq Product Footer
     * ======================================================
     */

    .nxtgen-powered-by {
      display: flex;

      align-items: center;
      justify-content: center;

      gap: 7px;

      min-height: 31px;

      padding:
        4px
        10px
        8px;

      background: #ffffff;

      color: #94a3b8;

      font-size: 9px;
      font-weight: 500;

      letter-spacing: 0.01em;

      white-space: nowrap;
    }

    .nxtgen-footer-brand {
      display: inline-flex;

      align-items: center;

      gap: 5px;

      color: #334155;

      font-size: 10px;
      font-weight: 700;

      letter-spacing: -0.01em;

      line-height: 1;
    }

    .nxtgen-footer-brand-mark {
      display: block;

      width: 19px;
      height: 19px;

      flex:
        0
        0
        19px;
    }

    .nxtgen-footer-divider {
      display: block;

      width: 1px;
      height: 14px;

      flex:
        0
        0
        1px;

      background: #e2e8f0;
    }

    .nxtgen-footer-product {
      display: inline-flex;

      align-items: baseline;

      gap: 3px;

      color: #94a3b8;

      font-size: 9px;
      font-weight: 500;
    }

    .nxtgen-footer-product strong {
      color: #64748b;

      font-weight: 600;
    }


    /*
     * ======================================================
     * Mobile
     * ======================================================
     */

    @media (max-width: 480px) {

      #nxtgen-chat-widget {
        right: 12px;
        bottom: 12px;
      }

      .nxtgen-launcher {
        min-width: 100px;
        height: 46px;

        padding:
          0
          15px;
      }

      .nxtgen-panel {
        position: fixed;

        left: 12px;
        right: 12px;

        top: 12px;
        bottom: 70px;

        width: auto;
        height: auto;
      }

      .nxtgen-powered-by {
        gap: 5px;

        padding-left: 6px;
        padding-right: 6px;

        font-size: 8px;
      }

      .nxtgen-footer-brand {
        gap: 4px;

        font-size: 9px;
      }

      .nxtgen-footer-brand-mark {
        width: 17px;
        height: 17px;

        flex-basis: 17px;
      }

      .nxtgen-footer-product {
        gap: 2px;

        font-size: 8px;
      }
    }


    @media (max-width: 360px) {

      .nxtgen-footer-brand {
        font-size: 8px;
      }

      .nxtgen-footer-product {
        font-size: 7px;
      }

      .nxtgen-footer-brand-mark {
        width: 15px;
        height: 15px;

        flex-basis: 15px;
      }
    }
  `;


  document.head.appendChild(
    style
  );


  /*
   * ========================================================
   * Widget HTML
   * ========================================================
   */

  root.innerHTML = `
    <div class="nxtgen-panel">

      <div class="nxtgen-header">

        <div class="nxtgen-header-left">

          <div class="nxtgen-header-icon">
            ✦
          </div>

          <div class="nxtgen-header-text">

            <div class="nxtgen-header-title">
              Assistant
            </div>

            <div class="nxtgen-header-status">
              AI-powered assistant
            </div>

          </div>

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


        <!--
          ====================================================
          Knowgentiq Product Branding

          Logo is INLINE SVG.

          No external image request.
          No data-logo-url required.
          No dependency on client website assets.
          ====================================================
        -->

        <div
          class="nxtgen-powered-by"
          aria-label="Knowgentiq, a product of NXTGEN Innovate Technologies"
        >

          <span class="nxtgen-footer-brand">

            <svg
              class="nxtgen-footer-brand-mark"
              viewBox="0 0 48 48"
              role="img"
              aria-label="Knowgentiq"
            >

              <defs>

                <linearGradient
                  id="nxtgen-footer-logo-gradient"
                  x1="5"
                  y1="5"
                  x2="43"
                  y2="43"
                  gradientUnits="userSpaceOnUse"
                >

                  <stop
                    offset="0"
                    stop-color="#22d3ee"
                  />

                  <stop
                    offset="0.52"
                    stop-color="#3b82f6"
                  />

                  <stop
                    offset="1"
                    stop-color="#7c3aed"
                  />

                </linearGradient>

              </defs>


              <rect
                x="3"
                y="3"
                width="42"
                height="42"
                rx="12"
                fill="url(#nxtgen-footer-logo-gradient)"
              />


              <path
                d="
                  M16 12
                  v24

                  M17 25
                  l14-13

                  M19 23
                  l13 13
                "
                fill="none"
                stroke="#ffffff"
                stroke-width="5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />

            </svg>


            <span>
              Knowgentiq
            </span>

          </span>


          <span
            class="nxtgen-footer-divider"
            aria-hidden="true"
          ></span>


          <span class="nxtgen-footer-product">

            <span>
              A Product Of
            </span>

            <strong>
              NXTGEN Innovate Technologies
            </strong>

          </span>

        </div>

      </div>

    </div>


    <!--
      Launcher intentionally unchanged.
    -->

    <button
      type="button"
      class="nxtgen-launcher"
      aria-label="Ask AI"
    >

      <span class="nxtgen-launcher-icon">
        ✦
      </span>

      <span>
        Ask AI
      </span>

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


  /*
   * Persist rendered conversation for
   * the current browser tab.
   */
  function persistMessages() {
    try {

      sessionStorage.setItem(
        messagesKey,
        messagesElement.innerHTML
      );

    } catch {

      /*
       * Chat should continue normally
       * even if browser storage is blocked.
       */

    }
  }


  function restoreMessages() {
    try {

      const stored =
        sessionStorage.getItem(
          messagesKey
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

    persistMessages();

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


    /*
     * Prevent duplicated source blocks
     * if metadata is emitted more than once.
     */

    const existingSources =
      messageElement.querySelector(
        ".nxtgen-sources"
      );

    if (existingSources) {
      existingSources.remove();
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

    persistMessages();

    scrollToBottom();
  }


  function clearMessages() {
    messagesElement.innerHTML =
      "";
  }


  /*
   * ========================================================
   * Load Widget Configuration
   * ========================================================
   */

  async function loadConfig() {

    const response =
      await fetch(
        `${apiBase}/public/v1/widget/config/${channelId}`,
        {
          method:
            "GET",
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


    /*
     * Restore an existing tab conversation
     * before showing the welcome message.
     */

    const restored =
      restoreMessages();


    if (
      !restored &&
      widgetConfig.welcome_message
    ) {

      clearMessages();


      addMessage(
        "assistant",
        widgetConfig.welcome_message
      );

    }
  }


  /*
   * ========================================================
   * Visitor Token
   * ========================================================
   */

  function tokenIsValid() {

    return (
      visitorToken &&
      Date.now()
        <
      tokenExpiresAt - 30000
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
      +
      (
        data.expires_in
        * 1000
      );


    return visitorToken;
  }


  /*
   * ========================================================
   * SSE Parser
   * ========================================================
   */

  function parseEventBlock(
    block
  ) {

    let eventType =
      "message";


    const dataLines =
      [];


    for (
      const line
      of block.split(
        "\n"
      )
    ) {

      if (
        line.startsWith(
          "event:"
        )
      ) {

        let value =
          line.slice(
            6
          );


        if (
          value.startsWith(
            " "
          )
        ) {

          value =
            value.slice(
              1
            );

        }


        eventType =
          value.trim();


        continue;
      }


      if (
        line.startsWith(
          "data:"
        )
      ) {

        let value =
          line.slice(
            5
          );


        /*
         * SSE permits one optional protocol
         * space after the colon.
         *
         * Remove only that space because
         * additional whitespace may belong
         * to an LLM token.
         */

        if (
          value.startsWith(
            " "
          )
        ) {

          value =
            value.slice(
              1
            );

        }


        dataLines.push(
          value
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


  /*
   * ========================================================
   * Send Message
   * ========================================================
   */

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


    isSending =
      true;


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


      /*
       * Continue the same backend
       * conversation within this tab.
       */

      if (sessionId) {

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
            buffer.slice(
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


          /*
           * LLM text token.
           */

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

            continue;
          }


          /*
           * Conversation metadata and
           * citations.
           */

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

              /*
               * Ignore malformed metadata.
               * The answer can still render.
               */

            }


            continue;
          }


          /*
           * Backend application errors can
           * be delivered inside the SSE
           * stream while HTTP remains 200.
           */

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


        persistMessages();

      }

    } catch (error) {

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


  /*
   * ========================================================
   * Initialization
   * ========================================================
   */

  async function initialize() {

    if (widgetConfig) {
      return true;
    }


    if (isInitializing) {
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

    if (widgetConfig) {
      return true;
    }


    const initialized =
      await initialize();


    if (initialized) {
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


  /*
   * ========================================================
   * Event Handlers
   * ========================================================
   */

  launcher.addEventListener(
    "click",
    async function () {

      isOpen =
        !isOpen;


      panel.classList.toggle(
        "open",
        isOpen
      );


      if (!isOpen) {
        return;
      }


      const ready =
        await ensureInitialized();


      if (ready) {

        scrollToBottom();

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
        === "Enter" &&
        !event.shiftKey
      ) {

        event.preventDefault();

        sendMessage();

      }
    }
  );


  /*
   * Silent warm-up.
   *
   * If the API is temporarily unavailable,
   * opening the widget will retry.
   */

  initialize().catch(
    function () {

      // Intentionally silent.

    }
  );

})();