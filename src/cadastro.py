import sys
#import pymysql
import bcrypt
from PyQt6 import QtWidgets, uic
from utils.cnn import conectar


class TelaCadastro(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        uic.loadUi("views/cadastro.ui", self)


        self.btn_cadastrar.clicked.connect(self.cadastrar)
        self.btn_voltar_login.clicked.connect(self.voltar)

    def voltar(self):
        from main import TelaLogin
        self.nova_tela = TelaLogin()
        self.nova_tela.show()
        self.close()

    def cadastrar(self):

        nome = self.txt_nome.text()
        login = self.txt_login.text()
        senha = self.txt_senha.text()
        confirma = self.txt_usuario_5.text()

        if not nome or not login or not senha:
            QtWidgets.QMessageBox.warning(
                self,
                "Erro",
                "Preencha todos os campos."
            )
            return

        if senha != confirma:
            QtWidgets.QMessageBox.warning(
                self,
                "Erro",
                "As senhas não conferem!"
            )
            return

        try:

            senha_hash = bcrypt.hashpw(
                senha.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")



            conexao = conectar()
            cursor = conexao.cursor()

            sql = """
            INSERT INTO usuario
            (nome, login, senha, email)
            VALUES (%s, %s, %s, %s)
            """

            cursor.execute(
                sql,
                (
                    nome,
                    login,
                    senha_hash,
                    ""
                )
            )

            conexao.commit()

            cursor.close()
            conexao.close()

            QtWidgets.QMessageBox.information(
                self,
                "Sucesso",
                "Usuário cadastrado com sucesso!"
            )

            self.txt_nome.clear()
            self.txt_login.clear()
            self.txt_senha.clear()
            self.txt_usuario_5.clear()

        except Exception as erro:

            QtWidgets.QMessageBox.critical(
                self,
                "Erro",
                str(erro)
            )

'''
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    janela = TelaCadastro()
    janela.show()

   
    sys.exit(app.exec())
'''