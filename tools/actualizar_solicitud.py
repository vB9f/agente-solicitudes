import os
import pandas as pd
import datetime
from langchain.tools import tool

@tool("actualizar_solicitud")
def actualizar_solicitud(n_solicitud: str, nuevo_estado: str, nueva_respuesta: str) -> str:
    """
    Actualiza el Estado, FechaRespuesta y la RespuestaEquipo de una solicitud de reembolso médica registrada.
    El 'nuevo_estado' debe ser uno de: Pendiente, Aprobado, Rechazado, Observado.
    La 'nueva_respuesta' es el comentario/justificación del equipo médico.
    Si bien las variables indican 'nuevo' en su denominación, si el usuario solo indica 'estado' o 'respuesta' se debería asociar a ellas.
    """

    archivo = os.path.join(os.path.dirname(__file__), "dataReembolsos.csv")

    #CHECKPOINT
    #print("CHECKPOINT: Tool identificó archivo .csv")

    df = pd.read_csv(archivo)
    
    #CHECKPOINT
    #print("CHECKPOINT: Tool leyó archivo .csv")

    # Normalizar la entrada de estado y verificar validez
    nuevo_estado = nuevo_estado.strip().capitalize()
    estados_validos = ["Pendiente", "Aprobado", "Rechazado", "Observado"]
    if nuevo_estado not in estados_validos:
        return f"⚠️ Estado no válido. Debe ser uno de: {', '.join(estados_validos)}"

    # Buscar la fila a actualizar
    idx = df[df['N_Solicitud'] == n_solicitud].index
    
    if idx.empty:
        return f"⚠️ No se encontró ninguna solicitud con el número: {n_solicitud}"

    df.loc[idx, 'Estado'] = nuevo_estado
    df.loc[idx, 'RespuestaEquipo'] = nueva_respuesta
    df.loc[idx, 'FechaRespuesta'] = datetime.date.today().strftime("%Y-%m-%d")

    df.to_csv(archivo, index=False)

    return (
        f"✅ Solicitud **{n_solicitud}** actualizada con éxito:\n"
        f"- Nuevo Estado: **{nuevo_estado}**\n"
        f"- Nueva Respuesta: **{nueva_respuesta}**"
    )