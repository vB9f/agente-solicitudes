# 🩺 Agente de Soporte de Reembolsos Médicos

Este proyecto implementa un agente conversacional inteligente basado en **LangGraph** y **Streamlit** para la gestión de solicitudes de reembolso. Su principal característica es uso de herramientas (tools) del agente y el **Control de Acceso Basado en Roles (RBAC)** que diferencia las capacidades entre usuarios generales y administradores.

## 🚀 Requisitos y Configuración Inicial

Para ejecutar la aplicación localmente, necesitas tener **Python 3.10 o superior** y una clave de API de OpenAI.

### - Instalación de dependencias

Ejecuta el siguiente comando para instalar todas las librerías necesarias (LangChain, Streamlit, Pandas, etc.):

```bash
pip install -r requirements.txt
```

### - Configuración de archivos necesarios

Para ejecutar el código necesitas los siguientes archivos en las ubicaciones específicas:

| Archivo | Ubicación | Columnas Clave |
| :--- | :--- | :--- |
| **`clave_api.txt`** | Raíz | Almacena tu clave de API de **OpenAI**. |
| **`dataUsuarios.csv`** | Raíz | Contiene credenciales y roles (`General` o `Administrador`) |
| **`dataReembolsos.csv`** | 'Tools' | Almacena el historial de solicitudes y sus estados. |

---

## ⚙️ Instrucciones de Ejecución Local

Para lanzar la interfaz web de Streamlit, utiliza el siguiente comando desde el directorio principal:

```bash
streamlit run app.py
```
