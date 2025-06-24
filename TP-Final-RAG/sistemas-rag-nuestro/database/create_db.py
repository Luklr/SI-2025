import pandas as pd
from sqlalchemy import text
from .database import Database
from .seeders import empleados_data, proyectos_data, ventas_data

engine = Database.get_engine()

# Crear DataFrames y guardar en la base de datos
df_empleados = pd.DataFrame(empleados_data)
df_proyectos = pd.DataFrame(proyectos_data)
df_ventas = pd.DataFrame(ventas_data)

# Guardar en la base de datos
df_empleados.to_sql("empleados", engine, if_exists="replace", index=False)
df_proyectos.to_sql("proyectos", engine, if_exists="replace", index=False)
df_ventas.to_sql("ventas", engine, if_exists="replace", index=False)

print("✅ Base de datos creada con éxito")
print(
    f"📊 Tablas creadas: empleados ({len(df_empleados)} filas), proyectos ({len(df_proyectos)} filas), ventas ({len(df_ventas)} filas)"
)

# Mostrar esquema de las tablas
with engine.connect() as conn:
    for tabla in ["empleados", "proyectos", "ventas"]:
        result = conn.execute(text(f"SELECT * FROM {tabla} LIMIT 2"))
        print(f"\n📋 Muestra de tabla '{tabla}':")
        for row in result:
            print(f"  {dict(row)}")
