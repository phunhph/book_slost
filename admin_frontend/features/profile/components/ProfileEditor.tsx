"use client";

import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { getProfileByUserId, updateProfile } from "@/features/profile/services/profileApi";
import { LayoutBlock, LayoutBlockId, UserProfile, UserProfileUpdatePayload } from "@/features/profile/types/profile.types";

const DEFAULT_BLOCKS: LayoutBlock[] = [
  { id: "media_block", active: true },
  { id: "booking_block", active: true },
  { id: "products_block", active: true },
  { id: "affiliate_block", active: true }
];

export function ProfileEditor() {
  const [userId, setUserId] = useState("");
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [displayName, setDisplayName] = useState("");
  const [username, setUsername] = useState("");
  const [bio, setBio] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [fontFamily, setFontFamily] = useState("Inter");
  const [primaryColor, setPrimaryColor] = useState("#FF007F");
  const [textColor, setTextColor] = useState("#111111");
  const [bgType, setBgType] = useState<"color" | "gradient" | "image">("color");
  const [bgValue, setBgValue] = useState("#FFFFFF");
  const [avatarStyle, setAvatarStyle] = useState<"circle" | "square" | "rounded">("circle");
  const [buttonStyle, setButtonStyle] = useState<"filled" | "outline" | "shadow">("filled");
  const [layoutBlocks, setLayoutBlocks] = useState<LayoutBlock[]>(DEFAULT_BLOCKS);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const savedUserId = window.localStorage.getItem("abc_user_id");
    if (!savedUserId) {
      setError("Chua co user_id trong trinh duyet. Hay dang ky truoc.");
      setIsLoading(false);
      return;
    }

    setUserId(savedUserId);

    getProfileByUserId(savedUserId)
      .then((data) => {
        setProfile(data);
        setDisplayName(data.display_name ?? "");
        setUsername(data.username ?? "");
        setBio(data.bio ?? "");
        setAvatarUrl(data.avatar_url ?? "");
        setFontFamily(data.font_family);
        setPrimaryColor(data.primary_color);
        setTextColor(data.text_color);
        setBgType(data.bg_type);
        setBgValue(data.bg_value ?? "#FFFFFF");
        setAvatarStyle(data.avatar_style);
        setButtonStyle(data.button_style);
        setLayoutBlocks(data.layout_structure);
      })
      .catch((loadError) => {
        setError(loadError instanceof Error ? loadError.message : "Khong the tai profile.");
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const previewUrl = useMemo(() => {
    if (!username) return "";
    const clientOrigin = process.env.NEXT_PUBLIC_CLIENT_APP_URL ?? "http://localhost:3001";
    return `${clientOrigin}/${username}`;
  }, [username]);

  function toggleBlock(id: LayoutBlockId) {
    setLayoutBlocks((current) => current.map((block) => (block.id === id ? { ...block, active: !block.active } : block)));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!userId) return;

    setStatus("");
    setError("");
    setIsSaving(true);

    const payload: UserProfileUpdatePayload = {
      username: username || undefined,
      display_name: displayName || undefined,
      bio: bio || undefined,
      avatar_url: avatarUrl || undefined,
      font_family: fontFamily,
      primary_color: primaryColor,
      text_color: textColor,
      bg_type: bgType,
      bg_value: bgValue,
      avatar_style: avatarStyle,
      button_style: buttonStyle,
      layout_structure: layoutBlocks
    };

    try {
      const updated = await updateProfile(userId, payload);
      setProfile(updated);
      setStatus("Cap nhat profile thanh cong.");
      if (updated.username) {
        localStorage.setItem("abc_username", updated.username);
      }
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Khong the cap nhat profile.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
      <Card>
        <div className="mb-6">
          <h1 className="text-2xl font-semibold text-slate-900">Edit profile</h1>
          <p className="mt-2 text-sm text-slate-600">Man hinh nay dang noi truc tiep vao GET/PUT /api/profiles/by-user/user_id.</p>
        </div>

        {isLoading ? (
          <p className="text-sm text-slate-500">Dang tai profile...</p>
        ) : (
          <form className="space-y-5" onSubmit={handleSubmit}>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Display name</label>
                <Input value={displayName} onChange={(event) => setDisplayName(event.target.value)} />
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Username</label>
                <Input value={username} onChange={(event) => setUsername(event.target.value)} />
              </div>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Bio</label>
              <textarea className="min-h-28 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm text-slate-900 outline-none focus:border-slate-500" value={bio} onChange={(event) => setBio(event.target.value)} />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Avatar URL</label>
              <Input value={avatarUrl} onChange={(event) => setAvatarUrl(event.target.value)} />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Font family</label>
                <Input value={fontFamily} onChange={(event) => setFontFamily(event.target.value)} />
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Background type</label>
                <select className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm" value={bgType} onChange={(event) => setBgType(event.target.value as "color" | "gradient" | "image")}>
                  <option value="color">color</option>
                  <option value="gradient">gradient</option>
                  <option value="image">image</option>
                </select>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Primary color</label>
                <Input value={primaryColor} onChange={(event) => setPrimaryColor(event.target.value)} />
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Text color</label>
                <Input value={textColor} onChange={(event) => setTextColor(event.target.value)} />
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Background value</label>
                <Input value={bgValue} onChange={(event) => setBgValue(event.target.value)} />
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Avatar style</label>
                <select className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm" value={avatarStyle} onChange={(event) => setAvatarStyle(event.target.value as "circle" | "square" | "rounded")}>
                  <option value="circle">circle</option>
                  <option value="square">square</option>
                  <option value="rounded">rounded</option>
                </select>
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Button style</label>
                <select className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm" value={buttonStyle} onChange={(event) => setButtonStyle(event.target.value as "filled" | "outline" | "shadow")}>
                  <option value="filled">filled</option>
                  <option value="outline">outline</option>
                  <option value="shadow">shadow</option>
                </select>
              </div>
            </div>

            <div>
              <p className="mb-3 text-sm font-medium text-slate-700">Layout blocks</p>
              <div className="grid gap-3 md:grid-cols-2">
                {layoutBlocks.map((block) => (
                  <label key={block.id} className="flex items-center justify-between rounded-xl border border-slate-200 px-4 py-3 text-sm">
                    <span>{block.id}</span>
                    <input type="checkbox" checked={block.active} onChange={() => toggleBlock(block.id)} />
                  </label>
                ))}
              </div>
            </div>

            {error ? <p className="text-sm text-rose-600">{error}</p> : null}
            {status ? <p className="text-sm text-emerald-600">{status}</p> : null}

            <div className="flex flex-wrap gap-3">
              <Button type="submit" disabled={isSaving}>
                {isSaving ? "Dang luu..." : "Luu profile"}
              </Button>
              {previewUrl ? (
                <a href={previewUrl} target="_blank" rel="noreferrer" className="inline-flex items-center rounded-xl border border-slate-300 px-4 py-2 text-sm">
                  Xem public profile
                </a>
              ) : null}
            </div>
          </form>
        )}
      </Card>

      <Card>
        <h2 className="text-lg font-semibold text-slate-900">Quick info</h2>
        <div className="mt-4 space-y-2 text-sm text-slate-600">
          <p><strong>User ID:</strong> {userId || "Chua co"}</p>
          <p><strong>Username:</strong> {profile?.username ?? username ?? "Chua dat"}</p>
          <p><strong>Public URL:</strong> {username ? previewUrl : "Can username"}</p>
        </div>
      </Card>
    </div>
  );
}
