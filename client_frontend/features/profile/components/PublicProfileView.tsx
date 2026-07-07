import { Card } from "@/components/ui/Card";
import { UserProfile } from "@/features/profile/types/profile.types";

function renderBlockLabel(id: string) {
  switch (id) {
    case "media_block":
      return "Media Block";
    case "booking_block":
      return "Booking Block";
    case "products_block":
      return "Products Block";
    case "affiliate_block":
      return "Affiliate Block";
    default:
      return id;
  }
}

function buildBackground(profile: UserProfile) {
  if (profile.bg_type === "image" && profile.bg_value) {
    return { backgroundImage: `url(${profile.bg_value})`, backgroundSize: "cover", backgroundPosition: "center" };
  }

  if (profile.bg_type === "gradient" && profile.bg_value) {
    return { background: profile.bg_value };
  }

  return { background: profile.bg_value ?? "#FFFFFF" };
}

export function PublicProfileView({ profile }: { profile: UserProfile }) {
  const avatarClassName =
    profile.avatar_style === "circle"
      ? "rounded-full"
      : profile.avatar_style === "rounded"
        ? "rounded-2xl"
        : "rounded-none";

  const buttonClassName =
    profile.button_style === "outline"
      ? "border-2 bg-transparent"
      : profile.button_style === "shadow"
        ? "shadow-lg"
        : "";

  return (
    <section className="min-h-[calc(100vh-72px)] px-6 py-10" style={buildBackground(profile)}>
      <div className="mx-auto max-w-3xl" style={{ color: profile.text_color, fontFamily: profile.font_family }}>
        <Card className="border-transparent bg-white/90 backdrop-blur">
          <div className="flex flex-col items-center text-center">
            <div className={`h-28 w-28 overflow-hidden bg-slate-200 ${avatarClassName}`}>
              {profile.avatar_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={profile.avatar_url} alt={profile.display_name ?? "Avatar"} className="h-full w-full object-cover" />
              ) : null}
            </div>
            <h1 className="mt-4 text-3xl font-semibold">{profile.display_name ?? profile.username ?? "Unnamed Creator"}</h1>
            <p className="mt-2 text-sm opacity-80">{profile.bio ?? "Chua co mo ta."}</p>
            <button className={`mt-6 rounded-xl px-5 py-2 text-sm font-medium text-white ${buttonClassName}`.trim()} style={{ backgroundColor: profile.primary_color, borderColor: profile.primary_color }}>
              Contact / Book
            </button>
          </div>
        </Card>

        <div className="mt-6 grid gap-4">
          {profile.layout_structure.filter((block) => block.active).map((block) => (
            <Card key={block.id}>
              <h2 className="text-lg font-semibold text-slate-900">{renderBlockLabel(block.id)}</h2>
              <p className="mt-2 text-sm text-slate-600">Day la placeholder UI cho block `{block.id}`. Client UI dang render dong theo `layout_structure`.</p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
