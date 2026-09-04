import { Boxes } from "lucide-react";

export function PlaceholderPage() {
  return (
    <div className="empty-page">
      <Boxes size={34} />
      <p className="eyebrow">COMING NEXT</p>
      <h1>Operations workspace</h1>
      <p>
        This route is scaffolded and ready for the next implementation phase.
      </p>
    </div>
  );
}
