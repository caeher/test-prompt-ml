export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  model_dir?: string;
  backend: string;
  device?: string;
  contract?: {
    max_length: number;
    normalizer: string;
    normalizer_version: string;
  };
  error?: string;
}

export interface ProbabilityMap {
  no_toxico: number;
  ofensivo: number;
  odio: number;
  amenazas: number;
}

export interface TextFeatures {
  n_palabras: number;
  has_url: boolean;
  has_mention: boolean;
}

export interface PredictResponse {
  text_original: string;
  text_normalized: string;
  label: string;
  label_index: number;
  confidence: number;
  probabilities: ProbabilityMap;
  features: TextFeatures;
}

export interface TokenWeight {
  token: string;
  weight: number;
}

export interface ExplainResponse {
  text: string;
  predicted_class: number;
  predicted_label: string;
  weights: TokenWeight[];
}

export interface SliceMetric {
  slice: string;
  f1_macro: number;
  accuracy: number;
  n: number;
  definition: string;
}

export interface MetricsResponse {
  model: string;
  f1_macro_official: number;
  test_n: number;
  slices: SliceMetric[];
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({ detail: response.statusText }));
    const message =
      typeof detail.detail === "string"
        ? detail.detail
        : detail.detail?.error ?? JSON.stringify(detail.detail ?? detail);
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch("/health");
  if (response.status === 503) {
    const detail = await response.json().catch(() => ({}));
    const body = detail.detail ?? detail;
    return {
      status: "unavailable",
      model_loaded: false,
      backend: body.backend ?? "mbert",
      error: body.error ?? body.hint ?? "Modelo no disponible",
    };
  }
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  return response.json() as Promise<HealthResponse>;
}

export function predictText(text: string): Promise<PredictResponse> {
  return request<PredictResponse>("/api/predict", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export function explainText(text: string): Promise<ExplainResponse> {
  return request<ExplainResponse>("/api/explain", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export function fetchMetrics(): Promise<MetricsResponse> {
  return request<MetricsResponse>("/api/metrics");
}

export const LABEL_COLORS: Record<number, string> = {
  0: "#22c55e",
  1: "#f59e0b",
  2: "#f97316",
  3: "#ef4444",
};

export const LABEL_SHORT: Record<string, string> = {
  no_toxico: "No Tóxico",
  ofensivo: "Ofensivo",
  odio: "Odio",
  amenazas: "Amenazas",
};
