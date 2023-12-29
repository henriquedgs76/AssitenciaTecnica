import mysql.connector
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QListWidget, QListWidgetItem
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QDate, QDateTime
import sys

class DBHelper:
    def __init__(self, host='localhost', user='root', password='', database='controle_assistencia'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self._conectar()

    def _conectar(self):
        try:
            self.conn = mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def _executar_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
        except mysql.connector.Error as e:
            print(f"Erro na execução da query: {e}")

class ControleEstoque(DBHelper):
    def __init__(self):
        super().__init__()
        self.criar_tabela_estoque()

    def criar_tabela_estoque(self):
        self._executar_query('''
            CREATE TABLE IF NOT EXISTS estoque (
                id INT AUTO_INCREMENT PRIMARY KEY,
                produto VARCHAR(255) NOT NULL,
                marca VARCHAR(255) NOT NULL,
                modelo VARCHAR(255) NOT NULL,
                quantidade INT NOT NULL
            )
        ''')

    def adicionar_produto(self, produto, marca, modelo, quantidade):
        try:
            quantidade = int(quantidade)
        except ValueError:
            print('A quantidade deve ser um número inteiro.')
            return

        try:
            self._executar_query('INSERT INTO estoque (produto, marca, modelo, quantidade) VALUES (%s, %s, %s, %s)', (produto, marca, modelo, quantidade))
            print(f"Produto '{produto}' adicionado ao estoque.")
        except mysql.connector.Error as e:
            print(f"Erro ao adicionar produto: {e}")

    def listar_estoque(self):
        try:
            self.cursor.execute('SELECT * FROM estoque')
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Erro ao listar estoque: {e}")
            return []

class ControleOrdensServico(DBHelper):
    def __init__(self):
        super().__init__()
        self.criar_tabela_ordens_servico()

    def criar_tabela_ordens_servico(self):
        self._executar_query('''
            CREATE TABLE IF NOT EXISTS ordens_servico (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cliente VARCHAR(255) NOT NULL,
                marca VARCHAR(255) NOT NULL,
                modelo_computador VARCHAR(255) NOT NULL,
                descricao_problema TEXT,
                data_entrada DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_conclusao DATETIME,
                status VARCHAR(255) DEFAULT 'Em andamento'
            )
        ''')

    def criar_ordem_servico(self, cliente, marca, modelo_computador, descricao_problema):
        try:
            self._executar_query('''
                INSERT INTO ordens_servico (cliente, marca, modelo_computador, descricao_problema)
                VALUES (%s, %s, %s, %s)
            ''', (cliente, marca, modelo_computador, descricao_problema))
            print(f"Ordem de serviço para '{cliente}' criada.")
        except mysql.connector.Error as e:
            print(f"Erro ao criar ordem de serviço: {e}")

    def listar_ordens_servico(self):
        try:
            self.cursor.execute('SELECT * FROM ordens_servico')
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Erro ao listar ordens de serviço: {e}")
            return []

    def marcar_ordem_concluida(self, id_ordem):
        try:
            data_atual = QDate.currentDate()
            data_conclusao = QDateTime(data_atual)
            self._executar_query('UPDATE ordens_servico SET status = "Concluída", data_conclusao = %s WHERE id = %s', (data_conclusao.toString(Qt.ISODate), id_ordem))
        except mysql.connector.Error as e:
            print(f"Erro ao marcar ordem como concluída: {e}")

    def excluir_ordem_servico(self, id_ordem):
        try:
            self._executar_query('DELETE FROM ordens_servico WHERE id = %s', (id_ordem,))
        except mysql.connector.Error as e:
            print(f"Erro ao excluir ordem de serviço: {e}")

class ControleAssistenciaGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Assistência Técnica Henrique')
        self.setGeometry(100, 100, 800, 600)

        self.controle_estoque = ControleEstoque()
        self.controle_ordens_servico = ControleOrdensServico()

        self.init_ui()

    def init_ui(self):
        # Mensagem de boas-vindas
        mensagem_boas_vindas = QLabel("Assistência Técnica Henrique 2024")
        fonte = QFont()
        fonte.setPointSize(25)
        mensagem_boas_vindas.setFont(fonte)
        mensagem_boas_vindas.setAlignment(Qt.AlignCenter)

        # Campos de entrada para adicionar produto
        self.produto_input = QLineEdit(self)
        self.produto_input.setPlaceholderText('Nome do Produto')

        self.marca_input = QLineEdit(self)
        self.marca_input.setPlaceholderText('Marca')

        self.modelo_input = QLineEdit(self)
        self.modelo_input.setPlaceholderText('Modelo')

        self.quantidade_input = QLineEdit(self)
        self.quantidade_input.setPlaceholderText('Quantidade')

        # Botão para adicionar produto
        botao_adicionar_produto = QPushButton('Adicionar Produto', self)
        botao_adicionar_produto.clicked.connect(self.adicionar_produto)

        # Lista para exibição de dados do estoque
        lista_estoque = QListWidget()

        # Campos de entrada e botão para criar ordem de serviço
        self.cliente_input = QLineEdit(self)
        self.cliente_input.setPlaceholderText('Nome do Cliente')

        self.marca_os_input = QLineEdit(self)
        self.marca_os_input.setPlaceholderText('Marca do Computador')

        self.modelo_os_input = QLineEdit(self)
        self.modelo_os_input.setPlaceholderText('Modelo do Computador')

        self.descricao_os_input = QLineEdit(self)
        self.descricao_os_input.setPlaceholderText('Descrição do Problema')

        # Botão para criar ordem de serviço
        botao_criar_ordem_servico = QPushButton('Criar Ordem de Serviço', self)
        botao_criar_ordem_servico.clicked.connect(self.criar_ordem_servico)

        # Lista para exibição de dados das ordens de serviço
        lista_ordens_servico = QListWidget()

        # Layout principal
        layout_principal = QVBoxLayout(self)
        layout_principal.addWidget(mensagem_boas_vindas)

        # Adiciona campos de entrada e botão para adicionar produto
        layout_principal.addWidget(self.produto_input)
        layout_principal.addWidget(self.marca_input)
        layout_principal.addWidget(self.modelo_input)
        layout_principal.addWidget(self.quantidade_input)
        layout_principal.addWidget(botao_adicionar_produto)
        layout_principal.addWidget(lista_estoque)

        # Adiciona campos de entrada e botão para criar ordem de serviço
        layout_principal.addWidget(self.cliente_input)
        layout_principal.addWidget(self.marca_os_input)
        layout_principal.addWidget(self.modelo_os_input)
        layout_principal.addWidget(self.descricao_os_input)
        layout_principal.addWidget(botao_criar_ordem_servico)
        layout_principal.addWidget(lista_ordens_servico)

        # Atualiza as listas na interface
        self.atualizar_lista_estoque()
        self.atualizar_lista_ordens_servico()

        self.show()

    def adicionar_produto(self):
        produto = self.produto_input.text()
        marca = self.marca_input.text()
        modelo = self.modelo_input.text()
        quantidade = self.quantidade_input.text()

        self.controle_estoque.adicionar_produto(produto, marca, modelo, quantidade)
        self.atualizar_lista_estoque()

    def criar_ordem_servico(self):
        cliente = self.cliente_input.text()
        marca = self.marca_os_input.text()
        modelo = self.modelo_os_input.text()
        descricao = self.descricao_os_input.text()

        self.controle_ordens_servico.criar_ordem_servico(cliente, marca, modelo, descricao)
        self.atualizar_lista_ordens_servico()

    def atualizar_lista_estoque(self):
        lista_estoque = self.findChild(QListWidget)
        if lista_estoque:
            lista_estoque.clear()
            estoque = self.controle_estoque.listar_estoque()
            for item in estoque:
                texto = f"{item[1]} - {item[2]} - {item[3]} - Quantidade: {item[4]}"
                lista_estoque.addItem(QListWidgetItem(texto))

    def atualizar_lista_ordens_servico(self):
        lista_ordens_servico = self.findChild(QListWidget)
        if lista_ordens_servico:
            lista_ordens_servico.clear()
            ordens_servico = self.controle_ordens_servico.listar_ordens_servico()
            for ordem in ordens_servico:
                texto = f"{ordem[0]} - {ordem[1]} - {ordem[2]} - {ordem[3]} - {ordem[5]}"
                lista_ordens_servico.addItem(QListWidgetItem(texto))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ControleAssistenciaGUI()
    sys.exit(app.exec_())
