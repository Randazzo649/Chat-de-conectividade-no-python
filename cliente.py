import socket as sock
import threading

HOST = '127.0.0.1'
PORTA = 9999
socket_cliente = sock.socket(sock.AF_INET, sock.SOCK_STREAM)

socket_cliente.connect((HOST, PORTA))
print(5 * "-" + " CHAT INICIADO " + 5 * "-")
print("Digite 'sair' para sair do chat")
print("Para mandar uma mensagem privada, siga o formato: @nome mensagem")

nome = input("Informe seu nome para entrar no chat: ")
socket_cliente.sendall(nome.encode())

def receber_mensagens():
    while True:
        try:
            mensagem = socket_cliente.recv(1024).decode()
            if mensagem:
                print(mensagem)
            else:
                break
        except:
            print("Erro ao receber mensagem.")
            break

def enviar_mensagens():
    while True:
        try:
            mensagem = input('')
            if mensagem.lower() == 'sair':
                socket_cliente.sendall(f"{nome} saiu do chat.".encode())
                break
            socket_cliente.sendall(mensagem.encode())
        except KeyboardInterrupt:
            print("\nSaindo do chat...")
            break
    socket_cliente.close()

thread_receber = threading.Thread(target=receber_mensagens)
thread_receber.start()

try:
    enviar_mensagens()
except Exception as e:
    print(f"Erro: {e}")
    socket_cliente.close()