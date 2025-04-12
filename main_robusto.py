
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

def safe_get_json(url):
    try:
        res = requests.get(url, timeout=5)
        return res.json()
    except Exception as e:
        return {"__error__": str(e)}

@app.get("/")
def get_dolar_data():
    dolar = safe_get_json("https://dolarapi.com/v1/dolares")
    cripto = safe_get_json("https://criptoya.com/api/dolar/calaverita/ars/0.1")

    result = {"cotizaciones": {}, "desarbitrajes": {}, "errores": {}}

    if isinstance(dolar, list):
        try:
            result["cotizaciones"]["oficial"] = next(d for d in dolar if d["nombre"] == "oficial")["venta"]
            result["cotizaciones"]["blue"] = next(d for d in dolar if d["nombre"] == "blue")["venta"]
            result["cotizaciones"]["mep"] = next(d for d in dolar if d["nombre"] == "mep")["venta"]
            result["cotizaciones"]["ccl"] = next(d for d in dolar if d["nombre"] == "ccl")["venta"]
        except Exception as e:
            result["errores"]["dolar"] = str(e)
    else:
        result["errores"]["dolar"] = dolar.get("__error__", "Respuesta inválida")

    if isinstance(cripto, dict) and "totalAsk" in cripto:
        result["cotizaciones"]["cripto"] = cripto["totalAsk"]
    else:
        result["errores"]["cripto"] = cripto.get("__error__", "Respuesta inválida")

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
