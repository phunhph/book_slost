import { Card } from "@/components/ui/Card";

export default function HomePage() {
  return (
    <section className="mx-auto max-w-6xl px-6 py-12">
      <div className="max-w-3xl">
        <p className="text-sm font-medium uppercase tracking-wide text-slate-500">Client Project</p>
        <h1 className="mt-4 text-4xl font-bold text-slate-900">Affiliate Booking Client UI</h1>
        <p className="mt-4 text-lg text-slate-600">
          Day la project client doc lap, chi tap trung vao public-facing profile duoc render tu backend.
        </p>
      </div>

      <div className="mt-10">
        <Card>
          <h2 className="text-xl font-semibold text-slate-900">Public route</h2>
          <p className="mt-3 text-sm text-slate-600">Sau khi admin dat username, mo route /[username] de xem profile cong khai.</p>
        </Card>
      </div>
    </section>
  );
}
