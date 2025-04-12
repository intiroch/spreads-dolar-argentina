
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

headers = {
    "User-Agent": "Mozilla/5.0"
}

def safe_get_json(url):
    try:
        res = requests.get(url, headers=headers, timeout=5)
        return res.json()
    except Exception as e:
        return {"__error__": str(e)}

@app.get("/")
def get_dolar_data():
    dolar = safe_get_json("https://dolarapi.com/v1/dolares")

    result = {"cotizaciones": {}, "desarbitrajes": {}, "errores": {}}

    if isinstance(dolar, list):
        try:
            for tipo in ["oficial", "blue", "bolsa", "contadoconliqui", "cripto"]:
                d = next((d for d in dolar if d["casa"] == tipo), None)
                if d:
                    clave = "mep" if tipo == "bolsa" else "ccl" if tipo == "contadoconliqui" else tipo
                    result["cotizaciones"][clave] = {
                        "compra": d["compra"],
                        "venta": d["venta"]
                    }
        except Exception as e:
            result["errores"]["dolar"] = str(e)
    else:
        result["errores"]["dolar"] = dolar.get("__error__", "Respuesta inválida")

    return result
