import { notFound } from "next/navigation";

import { PublicProfileView } from "@/features/profile/components/PublicProfileView";
import { getPublicProfile } from "@/features/profile/services/profileApi";

export default async function PublicProfilePage({
  params
}: {
  params: { username: string };
}) {
  const { username } = params;

  try {
    const profile = await getPublicProfile(username);
    return <PublicProfileView profile={profile} />;
  } catch {
    notFound();
  }
}
