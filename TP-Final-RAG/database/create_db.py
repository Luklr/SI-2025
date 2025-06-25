import sqlite3

def crear_base_datos_universidad(db_path='universidad.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Crear tabla Estudiantes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS estudiantes (
        id INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        edad INTEGER,
        carrera TEXT,
        promedio REAL,
        fecha_ingreso DATE
    )
    ''')

    # Crear tabla Cursos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cursos (
        id INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        creditos INTEGER,
        profesor TEXT,
        departamento TEXT
    )
    ''')

    # Crear tabla Inscripciones
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inscripciones (
        id INTEGER PRIMARY KEY,
        estudiante_id INTEGER,
        curso_id INTEGER,
        calificacion REAL,
        semestre TEXT,
        FOREIGN KEY (estudiante_id) REFERENCES estudiantes (id),
        FOREIGN KEY (curso_id) REFERENCES cursos (id)
    )
    ''')

    # Datos de ejemplo
    estudiantes_data = [
        (1, 'Juan', 'Pérez', 20, 'Ingeniería Informática', 8.5, '2022-03-01'),
        (2, 'María', 'González', 21, 'Ingeniería Informática', 9.2, '2021-03-01'),
        (3, 'Carlos', 'Rodríguez', 22, 'Ingeniería Industrial', 7.8, '2020-03-01'),
        (4, 'Ana', 'López', 19, 'Matemáticas', 9.5, '2023-03-01'),
        (5, 'Luis', 'Martín', 23, 'Física', 8.1, '2019-03-01'),
        (6, 'Sofía', 'Fernández', 20, 'Ingeniería Informática', 8.9, '2022-08-15'),
        (7, 'Pedro', 'Sánchez', 24, 'Física', 7.7, '2018-03-01'),
        (8, 'Lucía', 'Ramírez', 21, 'Matemáticas', 9.7, '2021-09-01')
    ]

    cursos_data = [
        (1, 'Algoritmos y Estructuras de Datos', 6, 'Dr. Smith', 'Informática'),
        (2, 'Cálculo I', 8, 'Dra. Johnson', 'Matemáticas'),
        (3, 'Física General', 6, 'Dr. Brown', 'Física'),
        (4, 'Base de Datos', 6, 'Dr. Davis', 'Informática'),
        (5, 'Estadística', 4, 'Dra. Wilson', 'Matemáticas'),
        (6, 'Electromagnetismo', 5, 'Dr. White', 'Física')
    ]

    inscripciones_data = [
        (1, 1, 1, 8.5, '2023-1'),
        (2, 1, 2, 7.8, '2023-1'),
        (3, 2, 1, 9.2, '2023-1'),
        (4, 2, 4, 9.0, '2023-1'),
        (5, 3, 3, 7.5, '2023-1'),
        (6, 4, 2, 9.8, '2023-1'),
        (7, 5, 3, 8.2, '2023-1'),
        (8, 6, 1, 8.7, '2023-2'),
        (9, 7, 6, 7.9, '2023-2'),
        (10, 8, 5, 9.6, '2023-2')
    ]

    cursor.executemany('INSERT OR REPLACE INTO estudiantes VALUES (?,?,?,?,?,?,?)', estudiantes_data)
    cursor.executemany('INSERT OR REPLACE INTO cursos VALUES (?,?,?,?,?)', cursos_data)
    cursor.executemany('INSERT OR REPLACE INTO inscripciones VALUES (?,?,?,?,?)', inscripciones_data)

    conn.commit()
    conn.close()
    print(f"✅ Base de datos de universidad creada en {db_path}")