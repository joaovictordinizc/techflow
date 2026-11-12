from decimal import Decimal

from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QMessageBox, QAbstractItemView

from utils.cnn import conectar


class GerenciadorVendas:

    def __init__(self, tela):
        self.tela = tela

        # =====================================================
        # CONFIGURAÇÃO DA TABELA DE VENDAS
        # =====================================================
        self.modelo = QStandardItemModel()

        self.modelo.setHorizontalHeaderLabels([
            "Código",
            "Cliente",
            "Produto",
            "Quantidade",
            "Valor total",
            "Data da venda"
        ])

        self.tela.tabela_vendas.setModel(self.modelo)

        self.tela.tabela_vendas.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.tela.tabela_vendas.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.tela.tabela_vendas.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        # =====================================================
        # CONEXÃO DOS BOTÕES
        # =====================================================
        self.tela.btn_registrar.clicked.connect(
            self.registrar_venda
        )

        self.tela.btn_limpar_2.clicked.connect(
            self.limpar_campos
        )

        self.tela.btn_cancelar.clicked.connect(
            self.limpar_campos
        )

        self.tela.btn_atualizar.clicked.connect(
            self.atualizar_dados
        )

        # =====================================================
        # EVENTOS DOS COMBOBOX
        # =====================================================
        self.tela.combo_produto.currentIndexChanged.connect(
            self.calcular_total
        )

        self.tela.combo_quantidade.currentIndexChanged.connect(
            self.calcular_total
        )

        # =====================================================
        # CARREGAMENTO INICIAL
        # =====================================================
        self.carregar_quantidades()
        self.carregar_clientes()
        self.carregar_produtos()
        self.carregar_vendas()
        self.calcular_total()

    # =========================================================
    # CARREGAR QUANTIDADES
    # =========================================================
    def carregar_quantidades(self):
        self.tela.combo_quantidade.clear()

        for quantidade in range(1, 101):
            self.tela.combo_quantidade.addItem(
                str(quantidade),
                quantidade
            )

        self.tela.combo_quantidade.setCurrentIndex(0)

    # =========================================================
    # CARREGAR CLIENTES
    # =========================================================
    def carregar_clientes(self):
        self.tela.combo_cliente.clear()

        conexao = None
        cursor = None

        try:
            conexao = conectar()
            cursor = conexao.cursor()

            cursor.execute("""
                SELECT
                    id_clientes,
                    nome
                FROM clientes
                ORDER BY nome
            """)

            clientes = cursor.fetchall()

            if not clientes:
                self.tela.combo_cliente.addItem(
                    "Nenhum cliente cadastrado",
                    None
                )
                return

            for cliente in clientes:
                id_cliente = cliente[0]
                nome_cliente = cliente[1]

                self.tela.combo_cliente.addItem(
                    str(nome_cliente),
                    id_cliente
                )

        except Exception as erro:
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
    # CARREGAR PRODUTOS NO COMBOBOX DE VENDAS
    # =========================================================
    def carregar_produtos(self):
        produto_selecionado = (
            self.tela.combo_produto.currentData()
        )

        id_selecionado = None

        if isinstance(produto_selecionado, dict):
            id_selecionado = produto_selecionado.get("id")

        self.tela.combo_produto.blockSignals(True)
        self.tela.combo_produto.clear()

        conexao = None
        cursor = None

        try:
            conexao = conectar()
            cursor = conexao.cursor()

            cursor.execute("""
                SELECT
                    id_codigo,
                    nome,
                    preco,
                    quantidade
                FROM produtos
                ORDER BY nome
            """)

            produtos = cursor.fetchall()

            if not produtos:
                self.tela.combo_produto.addItem(
                    "Nenhum produto cadastrado",
                    None
                )
                return

            indice_selecionado = 0

            for indice, produto in enumerate(produtos):
                id_produto = produto[0]
                nome_produto = produto[1]
                preco_produto = produto[2]
                estoque_produto = produto[3]

                if preco_produto is None:
                    preco_produto = Decimal("0.00")
                else:
                    preco_produto = Decimal(
                        str(preco_produto)
                    )

                if estoque_produto is None:
                    estoque_produto = 0
                else:
                    estoque_produto = int(
                        estoque_produto
                    )

                preco_formatado = self.formatar_valor(
                    preco_produto
                )

                texto_produto = (
                    f"{nome_produto} - "
                    f"R$ {preco_formatado} - "
                    f"Estoque: {estoque_produto}"
                )

                dados_produto = {
                    "id": id_produto,
                    "nome": nome_produto,
                    "preco": preco_produto,
                    "estoque": estoque_produto
                }

                self.tela.combo_produto.addItem(
                    texto_produto,
                    dados_produto
                )

                if id_produto == id_selecionado:
                    indice_selecionado = indice

            self.tela.combo_produto.setCurrentIndex(
                indice_selecionado
            )

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

            self.tela.combo_produto.blockSignals(False)
            self.calcular_total()

    # =========================================================
    # CALCULAR O VALOR TOTAL
    # =========================================================
    def calcular_total(self):
        dados_produto = (
            self.tela.combo_produto.currentData()
        )

        quantidade = (
            self.tela.combo_quantidade.currentData()
        )

        if not isinstance(dados_produto, dict):
            self.tela.lbl_valor_total.setText(
                "R$ 0,00"
            )
            return

        if quantidade is None:
            self.tela.lbl_valor_total.setText(
                "R$ 0,00"
            )
            return

        preco = Decimal(
            str(dados_produto["preco"])
        )

        quantidade = int(quantidade)
        valor_total = preco * quantidade

        valor_formatado = self.formatar_valor(
            valor_total
        )

        self.tela.lbl_valor_total.setText(
            f"R$ {valor_formatado}"
        )

    # =========================================================
    # REGISTRAR VENDA E DESCONTAR O ESTOQUE
    # =========================================================
    def registrar_venda(self):
        id_cliente = (
            self.tela.combo_cliente.currentData()
        )

        dados_produto = (
            self.tela.combo_produto.currentData()
        )

        quantidade = (
            self.tela.combo_quantidade.currentData()
        )

        if id_cliente is None:
            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Selecione um cliente válido."
            )
            return

        if not isinstance(dados_produto, dict):
            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Selecione um produto válido."
            )
            return

        if quantidade is None:
            QMessageBox.warning(
                self.tela,
                "Aviso",
                "Selecione uma quantidade."
            )
            return

        id_produto = dados_produto["id"]
        nome_produto = dados_produto["nome"]

        preco_produto = Decimal(
            str(dados_produto["preco"])
        )

        quantidade = int(quantidade)

        if quantidade <= 0:
            QMessageBox.warning(
                self.tela,
                "Aviso",
                "A quantidade deve ser maior que zero."
            )
            return

        conexao = None
        cursor = None

        try:
            conexao = conectar()
            cursor = conexao.cursor()

            # Consulta o estoque atual e bloqueia o produto.
            cursor.execute(
                """
                SELECT quantidade
                FROM produtos
                WHERE id_codigo = %s
                FOR UPDATE
                """,
                (id_produto,)
            )

            produto = cursor.fetchone()

            if produto is None:
                conexao.rollback()

                QMessageBox.warning(
                    self.tela,
                    "Aviso",
                    "O produto selecionado não foi encontrado."
                )
                return

            estoque_atual = produto[0]

            if estoque_atual is None:
                estoque_atual = 0
            else:
                estoque_atual = int(estoque_atual)

            if estoque_atual < quantidade:
                conexao.rollback()

                QMessageBox.warning(
                    self.tela,
                    "Estoque insuficiente",
                    (
                        f"O produto {nome_produto} possui "
                        f"somente {estoque_atual} unidade(s) "
                        "em estoque."
                    )
                )
                return

            valor_total = preco_produto * quantidade

            # Registra a venda.
            cursor.execute(
                """
                INSERT INTO vendas (
                    id_clientes,
                    id_codigo,
                    quantidade,
                    valor_total,
                    data_venda
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    NOW()
                )
                """,
                (
                    id_cliente,
                    id_produto,
                    quantidade,
                    valor_total
                )
            )

            # Desconta a quantidade vendida do estoque.
            cursor.execute(
                """
                UPDATE produtos
                SET quantidade = quantidade - %s
                WHERE id_codigo = %s
                  AND quantidade >= %s
                """,
                (
                    quantidade,
                    id_produto,
                    quantidade
                )
            )

            if cursor.rowcount == 0:
                conexao.rollback()

                QMessageBox.warning(
                    self.tela,
                    "Estoque insuficiente",
                    (
                        "Não foi possível descontar a "
                        "quantidade do estoque."
                    )
                )
                return

            conexao.commit()

            # Atualiza as informações da tela após a venda.
            self.carregar_produtos()
            self.carregar_vendas()
            self.atualizar_tabela_produtos()
            self.limpar_campos()

            QMessageBox.information(
                self.tela,
                "Sucesso",
                (
                    "Venda registrada e estoque "
                    "atualizado com sucesso!"
                )
            )

        except Exception as erro:
            if conexao is not None:
                conexao.rollback()

            QMessageBox.critical(
                self.tela,
                "Erro",
                (
                    "Não foi possível registrar "
                    f"a venda:\n{erro}"
                )
            )

        finally:
            if cursor is not None:
                cursor.close()

            if conexao is not None:
                conexao.close()

    # =========================================================
    # ATUALIZAR A TABELA DA JANELA DE PRODUTOS
    # =========================================================
    def atualizar_tabela_produtos(self):
        metodos_possiveis = [
            "carregar_dados_na_tabela",
            "carregar_produtos",
            "listar_produtos",
            "buscar_produtos",
            "atualizar_tabela"
        ]

        nomes_possiveis = [
            "gerenciador_produtos",
            "gerenciador_produto",
            "produtos",
            "produto"
        ]

        for nome_objeto in nomes_possiveis:
            objeto = getattr(
                self.tela,
                nome_objeto,
                None
            )

            if objeto is None:
                continue

            for nome_metodo in metodos_possiveis:
                metodo = getattr(
                    objeto,
                    nome_metodo,
                    None
                )

                if callable(metodo):
                    try:
                        metodo()

                        print(
                            "Tabela de produtos atualizada:",
                            nome_objeto,
                            nome_metodo
                        )

                        return True

                    except Exception as erro:
                        print(
                            "Erro ao atualizar produtos:",
                            erro
                        )

        for nome_objeto, objeto in vars(
            self.tela
        ).items():

            if objeto is self:
                continue

            for nome_metodo in metodos_possiveis:
                metodo = getattr(
                    objeto,
                    nome_metodo,
                    None
                )

                if callable(metodo):
                    try:
                        metodo()

                        print(
                            "Tabela de produtos atualizada:",
                            nome_objeto,
                            nome_metodo
                        )

                        return True

                    except Exception as erro:
                        print(
                            "Erro ao atualizar produtos:",
                            erro
                        )

        print(
            "Não encontrei o gerenciador da tabela de produtos."
        )

        return False

    # =========================================================
    # CARREGAR O HISTÓRICO DE VENDAS
    # =========================================================
    def carregar_vendas(self):
        self.modelo.removeRows(
            0,
            self.modelo.rowCount()
        )

        conexao = None
        cursor = None

        try:
            conexao = conectar()
            cursor = conexao.cursor()

            cursor.execute("""
                SELECT
                    v.id_vendas,
                    c.nome,
                    p.nome,
                    v.quantidade,
                    v.valor_total,
                    v.data_venda
                FROM vendas AS v
                INNER JOIN clientes AS c
                    ON c.id_clientes = v.id_clientes
                INNER JOIN produtos AS p
                    ON p.id_codigo = v.id_codigo
                ORDER BY v.id_vendas DESC
            """)

            vendas = cursor.fetchall()

            for venda in vendas:
                id_venda = venda[0]
                nome_cliente = venda[1]
                nome_produto = venda[2]
                quantidade = venda[3]
                valor_total = venda[4]
                data_venda = venda[5]

                if valor_total is None:
                    valor_total = Decimal("0.00")
                else:
                    valor_total = Decimal(
                        str(valor_total)
                    )

                if data_venda is None:
                    data_formatada = ""

                elif hasattr(data_venda, "strftime"):
                    data_formatada = data_venda.strftime(
                        "%d/%m/%Y %H:%M"
                    )

                else:
                    data_formatada = str(data_venda)

                linha = [
                    QStandardItem(str(id_venda)),
                    QStandardItem(str(nome_cliente)),
                    QStandardItem(str(nome_produto)),
                    QStandardItem(str(quantidade)),
                    QStandardItem(
                        f"R$ {self.formatar_valor(valor_total)}"
                    ),
                    QStandardItem(data_formatada)
                ]

                self.modelo.appendRow(linha)

            self.tela.tabela_vendas.resizeColumnsToContents()

        except Exception as erro:
            QMessageBox.critical(
                self.tela,
                "Erro",
                (
                    "Erro ao carregar o histórico "
                    f"de vendas:\n{erro}"
                )
            )

        finally:
            if cursor is not None:
                cursor.close()

            if conexao is not None:
                conexao.close()

    # =========================================================
    # ATUALIZAR CLIENTES, PRODUTOS E VENDAS
    # =========================================================
    def atualizar_dados(self):
        self.carregar_clientes()
        self.carregar_produtos()
        self.carregar_vendas()
        self.calcular_total()

        QMessageBox.information(
            self.tela,
            "Sucesso",
            "Dados atualizados com sucesso!"
        )

    # =========================================================
    # LIMPAR OS CAMPOS
    # =========================================================
    def limpar_campos(self):
        if self.tela.combo_cliente.count() > 0:
            self.tela.combo_cliente.setCurrentIndex(0)

        if self.tela.combo_produto.count() > 0:
            self.tela.combo_produto.setCurrentIndex(0)

        if self.tela.combo_quantidade.count() > 0:
            self.tela.combo_quantidade.setCurrentIndex(0)

        self.tela.tabela_vendas.clearSelection()
        self.calcular_total()

    # =========================================================
    # FORMATAR VALOR EM REAL
    # =========================================================
    def formatar_valor(self, valor):
        valor = Decimal(str(valor))

        return (
            f"{valor:,.2f}"
            .replace(",", "TEMP")
            .replace(".", ",")
            .replace("TEMP", ".")
        )