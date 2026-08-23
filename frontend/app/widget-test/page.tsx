import Script from "next/script";


export default function WidgetTestPage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        padding: "48px",
      }}
    >
      <h1>
        NXTGEN Widget Test
      </h1>

      <p>
        The website chatbot should appear
        in the bottom-right corner.
      </p>

      <Script
        src="/nxtgen-widget.js"
        strategy="afterInteractive"
        data-channel-id="8644d901-86f2-440c-8a9d-b314669542ba"
        data-api-base="http://localhost:8000"
      />
    </main>
  );
}