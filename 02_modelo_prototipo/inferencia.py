from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "modelo_entrenado"
LEGACY_MODEL_PATH = BASE_DIR / "mi_modelo_xlmr"

LABELS = [
    "No Tóxico",
    "Lenguaje Ofensivo",
    "Discurso de Odio",
    "Amenazas / Violencia",
]


def cargar_modelo():
    """Carga el modelo entrenado y el tokenizador desde la ruta actual."""
    model_dir = MODEL_PATH if MODEL_PATH.exists() else LEGACY_MODEL_PATH
    if not model_dir.exists():
        raise FileNotFoundError(
            f"No se encontró la carpeta del modelo. Se esperaba '{MODEL_PATH}' o '{LEGACY_MODEL_PATH}'."
        )

    print(f"Cargando tokenizador y modelo desde: {model_dir}")
    tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
    model = AutoModelForSequenceClassification.from_pretrained(str(model_dir))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    print(f"Dispositivo activo: {device}")

    return tokenizer, model, device


def predecir_toxicidad(texto: str, tokenizer, model, device):
    """Recibe una frase y retorna la clase predicha, confianza y probabilidades."""
    inputs = tokenizer(
        texto,
        return_tensors="pt",
        truncation=True,
        max_length=128,
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]

    pred_idx = torch.argmax(probs).item()
    clase_predicha = LABELS[pred_idx]
    confianza = probs[pred_idx].item()
    return clase_predicha, confianza, probs


def ejecutar_ejemplos(tokenizer, model, device):
    ejemplos = [
        "Hola a todos, feliz inicio de semana",
        "Ese maje no sabe lo que esta haciendo",
        "Te voy a ir a buscar a la salida para romperte la cara",
    ]

    print("\n=== RESULTADOS DE INFERENCIA ===")
    for texto in ejemplos:
        clase, conf, _ = predecir_toxicidad(texto, tokenizer, model, device)
        print(f"\nTexto: '{texto}'")
        print(f"Predicción: {clase} (Confianza: {conf:.2%})")


def main():
    tokenizer, model, device = cargar_modelo()
    ejecutar_ejemplos(tokenizer, model, device)

    print("\n--- MODO INTERACTIVO ---")
    print("Escribe un texto para evaluar (o 'salir' para terminar):")

    while True:
        entrada = input("\nTexto > ")
        if entrada.lower() in ["salir", "exit", "quit"]:
            print("Saliendo del modo interactivo.")
            break
        if not entrada.strip():
            continue

        clase, conf, probs = predecir_toxicidad(entrada, tokenizer, model, device)
        print(f"-> Clasificación: {clase} ({conf:.2%})")
        print("   Desglose de probabilidades:")
        for idx, label in enumerate(LABELS):
            print(f"   - {label}: {probs[idx].item():.2%}")


if __name__ == "__main__":
    main()