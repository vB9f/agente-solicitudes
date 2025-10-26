import os
import pandas as pd
from langchain.tools import tool

@tool("consultar_estado")
def consultar_estado(n_solicitud: str, nombre_asegurado: str = None) -> str:
    """Consulta el estado de una solicitud de reembolso por número. 
    Permite el acceso total si 'nombre_asegurado' es nulo (modo Admin).
    
    Argumentos:
    1. n_solicitud (código): El número de solicitud (Ej: MED_00001).
    2. nombre_asegurado (str, opcional): El nombre completo del usuario logueado (Se usa para filtro, si está presente).
    """
    archivo = os.path.join(os.path.dirname(__file__), "dataReembolsos.csv")

    #CHECKPOINT
    #print("CHECKPOINT: Tool identificó archivo .csv")    

    df = pd.read_csv(archivo)

    #CHECKPOINT
    #print("CHECKPOINT: Tool leyó archivo .csv")

    consulta = df[df['N_Solicitud'].str.strip() == n_solicitud.strip()]
    
    if consulta.empty:
        return "⚠️ No se encontró ninguna solicitud con ese número."
    
    fila = consulta.iloc[0]
    
    nombre_asegurado = nombre_asegurado.strip() if nombre_asegurado else None

    if nombre_asegurado:
        if fila['NomUsuario'].strip() != nombre_asegurado:
            return "⚠️ No se encontró ninguna solicitud con ese número asociada a tu usuario."

    return (
        f"📄 Solicitud N° {fila['N_Solicitud']}\n"
        f"👤 Usuario: {fila['NomUsuario']}\n"
        f"👤 Beneficiario: {fila['NomBeneficiario']}\n"
        f"💬 Tipo de gasto: {fila['TipoGasto']}\n"
        f"💰 Monto: S/ {fila['Monto']}\n"
        f"📅 Fecha de Registro: {fila['FechaRegistro']}\n"
        f"📌 Estado: {fila['Estado']}\n"
        f"🩺 Detalle: {fila['RespuestaEquipo']}"
    )