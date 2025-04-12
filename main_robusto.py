
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
            result["cotizaciones"]["oficial"] = next(d for d in dolar if d["casa"] == "oficial")["venta"]
            result["cotizaciones"]["blue"] = next(d for d in dolar if d["casa"] == "blue")["venta"]
            result["cotizaciones"]["mep"] = next(d for d in dolar if d["casa"] == "bolsa")["venta"]
            result["cotizaciones"]["ccl"] = next(d for d in dolar if d["casa"] == "contadoconliqui")["venta"]
            result["cotizaciones"]["cripto"] = next(d for d in dolar if d["casa"] == "cripto")["venta"]
        except Exception as e:
            result["errores"]["dolar"] = str(e)
    else:
        result["errores"]["dolar"] = dolar.get("__error__", "Respuesta inválida")

    def spread(base, contra):
        return round(((contra - base) / base) * 100, 2)

    c = result["cotizaciones"]
    if "blue" in c and "oficial" in c:
        result["desarbitrajes"]["blue_vs_oficial"] = f"{spread(c['oficial'], c['blue'])}%"
    if "mep" in c and "oficial" in c:
        result["desarbitrajes"]["mep_vs_oficial"] = f"{spread(c['oficial'], c['mep'])}%"
    if "ccl" in c and "mep" in c:
        result["desarbitrajes"]["ccl_vs_mep"] = f"{spread(c['mep'], c['ccl'])}%"
    if "cripto" in c and "blue" in c:
        result["desarbitrajes"]["cripto_vs_blue"] = f"{spread(c['blue'], c['cripto'])}%"

    return result
