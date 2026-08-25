import { useEffect, useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import { fetchMetrics, type MetricsResponse } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const SLICE_LABELS: Record<string, string> = {
  con_jerga: "Con jerga",
  sin_jerga: "Sin jerga",
  sarcasmo_si: "Con sarcasmo",
  sarcasmo_no: "Sin sarcasmo",
};

export function MetricsPanel() {
  const [open, setOpen] = useState(false);
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMetrics()
      .then(setMetrics)
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <div>
          <CardTitle>Contexto del modelo</CardTitle>
          <CardDescription>Métricas globales de referencia (no recalculadas por prompt)</CardDescription>
        </div>
        <Button variant="ghost" size="sm" onClick={() => setOpen((v) => !v)}>
          {open ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </Button>
      </CardHeader>
      {open && (
        <CardContent className="space-y-4">
          {error && <p className="text-sm text-red-400">{error}</p>}
          {metrics && (
            <>
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary">Modelo: {metrics.model}</Badge>
                <Badge variant="success">
                  F1-macro oficial: {(metrics.f1_macro_official * 100).toFixed(1)}%
                </Badge>
                <Badge variant="outline">Test n={metrics.test_n}</Badge>
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                {metrics.slices.map((slice) => (
                  <div
                    key={slice.slice}
                    className="rounded-md border border-[var(--color-border)] p-3 text-sm"
                  >
                    <p className="font-medium">{SLICE_LABELS[slice.slice] ?? slice.slice}</p>
                    <p className="text-[var(--color-muted-foreground)]">
                      F1: {(slice.f1_macro * 100).toFixed(1)}% · Acc: {(slice.accuracy * 100).toFixed(1)}%
                    </p>
                    <p className="text-xs text-[var(--color-muted-foreground)]">n={slice.n}</p>
                  </div>
                ))}
              </div>
            </>
          )}
        </CardContent>
      )}
    </Card>
  );
}
