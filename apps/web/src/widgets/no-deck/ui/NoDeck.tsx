import { Link } from "react-router-dom";
import { useI18n } from "@/shared/lib/i18n";
import { Button } from "@/shared/ui/button";

export function NoDeck() {
  const { t } = useI18n();
  return (
    <div className="flex flex-col items-center gap-4 rounded-3xl border border-dashed border-border bg-card/60 p-10 text-center shadow-sm shadow-foreground/[0.02]">
      <div className="flex size-14 items-center justify-center rounded-2xl bg-tint-lavender text-2xl">
        📚
      </div>
      <p className="text-2xl font-black tracking-tight text-foreground">{t("noDeck.title")}</p>
      <p className="max-w-sm text-muted-foreground">{t("noDeck.hint")}</p>
      <Link to="/import">
        <Button className="rounded-full px-6" size="lg">
          {t("noDeck.import")}
        </Button>
      </Link>
    </div>
  );
}
