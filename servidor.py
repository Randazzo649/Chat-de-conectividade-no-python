import socket as sock
import threading
from datetime import datetime

lista_clientes = []


def recebe_dados(socket_cliente, endereco):
    ip_cliente, porta_cliente = endereco
    try:
        nome = socket_cliente.recv(50).decode()
        lista_clientes.append((socket_cliente, nome))
        print(f"Conexão bem-sucedida com {nome} (IP: {ip_cliente}, Porta: {porta_cliente})")
        broadcast(f"{nome} entrou no chat!", socket_cliente)
        while True:
            try:
                mensagem = socket_cliente.recv(1024).decode()
                if mensagem:
                    if mensagem.startswith('@'): 
                        nome_destino, msg = tratar_unicast(mensagem)
                        enviar_unicast(nome, nome_destino, msg, socket_cliente)
                    else:
                        horario = datetime.now().strftime("%H:%M:%S")
                        print(f"[{horario}] {nome}: {mensagem}")
                        broadcast(f"[{horario}] {nome}: {mensagem}", socket_cliente)
                else:
                    raise Exception("Cliente desconectado")
            except:
                remover(socket_cliente, nome)
                break
    except Exception as e:
        print(f"Erro ao conectar cliente: {e}")
        socket_cliente.close()


def tratar_unicast(mensagem):
    try:
        nome_destino, msg = mensagem[1:].split(' ', 1)
        return nome_destino.strip(), msg.strip()
    except ValueError:
        return None, None


def broadcast(mensagem, cliente_excluido=None):
    for cliente, nome in lista_clientes:
        if cliente != cliente_excluido:
            try:
                cliente.send(mensagem.encode())
            except:
                remover(cliente, nome)


def enviar_unicast(nome_origem, nome_destino, mensagem, remetente):
    """Envia uma mensagem privada para o destinatário especificado."""
    if not nome_destino or not mensagem:
        remetente.send("[Servidor] Formato inválido! Use: @destinatario mensagem".encode())
        return

    horario = datetime.now().strftime("%H:%M:%S")
    for cliente, nome in lista_clientes:
        if nome == nome_destino:
            try:
                cliente.send(f"[{horario}] [Privado de {nome_origem}] {mensagem}".encode())
                remetente.send(f"[{horario}] [Privado para {nome_destino}] {mensagem}".encode())
                return
            except:
                remover(cliente, nome)
                return
    remetente.send(f"[Servidor] Usuário {nome_destino} não encontrado.".encode())


def remover(cliente, nome):
    for c, n in lista_clientes:
        if c == cliente:
            lista_clientes.remove((c, n))
            break
    cliente.close()
    broadcast(f"{nome} saiu do chat.")


HOST = '127.0.0.1'
PORTA = 9999
sock_server = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
sock_server.bind((HOST, PORTA))
sock_server.listen()
print(f"O servidor {HOST}:{PORTA} está aguardando conexões...")

while True:
    sock_conn, ender = sock_server.accept()
    thread_cliente = threading.Thread(target=recebe_dados, args=(sock_conn, ender))
    thread_cliente.start()