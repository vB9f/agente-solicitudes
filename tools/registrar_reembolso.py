import os
import pandas as pd
import datetime
from langchain.tools import tool

@tool("registrar_reembolso")
def registrar_reembolso(nombre_asegurado: str, tipo_gasto: str, monto: float, nombre_beneficiario: str = None) -> str:
    """
    Registra una nueva solicitud de reembolso médico en la base de datos CSV llamada 'dataReembolsos.csv'.
    
    Argumentos:
    1. nombre_asegurado (str): Nombre completo del titular del beneficio.
    2. tipo_gasto (str): Tipo de gasto (Medicinas, Exámenes, Consultas).
    3. monto (float): Monto del gasto.
    4. nombre_beneficiario (str, opcional): Nombre de la persona que recibió el servicio (si es un dependiente o es diferente al asegurado).

    Si el usuario no te ha compartido los datos de gasto (tipo y monto), pregunta por ellos. 
    El nombre del Asegurado se toma automáticamente del contexto.

    El número de solicitud depende del tipo de gasto:
    - Medicinas → prefijo 'MED'
    - Exámenes → prefijo 'EXA'
    - Consultas → prefijo 'CON'
    Si el usuario no te ha compartido alguno de los datos necesarios para registrar la solicitud, volver a preguntar por los datos pendientes.
    """
    archivo = os.path.join(os.path.dirname(__file__), "dataReembolsos.csv")
    
    #CHECKPOINT
    #print("CHECKPOINT: Tool identificó archivo .csv")

    # Crear archivo si no existe
    columnas = ["N_Solicitud", "NomUsuario", "NomBeneficiario", "TipoGasto", "Monto", "Estado", "FechaRegistro", "RespuestaEquipo"]
    if not os.path.exists(archivo):
        pd.DataFrame(columns=columnas).to_csv(archivo, index=False)

    # Leer archivo existente
    df = pd.read_csv(archivo)
    
    #CHECKPOINT
    #print("CHECKPOINT: Tool leyó archivo .csv")

    # Normalizar tipo de gasto
    tipo_gasto = tipo_gasto.strip().capitalize()
    prefijos = {"Medicinas": "MED", "Exámenes": "EXA", "Consultas": "CON"}
    prefijo = prefijos.get(tipo_gasto, "OTR")

    # Calcular siguiente número incremental
    df_tipo = df[df["TipoGasto"].str.lower() == tipo_gasto.lower()] if not df.empty else pd.DataFrame()
    if not df_tipo.empty:
        try:
            ult_codigo = df_tipo["N_Solicitud"].iloc[-1]
            ult_num = int(ult_codigo.split("_")[1])
        except Exception:
            ult_num = 0
    else:
        ult_num = 0

    nuevo_codigo = f"{prefijo}_{ult_num + 1:05d}"
    
    #CHECKPOINT
    #print("CHECKPOINT: Tool creó nuevo código de reembolso")

    beneficiario_final = nombre_beneficiario if nombre_beneficiario else nombre_asegurado

    # Nueva fila
    nueva_fila = {
        "N_Solicitud": nuevo_codigo,
        "NomUsuario": nombre_asegurado,
        "NomBeneficiario": beneficiario_final,
        "TipoGasto": tipo_gasto,
        "Monto": monto,
        "Estado": "Pendiente",
        "FechaRegistro": datetime.date.today().strftime("%Y-%m-%d"),
        "FechaRespuesta": "No",
        "RespuestaEquipo": "En revisión por el área médica"
    }

    # Agregar y guardar
    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
    df.to_csv(archivo, index=False)

    return f"✅ Solicitud registrada con éxito. Código: {nuevo_codigo}, Estado: Pendiente."