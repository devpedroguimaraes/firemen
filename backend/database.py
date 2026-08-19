import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash


# =========================================================
# CAMINHOS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE = BASE_DIR / "firemen.db"


# =========================================================
# CONEXÃO COM O BANCO
# =========================================================

def conectar():

    conexao = sqlite3.connect(DATABASE)

    conexao.row_factory = sqlite3.Row

    return conexao


# =========================================================
# CRIAÇÃO / ATUALIZAÇÃO DO BANCO
# =========================================================

def criar_banco():

    conexao = conectar()

    cursor = conexao.cursor()

    # =====================================================
    # TABELA DE USUÁRIOS
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            nome TEXT NOT NULL,

            data_nascimento TEXT,

            cpf TEXT UNIQUE,

            endereco TEXT,

            email TEXT NOT NULL UNIQUE,

            telefone TEXT,

            senha TEXT NOT NULL,

            tipo TEXT NOT NULL DEFAULT 'aluno',

            ativo INTEGER NOT NULL DEFAULT 1,

            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # =====================================================
    # ATUALIZAÇÃO DE BANCOS ANTIGOS
    # =====================================================

    colunas = [
        ("data_nascimento", "TEXT"),
        ("cpf", "TEXT"),
        ("endereco", "TEXT"),
        ("telefone", "TEXT")
    ]

    for nome_coluna, tipo_coluna in colunas:

        try:

            cursor.execute(
                f"""
                ALTER TABLE usuarios
                ADD COLUMN {nome_coluna} {tipo_coluna}
                """
            )

        except sqlite3.OperationalError:

            # A coluna já existe
            pass

    # =====================================================
    # ÍNDICE DO CPF
    # =====================================================

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_usuarios_cpf
        ON usuarios(cpf)
    """)

    conexao.commit()

    cursor.close()

    conexao.close()


# =========================================================
# CRIAR USUÁRIO DE TESTE
# =========================================================

def criar_usuario_teste():

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id
        FROM usuarios
        WHERE email = ?
    """, (
        "aluno@firemencursos.com.br",
    ))

    usuario = cursor.fetchone()

    if usuario is None:

        senha_hash = generate_password_hash("123456")

        cursor.execute("""
            INSERT INTO usuarios (

                nome,
                data_nascimento,
                cpf,
                endereco,
                email,
                telefone,
                senha,
                tipo,
                ativo

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            "Aluno FIREMEN",

            "",

            "",

            "",

            "aluno@firemencursos.com.br",

            "",

            senha_hash,

            "aluno",

            1

        ))

        conexao.commit()

    cursor.close()

    conexao.close()


# =========================================================
# CRIAR ADMINISTRADOR DE TESTE
# =========================================================

def criar_admin_teste():

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id
        FROM usuarios
        WHERE email = ?
    """, (
        "admin@firemencursos.com.br",
    ))

    usuario = cursor.fetchone()

    if usuario is None:

        senha_hash = generate_password_hash("admin123")

        cursor.execute("""
            INSERT INTO usuarios (

                nome,
                email,
                senha,
                tipo,
                ativo

            )

            VALUES (?, ?, ?, ?, ?)
        """, (

            "Administrador FIREMEN",

            "admin@firemencursos.com.br",

            senha_hash,

            "admin",

            1

        ))

        conexao.commit()

    cursor.close()

    conexao.close()


# =========================================================
# BUSCAR USUÁRIO PARA LOGIN
# =========================================================

def buscar_usuario(email, senha):

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
        SELECT

            id,
            nome,
            email,
            senha,
            tipo

        FROM usuarios

        WHERE email = ?

        AND ativo = 1

    """, (
        email,
    ))

    usuario = cursor.fetchone()

    cursor.close()

    conexao.close()

    if usuario:

        senha_correta = check_password_hash(
            usuario["senha"],
            senha
        )

        if senha_correta:

            return {

                "id": usuario["id"],

                "nome": usuario["nome"],

                "email": usuario["email"],

                "tipo": usuario["tipo"]

            }

    return None


# =========================================================
# CADASTRAR ALUNO
# =========================================================

def cadastrar_aluno(
    nome,
    data_nascimento,
    cpf,
    endereco,
    email,
    telefone,
    senha
):

    conexao = conectar()

    cursor = conexao.cursor()

    # =====================================================
    # VERIFICAR E-MAIL OU CPF EXISTENTE
    # =====================================================

    cursor.execute("""
        SELECT id
        FROM usuarios

        WHERE email = ?

        OR cpf = ?

    """, (
        email,
        cpf
    ))

    usuario = cursor.fetchone()

    if usuario:

        cursor.close()

        conexao.close()

        return False

    # =====================================================
    # GERAR HASH DA SENHA
    # =====================================================

    senha_hash = generate_password_hash(senha)

    # =====================================================
    # INSERIR ALUNO
    # =====================================================

    cursor.execute("""
        INSERT INTO usuarios (

            nome,
            data_nascimento,
            cpf,
            endereco,
            email,
            telefone,
            senha,
            tipo,
            ativo

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        nome,

        data_nascimento,

        cpf,

        endereco,

        email,

        telefone,

        senha_hash,

        "aluno",

        1

    ))

    conexao.commit()

    cursor.close()

    conexao.close()

    return True