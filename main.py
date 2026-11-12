import sys
import bcrypt

from PyQt6 import QtWidgets, uic
from src.dashboard import TelaDashboard
from src.cadastro import TelaCadastro
from utils.cnn import conectar


class TelaLogin(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        uic.loadUi("views/login.ui", self)

        # Conexão dos botões
        self.btn_entrar.clicked.connect(
            self.verificar_login
        )

        self.btn_cadastrar_usuario.clicked.connect(
            self.criar_conta
        )

        # Enter no usuário passa para o campo de senha
        self.txt_usuario.returnPressed.connect(
            self.txt_senha.setFocus
        )

        # Enter na senha executa o login
        self.txt_senha.returnPressed.connect(
            self.btn_entrar.click
        )

    def criar_conta(self):
        self.nova_tela = TelaCadastro()
        self.nova_tela.show()
        self.close()

    def verificar_login(self):
        usuario_digitado = self.txt_usuario.text().strip()
        senha_digitada = self.txt_senha.text()

        if not usuario_digitado or not senha_digitada:
            QtWidgets.QMessageBox.warning(
                self,
                "Aviso",
                "Preencha o usuário e a senha."
            )
            return

        conexao = None
        cursor = None

        try:
            conexao = conectar()
            cursor = conexao.cursor()

            cursor.execute(
                """
                SELECT nome, senha
                FROM usuario
                WHERE login = %s
                """,
                (usuario_digitado,)
            )

            resultado = cursor.fetchone()

            if resultado is None:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Erro",
                    "Usuário ou senha incorretos."
                )
                return

            nome_usuario = resultado[0]
            senha_hash = resultado[1]

            senha_correta = bcrypt.checkpw(
                senha_digitada.encode("utf-8"),
                senha_hash.encode("utf-8")
            )

            if senha_correta:
                self.nova_tela = TelaDashboard(
                    nome_usuario
                )

                self.nova_tela.show()
                self.close()

            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Erro",
                    "Usuário ou senha incorretos."
                )

                self.txt_senha.clear()
                self.txt_senha.setFocus()

        except Exception as erro:
            QtWidgets.QMessageBox.critical(
                self,
                "Erro",
                str(erro)
            )

        finally:
            if cursor is not None:
                cursor.close()

            if conexao is not None:
                conexao.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    janela = TelaLogin()
    janela.show()

    sys.exit(app.exec())