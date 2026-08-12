type Props = {
  params: Promise<{
    id: string;
  }>;
};

export default async function KnowledgeBaseDetailPage({
  params,
}: Props) {
  const { id } = await params;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">
          Knowledge Base
        </h1>

        <p className="mt-1 text-slate-500">
          {id}
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-xl border bg-white p-6">
          <h2 className="text-lg font-semibold">
            Knowledge Sources
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            Manage sources for this knowledge base.
          </p>
        </div>

        <div className="rounded-xl border bg-white p-6">
          <h2 className="text-lg font-semibold">
            Documents
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            View and upload documents.
          </p>
        </div>

        <div className="rounded-xl border bg-white p-6">
          <h2 className="text-lg font-semibold">
            Chat
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            Ask questions against this knowledge base.
          </p>
        </div>
      </div>
    </div>
  );
}