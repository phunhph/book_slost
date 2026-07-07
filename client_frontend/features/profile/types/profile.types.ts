export type LayoutBlockId =
  | "media_block"
  | "booking_block"
  | "products_block"
  | "affiliate_block";

export interface LayoutBlock {
  id: LayoutBlockId;
  active: boolean;
}

export interface UserProfile {
  user_id: string;
  username: string | null;
  display_name: string | null;
  bio: string | null;
  avatar_url: string | null;
  theme_mode: "light" | "dark" | "custom";
  font_family: string;
  primary_color: string;
  text_color: string;
  bg_type: "color" | "gradient" | "image";
  bg_value: string | null;
  avatar_style: "circle" | "square" | "rounded";
  button_style: "filled" | "outline" | "shadow";
  layout_structure: LayoutBlock[];
  created_at: string;
  updated_at: string;
}
