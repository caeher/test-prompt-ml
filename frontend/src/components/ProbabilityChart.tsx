import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ProbabilityMap } from "@/lib/api";
import { LABEL_COLORS, LABEL_SHORT } from "@/lib/api";

interface ProbabilityChartProps {
  probabilities: ProbabilityMap;
  predictedIndex: number;
}

export function ProbabilityChart({ probabilities, predictedIndex }: ProbabilityChartProps) {
  const data = Object.entries(probabilities).map(([key, value], index) => ({
    name: LABEL_SHORT[key] ?? key,
    value: Math.round(value * 1000) / 10,
    index,
  }));

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2f3336" vertical={false} />
          <XAxis dataKey="name" tick={{ fill: "#71767b", fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis
            domain={[0, 100]}
            tickFormatter={(v) => `${v}%`}
            tick={{ fill: "#71767b", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            formatter={(value) => [`${Number(value ?? 0)}%`, "Probabilidad"]}
            contentStyle={{
              background: "#16181c",
              border: "1px solid #2f3336",
              borderRadius: "8px",
            }}
          />
          <Bar dataKey="value" radius={[6, 6, 0, 0]}>
            {data.map((entry) => (
              <Cell
                key={entry.name}
                fill={LABEL_COLORS[entry.index]}
                opacity={entry.index === predictedIndex ? 1 : 0.55}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
