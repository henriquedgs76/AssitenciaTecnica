import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QHeaderView
from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtGui import QFont
import sys

class ControleAssistencia:
    def __init__(self, nome_banco='controle_assistencia.db'):
        self.nome_banco = nome_banco
        self._conectar()
        self.criar_tabelas()

    def _conectar(self):
        try:
            self.conn = sqlite3.connect(self.nome_banco)
            self.conn.execute('PRAGMA foreign_keys = ON')
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def _desconectar(self):
        try:
            self.conn.close()
        except sqlite3.Error as e:
            print(f"Erro ao fechar a conexão: {e}")

    def _executar_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Erro na execução da query: {e}")

    def criar_tabelas(self):
        self._executar_query('''
            CREATE TABLE IF NOT EXISTS estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto TEXT NOT NULL,
                marca TEXT NOT NULL,
                modelo TEXT NOT NULL,
                quantidade INTEGER NOT NULL
            )
        ''')

        self._executar_query('''
            CREATE TABLE IF NOT EXISTS ordens_servico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT NOT NULL,
                marca TEXT NOT NULL,
                modelo_computador TEXT NOT NULL,
                descricao_problema TEXT,
                data_entrada DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_conclusao DATETIME,
                status TEXT DEFAULT 'Em andamento'
            )
        ''')

    def adicionar_produto(self, produto, marca, modelo, quantidade):
        try:
            quantidade = int(quantidade)
        except ValueError:
            print('A quantidade deve ser um número inteiro.')
            return

        try:
            self._executar_query('INSERT INTO estoque (produto, marca, modelo, quantidade) VALUES (?, ?, ?, ?)', (produto, marca, modelo, quantidade))
            print(f"Produto '{produto}' adicionado ao estoque.")
        except sqlite3.Error as e:
            print(f"Erro ao adicionar produto: {e}")

    def listar_estoque(self):
        try:
            self.cursor.execute('SELECT * FROM estoque')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao listar estoque: {e}")
            return []

    def criar_ordem_servico(self, cliente, marca, modelo_computador, descricao_problema):
        try:
            self._executar_query('''
                INSERT INTO ordens_servico (cliente, marca, modelo_computador, descricao_problema)
                VALUES (?, ?, ?, ?)
            ''', (cliente, marca, modelo_computador, descricao_problema))
            print(f"Ordem de serviço para '{cliente}' criada.")
        except sqlite3.Error as e:
            print(f"Erro ao criar ordem de serviço: {e}")

    def listar_ordens_servico(self):
        try:
            self.cursor.execute('SELECT * FROM ordens_servico')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao listar ordens de serviço: {e}")
            return []

    def marcar_ordem_concluida(self, id_ordem):
        try:
            data_atual = QDate.currentDate()
            data_conclusao = QDateTime(data_atual)
            self._executar_query('UPDATE ordens_servico SET status = "Concluída", data_conclusao = ? WHERE id = ?', (data_conclusao.toString(Qt.ISODate), id_ordem))
        except sqlite3.Error as e:
            print(f"Erro ao marcar ordem como concluída: {e}")

    def excluir_ordem_servico(self, id_ordem):
        try:
            self._executar_query('DELETE FROM ordens_servico WHERE id = ?', (id_ordem,))
        except sqlite3.Error as e:
            print(f"Erro ao excluir ordem de serviço: {e}")

class ControleAssistenciaGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Assistência Técnica Henrique')
        self.setGeometry(100, 100, 800, 600)

        self.controle_assistencia = ControleAssistencia()

        self.init_ui()

    def init_ui(self):
        titulo_label = QLabel('Assistência Técnica Henrique', self)
        titulo_label.setAlignment(Qt.AlignCenter)
        titulo_font = QFont("Arial", 16, QFont.Bold)
        titulo_label.setFont(titulo_font)

        self.entry_cliente = QLineEdit(self)
        self.entry_cliente.setPlaceholderText('Cliente')

        self.entry_marca = QLineEdit(self)
        self.entry_marca.setPlaceholderText('Marca')

        self.entry_modelo = QLineEdit(self)
        self.entry_modelo.setPlaceholderText('Modelo do Computador')

        self.entry_descricao = QLineEdit(self)
        self.entry_descricao.setPlaceholderText('Descrição do Problema')

        self.entry_quantidade = QLineEdit(self)
        self.entry_quantidade.setPlaceholderText('Quantidade')

        botoes_layout = QHBoxLayout()
        botoes_layout.setAlignment(Qt.AlignCenter)

        btn_adicionar_produto = QPushButton('Adicionar Produto')
        btn_adicionar_produto.clicked.connect(self.adicionar_produto)

        btn_listar_estoque = QPushButton('Listar Estoque')
        btn_listar_estoque.clicked.connect(self.listar_estoque)

        btn_criar_ordem = QPushButton('Criar Ordem de Serviço')
        btn_criar_ordem.clicked.connect(self.criar_ordem_servico)

        btn_listar_ordens = QPushButton('Listar Ordens de Serviço')
        btn_listar_ordens.clicked.connect(self.listar_ordens_servico)

        botoes_layout.addWidget(btn_adicionar_produto)
        botoes_layout.addWidget(btn_listar_estoque)
        botoes_layout.addWidget(btn_criar_ordem)
        botoes_layout.addWidget(btn_listar_ordens)

        self.table_ordens_servico = QTableWidget(self)
        self.table_ordens_servico.setColumnCount(9)
        self.table_ordens_servico.setHorizontalHeaderLabels(['ID', 'Cliente', 'Marca', 'Modelo', 'Descrição', 'Data Entrada', 'Data Conclusão', 'Status', 'Excluir'])
        self.table_ordens_servico.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout_principal = QVBoxLayout()
        layout_principal.addWidget(titulo_label)
        layout_principal.addWidget(self.entry_cliente)
        layout_principal.addWidget(self.entry_marca)
        layout_principal.addWidget(self.entry_modelo)
        layout_principal.addWidget(self.entry_descricao)
        layout_principal.addWidget(self.entry_quantidade)
        layout_principal.addLayout(botoes_layout)
        layout_principal.addWidget(self.table_ordens_servico)

        self.setLayout(layout_principal)

        self.listar_ordens_servico()

    def adicionar_produto(self):
        produto = self.entry_cliente.text()
        marca = self.entry_marca.text()
        modelo = self.entry_modelo.text()
        quantidade = self.entry_quantidade.text()

        if produto and marca and modelo and quantidade:
            self.controle_assistencia.adicionar_produto(produto, marca, modelo, int(quantidade))
            QMessageBox.information(self, 'Sucesso', f"Produto '{produto}' adicionado ao estoque.")
        else:
            QMessageBox.critical(self, 'Erro', 'Por favor, preencha todos os campos.')

    def listar_estoque(self):
        estoque = self.controle_assistencia.listar_estoque()
        if estoque:
            for item in estoque:
                print(item)
        else:
            print("Estoque vazio.")

    def criar_ordem_servico(self):
        cliente = self.entry_cliente.text()
        marca = self.entry_marca.text()
        modelo = self.entry_modelo.text()
        descricao = self.entry_descricao.text()

        if cliente and marca and modelo and descricao:
            self.controle_assistencia.criar_ordem_servico(cliente, marca, modelo, descricao)
            QMessageBox.information(self, 'Sucesso', f"Ordem de serviço para '{cliente}' criada.")
            self.listar_ordens_servico()
        else:
            QMessageBox.critical(self, 'Erro', 'Por favor, preencha todos os campos.')

    def listar_ordens_servico(self):
        ordens_servico = self.controle_assistencia.listar_ordens_servico()
        self.table_ordens_servico.setRowCount(0)

        for row, ordem in enumerate(ordens_servico):
            self.table_ordens_servico.insertRow(row)
            for col, value in enumerate(ordem):
                self.table_ordens_servico.setItem(row, col, QTableWidgetItem(str(value)))

            btn_excluir = QPushButton('Excluir')
            btn_excluir.clicked.connect(lambda _, row=row: self.excluir_ordem_servico(row))
            self.table_ordens_servico.setCellWidget(row, len(ordem), btn_excluir)

    def excluir_ordem_servico(self, row):
        id_ordem = self.table_ordens_servico.item(row, 0).text()
        confirmacao = QMessageBox.question(self, 'Excluir Ordem de Serviço', f'Deseja realmente excluir a Ordem de Serviço {id_ordem}?',
                                           QMessageBox.Yes | QMessageBox.No)

        if confirmacao == QMessageBox.Yes:
            self.controle_assistencia.excluir_ordem_servico(int(id_ordem))
            QMessageBox.information(self, 'Sucesso', f'Ordem de Serviço {id_ordem} excluída com sucesso.')
            self.listar_ordens_servico()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ControleAssistenciaGUI()
    ex.show()
    sys.exit(app.exec_())
