import socket
import json

PORT_TCP = 5000
PORT_UDP = 5001

def buscar_servidor_automatico():
    """Tenta achar o IP do servidor via Broadcast UDP (Ponto Extra)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(2)
        try:
            s.sendto("ONDE_ESTA_O_SERVIDOR?".encode(), ('<broadcast>', PORT_UDP))
            data, addr = s.recvfrom(1024)
            return addr[0]
        except:
            return None

def main():
    print("=== SISTEMA ACADÊMICO - CLIENTE ===")
    ip = buscar_servidor_automatico()
    if not ip:
        ip = input("Servidor não encontrado. Digite o IP manualmente: ")

    print(f"Conectado ao servidor no IP: {ip}\n")
    
    while True:
        print("\nMENU:")
        print("1. Aluno (Lançar 3 Notas)")
        print("2. Coordenador (Ver Estatísticas/Relatórios)")
        print("3. Sair")
        opcao = input("Escolha: ")

        if opcao == '3': break

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip, PORT_TCP))
                
                if opcao == '1':
                    turma = input("Nome da Turma: ").upper()
                    n1 = float(input("Nota N1: "))
                    n2 = float(input("Nota N2: "))
                    n3 = float(input("Nota N3 (se não tiver, digite 0): "))
                    
                    dados = {"tipo": "ALUNO", "turma": turma, "n1": n1, "n2": n2, "n3": n3}
                    s.sendall(json.dumps(dados).encode())
                    
                    resp = json.loads(s.recv(1024).decode())
                    print(f"\n--- RESULTADO ---")
                    print(f"Média: {resp['media']} | Status: {resp['status']}")
                    print(f"Predição: {resp['predicao']}")
                    
                elif opcao == '2':
                    s.sendall(json.dumps({"tipo": "COORDENADOR"}).encode())
                    relatorio = s.recv(4096).decode()
                    print(relatorio)
        except Exception as e:
            print(f"Erro de conexão: {e}")

if __name__ == "__main__":
    main()