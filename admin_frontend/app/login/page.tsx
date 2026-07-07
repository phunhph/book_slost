import { Card } from "@/components/ui/Card";

export default function LoginPage() {
  return (
    <section className="mx-auto max-w-4xl px-6 py-12">
      <Card className="mx-auto max-w-xl">
        <h1 className="text-2xl font-semibold text-slate-900">Admin login</h1>
        <p className="mt-3 text-sm text-slate-600">
          Backend hien tai chua co JWT auth that. Trang nay dang duoc giu san de bo sung login o phase tiep theo.
        </p>
      </Card>
    </section>
  );
}
