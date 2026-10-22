import sys
#import pymysql
import bcrypt
from PyQt6 import QtWidgets, uic
from src.dashboard import TelaDashboard
from src.cadastro import TelaCadastro

from utils.cnn import conectar


class TelaLogin(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        uic.loadUi("views/login.ui", self)

        self.btn_entrar.clicked.connect(self.verificar_login)
        self.btn_cadastrar_usuario.clicked.connect(self.criar_conta)

    def criar_conta(self):

        self.nova_tela = TelaCadastro()
        self.nova_tela.show()
        self.close()

    def verificar_login(self):

        usuario_digitado = self.txt_usuario.text()
        senha_digitada = self.txt_senha.text()

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

            cursor.close()
            conexao.close()

            if resultado:

                nome_usuario = resultado[0]
                senha_hash = resultado[1]

                if bcrypt.checkpw(
                    senha_digitada.encode("utf-8"),
                    senha_hash.encode("utf-8")
                ):
                    '''
                    QtWidgets.QMessageBox.information(
                        self,
                        "Sucesso",
                        "Login realizado com sucesso!"
                    )
                    '''
                    self.nova_tela = TelaDashboard(nome_usuario)
                    self.nova_tela.show()
                    self.close()

                else:

                    QtWidgets.QMessageBox.warning(
                        self,
                        "Erro",
                        "Usuário ou senha incorretos."
                    )

            else:

                QtWidgets.QMessageBox.warning(
                    self,
                    "Erro",
                    "Usuário não encontrado."
                )

        except Exception as erro:

            QtWidgets.QMessageBox.critical(
                self,
                "Erro",
                str(erro)
            )

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    janela = TelaLogin()
    janela.show()

    sys.exit(app.exec())