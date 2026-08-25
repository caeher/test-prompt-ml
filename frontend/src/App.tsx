"use client";

import { useCallback, useEffect, useState } from "react";
import { AlertCircle, Loader2, Sparkles } from "lucide-react";
import {
  explainText,
  fetchHealth,
  LABEL_COLORS,
  predictText,
  type ExplainResponse,
  type HealthResponse,
  type PredictResponse,
} from "@/lib/api";
import { HighlightedText } from "@/components/HighlightedText";
import { MetricsPanel } from "@/components/MetricsPanel";
import { ProbabilityChart } from "@/components/ProbabilityChart";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Textarea } from "@/components/ui/textarea";

const EXAMPLE_TEXT = "Ese maje no sabe lo que está haciendo";

function labelBadgeVariant(index: number): "success" | "warning" | "danger" | "secondary" {
  if (index === 0) return "success";
  if (index === 1) return "warning";
  if (index === 2) return "danger";
  return "danger";
}

export default function App() {
  const [text, setText] = useState(EXAMPLE_TEXT);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [explanation, setExplanation] = useState<ExplainResponse | null>(null);
  const [loadingPredict, setLoadingPredict] = useState(false);
  const [loadingExplain, setLoadingExplain] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshHealth = useCallback(() => {
    fetchHealth()
      .then(setHealth)
      .catch((err: Error) => {
        setHealth({
          status: "unavailable",
          model_loaded: false,
          backend: "mbert",
          error: err.message,
        });
      });
  }, []);

  useEffect(() => {
    refreshHealth();
  }, [refreshHealth]);

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setLoadingPredict(true);
    setError(null);
    setExplanation(null);
    try {
      const prediction = await predictText(text.trim());
      setResult(prediction);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al analizar");
      setResult(null);
    } finally {
      setLoadingPredict(false);
    }
  };

  const handleExplain = async () => {
    if (!text.trim() || !result) return;
    setLoadingExplain(true);
    setError(null);
    try {
      const exp = await explainText(text.trim());
      setExplanation(exp);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al explicar");
    } finally {
      setLoadingExplain(false);
    }
  };

  return (
    <div className="mx-auto min-h-screen max-w-6xl px-4 py-8">
      <header className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Análisis de toxicidad</h1>
          <p className="text-sm text-[var(--color-muted-foreground)]">
            Clasificador multiclase en español salvadoreño · normalize_for_model v1.1
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="secondary">mBERT</Badge>
          {health?.model_loaded ? (
            <Badge variant="success">Modelo listo · {health.device}</Badge>
          ) : (
            <Badge variant="danger">Modelo no disponible</Badge>
          )}
        </div>
      </header>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Texto a analizar</CardTitle>
          <CardDescription>Escribe o pega un mensaje de red social</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Escribe aquí el texto..."
            maxLength={2000}
          />
          <div className="flex flex-wrap gap-3">
            <Button onClick={handleAnalyze} disabled={loadingPredict || !text.trim()}>
              {loadingPredict ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              Analizar
            </Button>
            <Button
              variant="outline"
              onClick={handleExplain}
              disabled={loadingExplain || !result || !text.trim()}
            >
              {loadingExplain ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
              Explicar (LIME)
            </Button>
          </div>
          {error && (
            <div className="flex items-start gap-2 rounded-md border border-red-900/50 bg-red-950/30 p-3 text-sm text-red-300">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}
          {!health?.model_loaded && health?.error && (
            <p className="text-sm text-[var(--color-muted-foreground)]">
              El backend está preparando el modelo. Comprueba la conexión con Hugging Face si el
              problema persiste.
            </p>
          )}
        </CardContent>
      </Card>

      {result && (
        <div className="mb-6 grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Resultado</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant={labelBadgeVariant(result.label_index)}>{result.label}</Badge>
                <span className="text-sm text-[var(--color-muted-foreground)]">
                  Confianza: {(result.confidence * 100).toFixed(1)}%
                </span>
              </div>
              <Progress
                value={result.confidence * 100}
                indicatorClassName="bg-[var(--color-primary)]"
              />
              <div>
                <p className="mb-1 text-xs font-medium uppercase tracking-wide text-[var(--color-muted-foreground)]">
                  Texto normalizado
                </p>
                <p className="rounded-md bg-[var(--color-secondary)] p-3 text-sm">{result.text_normalized}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <Badge variant="outline">{result.features.n_palabras} palabras</Badge>
                {result.features.has_url && <Badge variant="warning">URL</Badge>}
                {result.features.has_mention && <Badge variant="warning">Mención</Badge>}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Probabilidades por clase</CardTitle>
            </CardHeader>
            <CardContent>
              <ProbabilityChart
                probabilities={result.probabilities}
                predictedIndex={result.label_index}
              />
              <div className="mt-2 flex flex-wrap gap-2 text-xs">
                {Object.entries(result.probabilities).map(([key, value], index) => (
                  <span key={key} style={{ color: LABEL_COLORS[index] }}>
                    {key}: {(value * 100).toFixed(1)}%
                  </span>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {explanation && explanation.weights.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Explicación LIME</CardTitle>
            <CardDescription>
              Tokens que empujan hacia <strong>{explanation.predicted_label}</strong> (naranja) o en
              contra (gris)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <HighlightedText text={explanation.text} weights={explanation.weights} />
          </CardContent>
        </Card>
      )}

      <MetricsPanel />
    </div>
  );
}
