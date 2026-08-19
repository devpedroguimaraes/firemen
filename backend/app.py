from pathlib import Path

from flask import (
    Flask,
    send_from_directory,
    request,
    redirect,
    session,
    render_template
)

from database import (
    criar_banco,
    criar_usuario_teste,
    criar_admin_teste,
    buscar_usuario,
    cadastrar_aluno,
    conectar
)


# =========================================================
# CAMINHOS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PUBLIC_DIR = BASE_DIR / "frontend" / "public"
CSS_DIR = BASE_DIR / "frontend" / "css"
JS_DIR = BASE_DIR / "frontend" / "js"


# =========================================================
# FLASK
# =========================================================

app = Flask(
    __name__,
    template_folder=str(
        BASE_DIR / "frontend" / "templates"
    )
)

app.config["SECRET_KEY"] = "FIREMEN_CURSO_SECRET_2026"

app.config["SESSION_COOKIE_HTTPONLY"] = True

app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


# =========================================================
# BANCO DE DADOS
# =========================================================

criar_banco()

criar_usuario_teste()

criar_admin_teste()


# =========================================================
# INÍCIO
# =========================================================

@app.route("/")
def home():

    return send_from_directory(
        PUBLIC_DIR,
        "index.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        senha = request.form.get(
            "password",
            ""
        ).strip()

        print("================================")
        print("TENTATIVA DE LOGIN")
        print("E-mail:", email)

        usuario = buscar_usuario(
            email,
            senha
        )

        if usuario:

            session.clear()

            session["usuario"] = {

                "id": usuario["id"],

                "email": usuario["email"],

                "nome": usuario["nome"],

                "tipo": usuario["tipo"]

            }

            session.modified = True

            print("LOGIN CORRETO")

            print(
                "USUÁRIO:",
                session["usuario"]
            )

            print("================================")

            # =========================================
            # ADMIN
            # =========================================

            if usuario["tipo"] == "admin":

                return redirect("/admin")

            # =========================================
            # ALUNO
            # =========================================

            return redirect("/area-aluno")

        print("LOGIN INCORRETO")

        print("================================")

        return redirect(
            "/login?erro=1"
        )

    return send_from_directory(
        PUBLIC_DIR,
        "login.html"
    )


# =========================================================
# ÁREA DO ALUNO
# =========================================================

@app.route("/area-aluno")
def area_aluno():

    if "usuario" not in session:

        return redirect("/login")

    usuario = session["usuario"]

    return render_template(
        "area-aluno.html",
        usuario=usuario
    )


# =========================================================
# PAINEL ADMINISTRATIVO
# =========================================================

@app.route("/admin")
def admin():

    if "usuario" not in session:

        return redirect("/login")

    if session["usuario"]["tipo"] != "admin":

        return redirect("/area-aluno")

    usuario = session["usuario"]

    return render_template(
        "admin.html",
        usuario=usuario
    )


# =========================================================
# GERENCIAR ALUNOS
# =========================================================

@app.route(
    "/admin/alunos",
    methods=["GET", "POST"]
)
def admin_alunos():

    # =========================================
    # VERIFICAR LOGIN
    # =========================================

    if "usuario" not in session:

        return redirect("/login")

    # =========================================
    # VERIFICAR ADMIN
    # =========================================

    if session["usuario"]["tipo"] != "admin":

        return redirect("/area-aluno")

    mensagem = None

    tipo_mensagem = None

    # =========================================
    # CADASTRAR ALUNO
    # =========================================

    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()

        data_nascimento = request.form.get(
            "data_nascimento",
            ""
        ).strip()

        cpf = request.form.get(
            "cpf",
            ""
        ).strip()

        endereco = request.form.get(
            "endereco",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        telefone = request.form.get(
            "telefone",
            ""
        ).strip()

        senha = request.form.get(
            "senha",
            ""
        ).strip()

        # =========================================
        # VALIDAR CAMPOS
        # =========================================

        if (
            not nome
            or not data_nascimento
            or not cpf
            or not endereco
            or not email
            or not telefone
            or not senha
        ):

            mensagem = (
                "Preencha todos os campos."
            )

            tipo_mensagem = "erro"

        # =========================================
        # VALIDAR SENHA
        # =========================================

        elif len(senha) < 6:

            mensagem = (
                "A senha deve ter pelo menos 6 caracteres."
            )

            tipo_mensagem = "erro"

        # =========================================
        # CADASTRAR
        # =========================================

        else:

            cadastrado = cadastrar_aluno(

                nome,

                data_nascimento,

                cpf,

                endereco,

                email,

                telefone,

                senha

            )

            if cadastrado:

                mensagem = (
                    "Aluno cadastrado com sucesso!"
                )

                tipo_mensagem = "sucesso"

            else:

                mensagem = (
                    "Este e-mail ou CPF já possui cadastro."
                )

                tipo_mensagem = "erro"

    # =========================================
    # BUSCAR ALUNOS
    # =========================================

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            id,
            nome,
            email,
            ativo
        FROM usuarios
        WHERE tipo = 'aluno'
        ORDER BY nome
    """)

    alunos = cursor.fetchall()

    cursor.close()

    conexao.close()

    # =========================================
    # EXIBIR PÁGINA
    # =========================================

    return render_template(

        "gerenciar-alunos.html",

        usuario=session["usuario"],

        alunos=alunos,

        mensagem=mensagem,

        tipo_mensagem=tipo_mensagem

    )


# =========================================================
# VISUALIZAR ALUNO
# =========================================================

@app.route("/admin/alunos/<int:aluno_id>")
def visualizar_aluno(aluno_id):

    # =========================================
    # VERIFICAR LOGIN
    # =========================================

    if "usuario" not in session:

        return redirect("/login")

    # =========================================
    # VERIFICAR ADMIN
    # =========================================

    if session["usuario"]["tipo"] != "admin":

        return redirect("/area-aluno")

    # =========================================
    # CONECTAR AO BANCO
    # =========================================

    conexao = conectar()

    cursor = conexao.cursor()

    # =========================================
    # BUSCAR ALUNO
    # =========================================

    cursor.execute("""
        SELECT
            id,
            nome,
            data_nascimento,
            cpf,
            endereco,
            email,
            telefone,
            ativo,
            criado_em
        FROM usuarios
        WHERE id = ?
        AND tipo = 'aluno'
    """, (aluno_id,))

    aluno = cursor.fetchone()

    cursor.close()

    conexao.close()

    # =========================================
    # ALUNO NÃO ENCONTRADO
    # =========================================

    if aluno is None:

        return redirect("/admin/alunos")

    # =========================================
    # EXIBIR DADOS
    # =========================================

    return render_template(

        "visualizar-aluno.html",

        usuario=session["usuario"],

        aluno=aluno

    )


# =========================================================
# EDITAR ALUNO
# =========================================================
#
# NOVA URL:
#
# /admin/alunos/<id>/editar
#
# Exemplo:
#
# /admin/alunos/5/editar
#
# =========================================================

@app.route(
    "/admin/alunos/<int:aluno_id>/editar",
    methods=["GET", "POST"]
)
@app.route(
    "/admin/alunos/editar/<int:aluno_id>",
    methods=["GET", "POST"]
)
def editar_aluno(aluno_id):

    # =========================================
    # VERIFICAR LOGIN
    # =========================================

    if "usuario" not in session:

        return redirect("/login")

    # =========================================
    # VERIFICAR ADMIN
    # =========================================

    if session["usuario"]["tipo"] != "admin":

        return redirect("/area-aluno")

    # =========================================
    # CONECTAR AO BANCO
    # =========================================

    conexao = conectar()

    cursor = conexao.cursor()

    mensagem = None

    tipo_mensagem = None

    # =========================================
    # BUSCAR ALUNO
    # =========================================

    cursor.execute("""
        SELECT
            id,
            nome,
            data_nascimento,
            cpf,
            endereco,
            email,
            telefone,
            ativo
        FROM usuarios
        WHERE id = ?
        AND tipo = 'aluno'
    """, (aluno_id,))

    aluno = cursor.fetchone()

    # =========================================
    # ALUNO NÃO ENCONTRADO
    # =========================================

    if aluno is None:

        cursor.close()

        conexao.close()

        return redirect("/admin/alunos")

    # =========================================
    # ATUALIZAR ALUNO
    # =========================================

    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()

        data_nascimento = request.form.get(
            "data_nascimento",
            ""
        ).strip()

        cpf = request.form.get(
            "cpf",
            ""
        ).strip()

        endereco = request.form.get(
            "endereco",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        telefone = request.form.get(
            "telefone",
            ""
        ).strip()

        senha = request.form.get(
            "senha",
            ""
        ).strip()

        # =========================================
        # VALIDAR CAMPOS
        # =========================================

        if (
            not nome
            or not data_nascimento
            or not cpf
            or not endereco
            or not email
            or not telefone
        ):

            mensagem = (
                "Preencha todos os campos."
            )

            tipo_mensagem = "erro"

        # =========================================
        # VALIDAR SENHA
        # =========================================

        elif senha and len(senha) < 6:

            mensagem = (
                "A senha deve ter pelo menos 6 caracteres."
            )

            tipo_mensagem = "erro"

        else:

            # =========================================
            # VERIFICAR DUPLICIDADE
            # =========================================

            cursor.execute("""
                SELECT
                    id
                FROM usuarios
                WHERE
                    (email = ? OR cpf = ?)
                    AND id != ?
                    AND tipo = 'aluno'
            """, (
                email,
                cpf,
                aluno_id
            ))

            duplicado = cursor.fetchone()

            if duplicado:

                mensagem = (
                    "Este e-mail ou CPF já pertence a outro cadastro."
                )

                tipo_mensagem = "erro"

            else:

                # =========================================
                # ATUALIZAR COM SENHA
                # =========================================

                if senha:

                    from werkzeug.security import (
                        generate_password_hash
                    )

                    senha_hash = generate_password_hash(
                        senha
                    )

                    cursor.execute("""
                        UPDATE usuarios
                        SET
                            nome = ?,
                            data_nascimento = ?,
                            cpf = ?,
                            endereco = ?,
                            email = ?,
                            telefone = ?,
                            senha = ?
                        WHERE
                            id = ?
                            AND tipo = 'aluno'
                    """, (
                        nome,
                        data_nascimento,
                        cpf,
                        endereco,
                        email,
                        telefone,
                        senha_hash,
                        aluno_id
                    ))

                # =========================================
                # ATUALIZAR SEM ALTERAR SENHA
                # =========================================

                else:

                    cursor.execute("""
                        UPDATE usuarios
                        SET
                            nome = ?,
                            data_nascimento = ?,
                            cpf = ?,
                            endereco = ?,
                            email = ?,
                            telefone = ?
                        WHERE
                            id = ?
                            AND tipo = 'aluno'
                    """, (
                        nome,
                        data_nascimento,
                        cpf,
                        endereco,
                        email,
                        telefone,
                        aluno_id
                    ))

                # =========================================
                # SALVAR
                # =========================================

                conexao.commit()

                mensagem = (
                    "Aluno atualizado com sucesso!"
                )

                tipo_mensagem = "sucesso"

                # =========================================
                # BUSCAR DADOS ATUALIZADOS
                # =========================================

                cursor.execute("""
                    SELECT
                        id,
                        nome,
                        data_nascimento,
                        cpf,
                        endereco,
                        email,
                        telefone,
                        ativo
                    FROM usuarios
                    WHERE id = ?
                    AND tipo = 'aluno'
                """, (aluno_id,))

                aluno = cursor.fetchone()

    # =========================================
    # FECHAR BANCO
    # =========================================

    cursor.close()

    conexao.close()

    # =========================================
    # EXIBIR PÁGINA DE EDIÇÃO
    # =========================================

    return render_template(

        "editar-aluno.html",

        usuario=session["usuario"],

        aluno=aluno,

        mensagem=mensagem,

        tipo_mensagem=tipo_mensagem

    )

# =========================================================
# EXCLUIR ALUNO
# =========================================================

@app.route(
    "/admin/alunos/excluir/<int:aluno_id>",
    methods=["POST"]
)
def excluir_aluno(aluno_id):

    # =========================================
    # VERIFICAR LOGIN
    # =========================================

    if "usuario" not in session:

        return redirect("/login")

    # =========================================
    # VERIFICAR ADMIN
    # =========================================

    if session["usuario"]["tipo"] != "admin":

        return redirect("/area-aluno")

    # =========================================
    # CONECTAR AO BANCO
    # =========================================

    conexao = conectar()

    cursor = conexao.cursor()

    # =========================================
    # VERIFICAR SE O ALUNO EXISTE
    # =========================================

    cursor.execute("""
        SELECT id
        FROM usuarios
        WHERE id = ?
        AND tipo = 'aluno'
    """, (aluno_id,))

    aluno = cursor.fetchone()

    # =========================================
    # ALUNO NÃO ENCONTRADO
    # =========================================

    if aluno is None:

        cursor.close()

        conexao.close()

        return redirect("/admin/alunos")

    # =========================================
    # EXCLUIR ALUNO
    # =========================================

    cursor.execute("""
        DELETE FROM usuarios
        WHERE id = ?
        AND tipo = 'aluno'
    """, (aluno_id,))

    conexao.commit()

    cursor.close()

    conexao.close()

    # =========================================
    # VOLTAR PARA LISTA
    # =========================================

    return redirect(
        "/admin/alunos?excluido=1"
    )

# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================================================
# CSS
# =========================================================

@app.route("/css/<path:filename>")
def css(filename):

    return send_from_directory(
        CSS_DIR,
        filename
    )


# =========================================================
# JAVASCRIPT
# =========================================================

@app.route("/js/<path:filename>")
def js(filename):

    return send_from_directory(
        JS_DIR,
        filename
    )


# =========================================================
# OUTROS ARQUIVOS
# =========================================================

@app.route("/<path:filename>")
def frontend(filename):

    return send_from_directory(
        PUBLIC_DIR,
        filename
    )


# =========================================================
# EXECUTAR
# =========================================================

if __name__ == "__main__":

    app.run(

        debug=True,

        host="127.0.0.1",

        port=5000

    )