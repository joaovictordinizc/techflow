from decimal import Decimal, InvalidOperation

from PyQt6.QtGui import (
    QIntValidator,
    QStandardItem,
    QStandardItemModel
)

from PyQt6.QtWidgets import (
    QMessageBox,
    QAbstractItemView
)

from utils.cnn import conectar


class GerenciadorProdutos:
    """
    Controla o CRUD da tabela produtos na tela do dashboard.
    """

    def __init__(self, tela):
        self.tela = tela

        # O código será gerado pelo banco de dados.
        self.tela.cod_produto.setReadOnly(True)

        # Campo quantidade aceita somente números inteiros positivos.
        self.tela.estoque_produto.setValidator(
            QIntValidator(0, 999999999, self.tela)
        )

        # Criação do modelo usado pela tabela.
        self.modelo = QStandardItemModel()

        self.modelo.setHorizontalHeaderLabels(
            [
                "Código",
                "Nome",
                "Descrição",
                "Categoria",
                "Preço",
                "Quantidade"
            ]
        )

        # Coloca o modelo dentro da tabela.
        self.tela.tabela_produto.setModel(self.modelo)

        # A seleção será feita pela linha completa.
        self.tela.tabela_produto.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        # Permite selecionar apenas uma linha.
        self.tela.tabela_produto.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        # Impede edição diretamente na tabela.
        self.tela.tabela_produto.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        # Conexão dos botões com os métodos.
        self.tela.btn_salvar_produto.clicked.connect(
            self.salvar_produto
        )

        self.tela.btn_limpar_produto.clicked.connect(
            self.limpar_campos
        )

        self.tela.btn_excluir_produto.clicked.connect(
            self.excluir_produto
        )

        # Duplo clique em uma linha carrega o produto nos campos.
        self.tela.tabela_produto.doubleClicked.connect(
            self.carregar_campos_ao_duplo_clique
        )

        # Carrega os produtos ao abrir a tela.
        self.carregar_dados_na_tabela()

    def carregar_dados_na_tabela(self):
        """
        Busca todos os produtos no banco de dados e exibe
        os produtos na tabela.
        """

        # Limpa as linhas existentes antes de carregar novamente.
        self.modelo.removeRows(
            0,
            self.modelo.rowCount()
        )

        conexao = None
        cursor = None

        try:
            conexao = conectar()
            cursor = conexao.cursor()

            comando_sql = """
                SELECT
                    id_codigo,
                    nome,
                    descricao,
                    categoria,
                    preco,
                    quantidade
                FROM produtos
                ORDER BY id_codigo
            """

            cursor.execute(comando_sql)

            produtos = cursor.fetchall()

            for produto in produtos:
                codigo = produto[0]
                nome = produto[1]
                descricao = produto[2]
                categoria = produto[3]
                preco = produto[4]
                quantidade = produto[5]

                if preco is None:
                    preco_formatado = ""
                else:
                    preco_formatado = f"{Decimal(str(preco)):.2f}"

                linha = [
                    QStandardItem(
                        "" if codigo is None else str(codigo)
                    ),
                    QStandardItem(
                        "" if nome is None else str(nome)
                    ),
                    QStandardItem(
                        "" if descricao is None else str(descricao)
                    ),
                    QStandardItem(
                        "" if categoria is None else str(categoria)
                    ),
                    QStandardItem(preco_formatado),
                    QStandardItem(
                        "" if quantidade is None else str(quantidade)
                    )
                ]

                self.modelo.appendRow(linha)

            # Ajusta automaticamente o tamanho das colunas.
            self.tela.tabela_produto.resizeColumnsToContents()

        except Exception as erro:
            QMessageBox.critical(
                self.tela,
                "Erro",
                f"Erro ao carregar produtos:\n{erro}"
            )

        finally:
            if cursor is not None:
                cursor.close()

            if conexao is not None:
                conexao.close()

    def salvar_produto(self):
        """
        Cadastra um produto novo ou altera um produto existente.

        Campo código vazio:
        realiza INSERT.

        Campo código preenchido:
        realiza UPDATE.
        """

        codigo = self.tela.cod_produto.text().strip()
        nome = self.tela.nome_produto.text().strip()
        descricao = self.tela.decr_produto.text().strip()

        # Pega a categoria selecionada no QComboBox.
        categoria = (
            self.tela.categoria_produto
            .currentText()
            .strip()
        )

        preco_texto = (
            self.tela.preco_produto
            .text()
            .strip()
            .replace("R$", "")
            .strip()
        )

        quantidade_texto = (
            self.tela.estoque_produto
            .text()
            .strip()
        )

        # Validação do nome.
        if not nome:
            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Preencha o nome do produto."
            )
            return

        # Validação da descrição.
        if not descricao:
            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Preencha a descrição do produto."
            )
            return

        # Validação da categoria.
        if not categoria:
            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Selecione a categoria do produto."
            )
            return

        # Validação do preço.
        if not preco_texto:
            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Preencha o preço do produto."
            )
            return

        # Validação da quantidade.
        if not quantidade_texto:
            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Preencha a quantidade do produto."
            )
            return

        try:
            # Permite informar:
            # 15,90
            # 15.90
            # 1.500,90

            if "," in preco_texto:
                preco_texto = preco_texto.replace(".", "")
                preco_texto = preco_texto.replace(",", ".")

            preco = Decimal(preco_texto)
            quantidade = int(quantidade_texto)

            if preco < 0:
                QMessageBox.warning(
                    self.tela,
                    "Aviso",
                    "O preço não pode ser negativo."
                )
                return

            if quantidade < 0:
                QMessageBox.warning(
                    self.tela,
                    "Aviso",
                    "A quantidade não pode ser negativa."
                )
                return

        except InvalidOperation:
            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Informe um preço válido."
            )
            return

        except ValueError:
            QMessageBox.warning(
                self.tela,
                "Aviso",
                "A quantidade deve ser um número inteiro."
            )
            return

        conexao = None
        cursor = None

        try:
            conexao = conectar()
            cursor = conexao.cursor()

            # Se há código, altera o produto existente.
            if codigo:
                comando_sql = """
                    UPDATE produtos
                    SET
                        nome = %s,
                        descricao = %s,
                        categoria = %s,
                        preco = %s,
                        quantidade = %s
                    WHERE id_codigo = %s
                """

                valores = (
                    nome,
                    descricao,
                    categoria,
                    preco,
                    quantidade,
                    int(codigo)
                )

                cursor.execute(
                    comando_sql,
                    valores
                )

                # Verifica se algum produto foi encontrado.
                if cursor.rowcount == 0:
                    QMessageBox.warning(
                        self.tela,
                        "Aviso",
                        (
                            "Nenhum produto foi alterado. "
                            "Verifique se o código existe."
                        )
                    )

                    conexao.rollback()
                    return

                mensagem = "Produto atualizado com sucesso!"

            # Se não há código, cadastra um novo produto.
            else:
                comando_sql = """
                    INSERT INTO produtos (
                        nome,
                        descricao,
                        categoria,
                        preco,
                        quantidade
                    )
                    VALUES (%s, %s, %s, %s, %s)
                """

                valores = (
                    nome,
                    descricao,
                    categoria,
                    preco,
                    quantidade
                )

                cursor.execute(
                    comando_sql,
                    valores
                )

                mensagem = "Produto cadastrado com sucesso!"

            conexao.commit()

            QMessageBox.information(
                self.tela,
                "Sucesso",
                mensagem
            )

            self.limpar_campos()
            self.carregar_dados_na_tabela()

        except Exception as erro:
            if conexao is not None:
                conexao.rollback()

            QMessageBox.critical(
                self.tela,
                "Erro",
                f"Não foi possível salvar o produto:\n{erro}"
            )

        finally:
            if cursor is not None:
                cursor.close()

            if conexao is not None:
                conexao.close()

    def carregar_campos_ao_duplo_clique(self, index):
        """
        Carrega os dados da linha nos campos ao dar dois
        cliques em um produto.
        """

        linha = index.row()

        item_codigo = self.modelo.item(linha, 0)
        item_nome = self.modelo.item(linha, 1)
        item_descricao = self.modelo.item(linha, 2)
        item_categoria = self.modelo.item(linha, 3)
        item_preco = self.modelo.item(linha, 4)
        item_quantidade = self.modelo.item(linha, 5)

        if item_codigo is not None:
            self.tela.cod_produto.setText(
                item_codigo.text()
            )

        if item_nome is not None:
            self.tela.nome_produto.setText(
                item_nome.text()
            )

        if item_descricao is not None:
            self.tela.decr_produto.setText(
                item_descricao.text()
            )

        if item_categoria is not None:
            categoria = item_categoria.text()

            indice_categoria = (
                self.tela.categoria_produto.findText(
                    categoria
                )
            )

            if indice_categoria >= 0:
                self.tela.categoria_produto.setCurrentIndex(
                    indice_categoria
                )

        if item_preco is not None:
            self.tela.preco_produto.setText(
                item_preco.text()
            )

        if item_quantidade is not None:
            self.tela.estoque_produto.setText(
                item_quantidade.text()
            )

    def excluir_produto(self):
        """
        Exclui o produto carregado nos campos ou selecionado
        diretamente na tabela.
        """

        codigo = self.tela.cod_produto.text().strip()

        # Se o código estiver vazio, tenta pegar da linha selecionada.
        if not codigo:
            selecao = (
                self.tela
                .tabela_produto
                .selectionModel()
                .selectedRows()
            )

            if not selecao:
                QMessageBox.warning(
                    self.tela,
                    "Aviso",
                    "Selecione um produto na tabela."
                )
                return

            linha = selecao[0].row()
            item_codigo = self.modelo.item(linha, 0)

            if item_codigo is not None:
                codigo = item_codigo.text()

        try:
            codigo = int(codigo)

        except ValueError:
            QMessageBox.warning(
                self.tela,
                "Aviso",
                "O código do produto é inválido."
            )
            return

        resposta = QMessageBox.question(
            self.tela,
            "Confirmar exclusão",
            (
                "Deseja realmente excluir o produto "
                f"de código {codigo}?"
            ),
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No
        )

        if resposta != QMessageBox.StandardButton.Yes:
            return

        conexao = None
        cursor = None

        try:
            conexao = conectar()
            cursor = conexao.cursor()

            comando_sql = """
                DELETE FROM produtos
                WHERE id_codigo = %s
            """

            cursor.execute(
                comando_sql,
                (codigo,)
            )

            # Verifica antes do commit se algum registro foi excluído.
            if cursor.rowcount == 0:
                conexao.rollback()

                QMessageBox.warning(
                    self.tela,
                    "Aviso",
                    "Produto não encontrado."
                )
                return

            conexao.commit()

            QMessageBox.information(
                self.tela,
                "Sucesso",
                "Produto excluído com sucesso!"
            )

            self.limpar_campos()
            self.carregar_dados_na_tabela()

        except Exception as erro:
            if conexao is not None:
                conexao.rollback()

            QMessageBox.critical(
                self.tela,
                "Erro",
                f"Não foi possível excluir o produto:\n{erro}"
            )

        finally:
            if cursor is not None:
                cursor.close()

            if conexao is not None:
                conexao.close()

    def limpar_campos(self):
        """
        Limpa todos os campos do cadastro de produtos.
        """

        self.tela.cod_produto.clear()
        self.tela.nome_produto.clear()
        self.tela.decr_produto.clear()
        self.tela.preco_produto.clear()
        self.tela.estoque_produto.clear()

        # Volta para a primeira categoria.
        self.tela.categoria_produto.setCurrentIndex(0)

        # Remove a seleção da tabela.
        self.tela.tabela_produto.clearSelection()

        # Coloca o cursor no campo nome.
        self.tela.nome_produto.setFocus()