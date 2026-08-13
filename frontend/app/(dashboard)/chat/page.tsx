import ChatWindow from "@/features/chat/components/ChatWindow";


export default function ChatPage() {
  return (
    <div className="space-y-6">

      <div>
        <p className="text-sm font-medium text-slate-500">
          Knowledge Assistant
        </p>

        <h1 className="mt-1 text-3xl font-bold text-slate-900">
          Chat
        </h1>

        <p className="mt-2 text-slate-500">
          Ask questions and receive
          answers grounded in your
          knowledge bases.
        </p>
      </div>


      <ChatWindow />

    </div>
  );
}