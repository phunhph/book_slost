import Link from "next/link";

import { Card } from "@/components/ui/Card";

export default function HomePage() {
  return (
    <section className="mx-auto max-w-6xl px-6 py-12">
      <div className="max-w-3xl">
        <p className="text-sm font-medium uppercase tracking-wide text-slate-500">Admin Project</p>
        <h1 className="mt-4 text-4xl font-bold text-slate-900">Affiliate Booking Admin UI</h1>
        <p className="mt-4 text-lg text-slate-600">
          Day la project admin doc lap de dang ky creator, quan ly dashboard va cap nhat public profile.
        </p>
      </div>

      <div className="mt-10 grid gap-6 md:grid-cols-3">
        <Card>
          <h2 className="text-xl font-semibold text-slate-900">Register</h2>
          <p className="mt-3 text-sm text-slate-600">Tao user moi qua backend va bat dau flow quan tri.</p>
          <Link href="/register" className="mt-5 inline-block text-sm font-medium text-slate-900">Mo trang dang ky</Link>
        </Card>

        <Card>
          <h2 className="text-xl font-semibold text-slate-900">Dashboard</h2>
          <p className="mt-3 text-sm text-slate-600">Diem vao nhanh cho khu quan ly profile.</p>
          <Link href="/dashboard" className="mt-5 inline-block text-sm font-medium text-slate-900">Mo dashboard</Link>
        </Card>

        <Card>
          <h2 className="text-xl font-semibold text-slate-900">Edit Profile</h2>
          <p className="mt-3 text-sm text-slate-600">Cap nhat username, bio, mau sac va layout block.</p>
          <Link href="/edit-profile" className="mt-5 inline-block text-sm font-medium text-slate-900">Mo profile editor</Link>
        </Card>
      </div>
    </section>
  );
}
