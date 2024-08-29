import textwrap
from abc import ABC, abstractmethod
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def criar_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor > self._saldo:
            print("\n@@@ Erro: Saldo insuficiente. @@@")
            return False

        if valor <= 0:
            print("\n@@@ Erro: Valor de saque inválido. @@@")
            return False

        self._saldo -= valor
        print("\n=== Saque efetuado com sucesso! ===")
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("\n@@@ Erro: Valor de depósito inválido. @@@")
            return False

        self._saldo += valor
        print("\n=== Depósito realizado com sucesso! ===")
        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        if valor > self.limite:
            print("\n@@@ Erro: Limite de saque excedido. @@@")
            return False

        if numero_saques >= self.limite_saques:
            print("\n@@@ Erro: Limite de saques atingido. @@@")
            return False

        return super().sacar(valor)

    def __str__(self):
        return f"""\
        Agência: {self.agencia}
        Número da Conta: {self.numero}
        Titular: {self.cliente.nome}\
        """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def registrar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.sacar(self._valor):
            conta.historico.registrar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self._valor):
            conta.historico.registrar_transacao(self)


# Função centralizada para capturar e validar CPF
def capturar_cpf(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = next((cliente for cliente in clientes if cliente.cpf == cpf), None)
    if cliente is None:
        print("\n@@@ Cliente não encontrado! @@@")
    return cliente


def menu():
    cabecalho_menu()
    menu_opcoes = """\n
    [d] Depositar
    [s] Sacar
    [e] Extrato
    [nc] Nova conta
    [lc] Listar contas
    [nu] Novo cliente
    [q] Sair
    => """
    return input(textwrap.dedent(menu_opcoes))


def cabecalho_menu():
    print("\n================ BANCO ==================")


def depositar(clientes):
    cliente = capturar_cpf(clientes)
    if not cliente:
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if conta:
        cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    cliente = capturar_cpf(clientes)
    if not cliente:
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if conta:
        cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
    cliente = capturar_cpf(clientes)
    if not cliente:
        return

    conta = recuperar_conta_cliente(cliente)
    if conta:
        print("\n=========== EXTRATO ===========")
        transacoes = conta.historico.transacoes

        if transacoes:
            for transacao in transacoes:
                print(f"{transacao['tipo']}:\tR$ {transacao['valor']:.2f} em {transacao['data']}")
        else:
            print("Nenhuma transação realizada.")

        print(f"\nSaldo Atual: R$ {conta.saldo:.2f}")
        print("===============================")


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return None

    return cliente.contas[0]  # Pode ser expandido para selecionar conta


def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente números): ")
    if any(cliente.cpf == cpf for cliente in clientes):
        print("\n@@@ CPF já cadastrado! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)
    clientes.append(cliente)

    print("\n=== Cliente cadastrado com sucesso! ===")


def criar_conta(numero_conta, clientes, contas):
    cliente = capturar_cpf(clientes)
    if not cliente:
        return

    conta = ContaCorrente.criar_conta(cliente, numero_conta)
    contas.append(conta)
    cliente.adicionar_conta(conta)

    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    if not contas:
        print("\n@@@ Nenhuma conta cadastrada. @@@")
        return

    for conta in contas:
        print("=" * 40)
        print(str(conta))


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)
        elif opcao == "s":
            sacar(clientes)
        elif opcao == "e":
            exibir_extrato(clientes)
        elif opcao == "nu":
            criar_cliente(clientes)
        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)
        elif opcao == "lc":
            listar_contas(contas)
        elif opcao == "q":
            break
        else:
            print("\n@@@ Opção inválida! @@@")

main()
