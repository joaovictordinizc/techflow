from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QMessageBox, QAbstractItemView
from utils.cnn import conectar


class GerenciadorClientes:

    def __init__(self, tela):
        self.tela = tela

        # =========================
        # CONFIGURAÇÃO DA TABELA
        # =========================
        self.modelo = QStandardItemModel()

        self.modelo.setHorizontalHeaderLabels([
            "Código",
            "Nome",
            "CPF",
            "Telefone",
            "Email",
            "Cidade"
        ])

        self.tela.tableView.setModel(self.modelo)

        # Selecionar linha inteira
        self.tela.tableView.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.tela.tableView.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        # Não permitir editar diretamente pela tabela
        self.tela.tableView.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        # =========================
        # BOTÕES
        # =========================
        self.tela.btn_salvar.clicked.connect(            
            self.salvar_cliente
        )

        self.tela.btn_limpar.clicked.connect(
            self.limpar_campos
        )

        self.tela.btn_excluir.clicked.connect(
            self.excluir_cliente
        )

        # Duplo clique na tabela
        self.tela.tableView.doubleClicked.connect(
            self.carregar_campos_ao_duplo_clique
        )

        # =========================
        # CARREGA CLIENTES
        # =========================
        self.carregar_dados_na_tabela()

    # =========================================================
    # LISTAR CLIENTES
    # =========================================================
    def carregar_dados_na_tabela(self):

        self.modelo.removeRows(
            0,
            self.modelo.rowCount()
        )

        conexao = None
        cursor = None

        try:
            conexao = conectar()
            cursor = conexao.cursor()

            sql = """
                SELECT
                    id_clientes,
                    nome,
                    cpf,
                    telefone,
                    email,
                    cidade
                FROM clientes
                ORDER BY id_clientes
            """

            cursor.execute(sql)

            clientes = cursor.fetchall()

            print("Clientes encontrados:", len(clientes))

            for cliente in clientes:

                linha = [
                    QStandardItem(str(cliente[0] if cliente[0] is not None else "")),
                    QStandardItem(str(cliente[1] if cliente[1] is not None else "")),
                    QStandardItem(str(cliente[2] if cliente[2] is not None else "")),
                    QStandardItem(str(cliente[3] if cliente[3] is not None else "")),
                    QStandardItem(str(cliente[4] if cliente[4] is not None else "")),
                    QStandardItem(str(cliente[5] if cliente[5] is not None else ""))
                ]

                self.modelo.appendRow(linha)

            # Ajusta o tamanho das colunas
            self.tela.tableView.resizeColumnsToContents()

        except Exception as erro:

            print("ERRO AO CARREGAR CLIENTES:", erro)

            QMessageBox.critical(
                self.tela,
                "Erro",
                f"Erro ao carregar clientes:\n{erro}"
            )

        finally:

            if cursor is not None:
                cursor.close()

            if conexao is not None:
                conexao.close()

    # =========================================================
    # SALVAR / ALTERAR CLIENTE
    # =========================================================
    def salvar_cliente(self):
        print("Salvando Produtos")

        codigo = self.tela.edit_codigo.text().strip()
        nome = self.tela.edit_nome.text().strip()
        cpf = self.tela.edit_cpf.text().strip()
        telefone = self.tela.edit_telefone.text().strip()
        email = self.tela.edit_email.text().strip()
        cidade = self.tela.edit_cidade.text().strip()

        # =========================
        # VALIDAÇÃO
        # =========================

        if not nome:
            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Preencha o nome do cliente."
            )
            return

        if not cpf:
            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Preencha o CPF."
            )
            return

        if not telefone:
            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Preencha o telefone."
            )
            return

        if not email:
            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Preencha o email."
            )
            return

        if not cidade:
            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Preencha a cidade."
            )
            return

        conexao = None
        cursor = None

        try:

            conexao = conectar()
            cursor = conexao.cursor()

            # ========================================
            # SE TEM CÓDIGO -> ALTERA
            # ========================================
            if codigo:

                sql = """
                    UPDATE clientes
                    SET
                        nome = %s,
                        cpf = %s,
                        telefone = %s,
                        email = %s,
                        cidade = %s
                    WHERE id_clientes = %s
                """

                cursor.execute(
                    sql,
                    (
                        nome,
                        cpf,
                        telefone,
                        email,
                        cidade,
                        int(codigo)
                    )
                )

                mensagem = "Cliente atualizado com sucesso!"

            # ========================================
            # SE NÃO TEM CÓDIGO -> CADASTRA
            # ========================================
            else:

                sql = """
                    INSERT INTO clientes
                    (
                        nome,
                        cpf,
                        telefone,
                        email,
                        cidade
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                """

                cursor.execute(
                    sql,
                    (
                        nome,
                        cpf,
                        telefone,
                        email,
                        cidade
                    )
                )

                mensagem = "Cliente cadastrado com sucesso!"

            conexao.commit()

            QMessageBox.information(
                self.tela,
                "Sucesso",
                mensagem
            )

            # Limpa os campos
            self.limpar_campos()

            # Atualiza a tabela automaticamente
            self.carregar_dados_na_tabela()

        except Exception as erro:

            if conexao is not None:
                conexao.rollback()

            print("ERRO AO SALVAR:", erro)

            QMessageBox.critical(
                self.tela,
                "Erro",
                f"Não foi possível salvar o cliente:\n{erro}"
            )

        finally:

            if cursor is not None:
                cursor.close()

            if conexao is not None:
                conexao.close()

    # =========================================================
    # DUPLO CLIQUE NA TABELA
    # =========================================================
    def carregar_campos_ao_duplo_clique(self, index):

        linha = index.row()

        codigo = self.modelo.item(linha, 0)
        nome = self.modelo.item(linha, 1)
        cpf = self.modelo.item(linha, 2)
        telefone = self.modelo.item(linha, 3)
        email = self.modelo.item(linha, 4)
        cidade = self.modelo.item(linha, 5)

        self.tela.edit_codigo.setText(
            codigo.text() if codigo else ""
        )

        self.tela.edit_nome.setText(
            nome.text() if nome else ""
        )

        self.tela.edit_cpf.setText(
            cpf.text() if cpf else ""
        )

        self.tela.edit_telefone.setText(
            telefone.text() if telefone else ""
        )

        self.tela.edit_email.setText(
            email.text() if email else ""
        )

        self.tela.edit_cidade.setText(
            cidade.text() if cidade else ""
        )

    # =========================================================
    # EXCLUIR CLIENTE
    # =========================================================
    def excluir_cliente(self):

        codigo = self.tela.edit_codigo.text().strip()

        # Se não tiver código no campo,
        # tenta pegar da linha selecionada
        if not codigo:

            selecao = (
                self.tela.tableView
                .selectionModel()
                .selectedRows()
            )

            if not selecao:

                QMessageBox.warning(
                    self.tela,
                    "Aviso",
                    "Selecione um cliente na tabela."
                )

                return

            linha = selecao[0].row()

            item_codigo = self.modelo.item(
                linha,
                0
            )

            if item_codigo is None:
                return

            codigo = item_codigo.text()

        try:
            codigo = int(codigo)

        except ValueError:

            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Código inválido."
            )

            return

        # =========================
        # CONFIRMAÇÃO
        # =========================

        resposta = QMessageBox.question(
            self.tela,
            "Confirmar exclusão",
            f"Deseja realmente excluir o cliente de código {codigo}?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if resposta != QMessageBox.StandardButton.Yes:
            return

        conexao = None
        cursor = None

        try:

            conexao = conectar()
            cursor = conexao.cursor()

            sql = """
                DELETE FROM clientes
                WHERE id_clientes = %s
            """

            cursor.execute(
                sql,
                (codigo,)
            )

            conexao.commit()

            if cursor.rowcount == 0:

                QMessageBox.warning(
                    self.tela,
                    "Aviso",
                    "Cliente não encontrado."
                )

            else:

                QMessageBox.information(
                    self.tela,
                    "Sucesso",
                    "Cliente excluído com sucesso!"
                )

            self.limpar_campos()

            # Atualiza tabela
            self.carregar_dados_na_tabela()

        except Exception as erro:

            if conexao is not None:
                conexao.rollback()

            print("ERRO AO EXCLUIR:", erro)

            QMessageBox.critical(
                self.tela,
                "Erro",
                f"Não foi possível excluir o cliente:\n{erro}"
            )

        finally:

            if cursor is not None:
                cursor.close()

            if conexao is not None:
                conexao.close()

    # =========================================================
    # LIMPAR CAMPOS
    # =========================================================
    def limpar_campos(self):

        self.tela.edit_codigo.clear()
        self.tela.edit_nome.clear()
        self.tela.edit_cpf.clear()
        self.tela.edit_telefone.clear()
        self.tela.edit_email.clear()
        self.tela.edit_cidade.clear()

        self.tela.tableView.clearSelection()