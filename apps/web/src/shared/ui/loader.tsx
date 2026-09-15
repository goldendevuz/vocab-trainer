import { cn } from "@/shared/lib/utils";

export function Loader({
  label = "Just a moment",
  className,
}: {
  label?: string;
  className?: string;
}) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={cn("flex items-center gap-2 text-sm text-muted-foreground", className)}
    >
      <span
        aria-hidden
        className="size-4 shrink-0 animate-spin rounded-full border-2 border-primary/20 border-t-primary"
      />
      <span>
        {label}
        <span aria-hidden className="inline-flex">
          <span>.</span>
          <span className="dot-fill-2">.</span>
          <span className="dot-fill-3">.</span>
        </span>
      </span>
    </div>
  );
}
