import Link from "next/link";

import { Card } from "@/components/ui/Card";

export default function DashboardPage() {
  return (
    <section className="mx-auto max-w-5xl px-6 py-12">
      <Card>
        <h1 className="text-2xl font-semibold text-slate-900">Admin dashboard</h1>
        <p className="mt-3 text-sm text-slate-600">
          Day la khu quan tri phase 1. Tu day, admin co the di sang man hinh sua profile de cap nhat giao dien public.
        </p>
        <Link href="/edit-profile" className="mt-5 inline-block rounded-xl bg-slate-900 px-4 py-2 text-sm text-white">
          Di den edit profile
        </Link>
      </Card>
    </section>
  );
}
