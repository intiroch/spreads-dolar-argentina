
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

@app.get("/")
def get_dolar_data():
    try:
        dolar = requests.get("https://dolarapi.com/v1/dolares").json()
        cripto = requests.get("https://criptoya.com/api/dolar/calaverita/ars/0.1").json()

        cotizaciones = {
            "oficial": next(d for d in dolar if d["nombre"] == "oficial")["venta"],
            "blue": next(d for d in dolar if d["nombre"] == "blue")["venta"],
            "mep": next(d for d in dolar if d["nombre"] == "mep")["venta"],
            "ccl": next(d for d in dolar if d["nombre"] == "ccl")["venta"],
            "cripto": cripto["totalAsk"]
        }

        def spread(base, contra):
            return round(((contra - base) / base) * 100, 2)

        desarbitrajes = {
            "blue_vs_oficial": f"{spread(cotizaciones['oficial'], cotizaciones['blue'])}%",
            "mep_vs_oficial": f"{spread(cotizaciones['oficial'], cotizaciones['mep'])}%",
            "ccl_vs_mep": f"{spread(cotizaciones['mep'], cotizaciones['ccl'])}%",
            "cripto_vs_blue": f"{spread(cotizaciones['blue'], cotizaciones['cripto'])}%"
        }

        return {
            "cotizaciones": cotizaciones,
            "desarbitrajes": desarbitrajes
        }

    except Exception as e:
        return {"error": str(e)}
