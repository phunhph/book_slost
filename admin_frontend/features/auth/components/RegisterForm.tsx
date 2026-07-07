"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { registerLocal } from "@/features/auth/services/authApi";

export function RegisterForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");
    setIsSubmitting(true);

    try {
      const result = await registerLocal({
        email,
        password,
        username: username || undefined,
        display_name: displayName || undefined
      });

      localStorage.setItem("abc_user_id", result.user.id);
      localStorage.setItem("abc_user_email", result.user.email);
      if (username) {
        localStorage.setItem("abc_username", username);
      }

      setSuccess("Register thanh cong. Ban se duoc chuyen den trang admin edit profile.");
      router.push("/edit-profile");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Dang ky that bai.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Card className="mx-auto max-w-xl">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-900">Tao tai khoan admin</h1>
        <p className="mt-2 text-sm text-slate-600">Form nay da noi truc tiep vao backend POST /api/auth/register-local.</p>
      </div>

      <form className="space-y-4" onSubmit={handleSubmit}>
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">Email</label>
          <Input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">Password</label>
          <Input type="password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={8} required />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">Username</label>
          <Input value={username} onChange={(event) => setUsername(event.target.value)} placeholder="idol-demo" />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">Display name</label>
          <Input value={displayName} onChange={(event) => setDisplayName(event.target.value)} placeholder="Demo Creator" />
        </div>

        {error ? <p className="text-sm text-rose-600">{error}</p> : null}
        {success ? <p className="text-sm text-emerald-600">{success}</p> : null}

        <Button type="submit" disabled={isSubmitting} className="w-full">
          {isSubmitting ? "Dang tao..." : "Dang ky"}
        </Button>
      </form>
    </Card>
  );
}
