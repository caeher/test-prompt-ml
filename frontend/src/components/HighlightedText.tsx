import type { TokenWeight } from "@/lib/api";
import { cn } from "@/lib/utils";

interface HighlightedTextProps {
  text: string;
  weights: TokenWeight[];
}

function buildWeightMap(weights: TokenWeight[]): Map<string, number> {
  const map = new Map<string, number>();
  for (const { token, weight } of weights) {
    const key = token.toLowerCase();
    const prev = map.get(key) ?? 0;
    if (Math.abs(weight) >= Math.abs(prev)) {
      map.set(key, weight);
    }
  }
  return map;
}

function tokenStyle(weight: number | undefined): string {
  if (weight === undefined) return "";
  if (weight > 0.05) return "bg-orange-500/30 text-orange-200 ring-1 ring-orange-500/40";
  if (weight > 0) return "bg-orange-500/15 text-orange-100";
  if (weight < -0.05) return "bg-slate-500/25 text-slate-300 ring-1 ring-slate-500/30";
  if (weight < 0) return "bg-slate-500/10 text-slate-400";
  return "";
}

export function HighlightedText({ text, weights }: HighlightedTextProps) {
  const weightMap = buildWeightMap(weights);
  const tokens = text.split(/(\s+)/);

  return (
    <p className="leading-relaxed text-sm">
      {tokens.map((token, index) => {
        const clean = token.trim().toLowerCase();
        const weight = clean ? weightMap.get(clean) : undefined;
        const style = tokenStyle(weight);
        return (
          <span
            key={`${index}-${token}`}
            className={cn("rounded px-0.5", style)}
            title={weight !== undefined ? `peso LIME: ${weight.toFixed(3)}` : undefined}
          >
            {token}
          </span>
        );
      })}
    </p>
  );
}
