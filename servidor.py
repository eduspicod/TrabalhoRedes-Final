import socket
import threading
import json
import os
import statistics

HOST = '0.0.0.0'
PORT_TCP = 5000
PORT_UDP = 5001
LOG_FILE = 'dados_academicos.json'

def salvar_no_log(turma, media, status):
    """Guarda os dados para gerar o relatório do coordenador."""
    dados = {"turma": turma.upper(), "media": round(media, 2), "status": status}
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            try: 
                logs = json.load(f)
            except: 
                logs = []
    logs.append(dados)
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=4)

def gerar_relatorio_estatistico():
    """Gera o relatório agregado com Média, Moda, Mediana e Desvio Padrão."""
    if not os.path.exists(LOG_FILE):
        return "\n[!] Nenhum dado registrado no servidor ainda."

    with open(LOG_FILE, 'r') as f:
        logs = json.load(f)

    resumo = {}
    todas_as_medias = []

    for item in logs:
        t = item['turma']
        m = item['media']
        s = item['status']
        todas_as_medias.append(m)
        
        if t not in resumo:
            resumo[t] = {"Aprovado": 0, "Prova Final": 0, "Reprovado": 0, "Total": 0, "notas": []}
        
        if s in resumo[t]:
            resumo[t][s] += 1
        resumo[t]["Total"] += 1
        resumo[t]["notas"].append(m)

    saida = "\n======= RELATÓRIO ESTATÍSTICO (COORDENAÇÃO) =======\n"
    
    if len(todas_as_medias) >= 1:
        saida += f"ESTATÍSTICAS GERAIS (Soma de todas as turmas):\n"
        saida += f" - Média Geral: {statistics.mean(todas_as_medias):.2f}\n"
        saida += f" - Mediana: {statistics.median(todas_as_medias):.2f}\n"
        try:
            saida += f" - Moda: {statistics.mode(todas_as_medias):.2f}\n"
        except:
            saida += f" - Moda: (Múltiplas ou insuficientes)\n"
        if len(todas_as_medias) > 1:
            saida += f" - Desvio Padrão: {statistics.stdev(todas_as_medias):.2f}\n"
        saida += "="*50 + "\n"

    for turma, d in resumo.items():
        taxa_aprov = (d['Aprovado'] / d['Total']) * 100 if d['Total'] > 0 else 0
        saida += f"TURMA: {turma}\n"
        saida += f" - Alunos: {d['Total']} | Aprovados: {d['Aprovado']} ({taxa_aprov:.1f}%)\n"
        saida += f" - Perigando (PF): {d['Prova Final']} | Reprovados: {d['Reprovado']}\n"
        if len(d['notas']) > 1:
            saida += f" - Desvio Padrão da Turma: {statistics.stdev(d['notas']):.2f}\n"
        saida += "-"*50 + "\n"
        
    return saida

def handle_tcp_client(conn, addr):
    """Lida com a conexão TCP do Aluno ou Coordenador."""
    try:
        data = conn.recv(1024).decode()
        if not data:
            return
            
        msg = json.loads(data)

        if msg['tipo'] == 'ALUNO':
            n1 = msg.get('n1', 0)
            n2 = msg.get('n2', 0)
            n3 = msg.get('n3', 0)
            
            if n3 == 0:
                media = (n1 + n2) / 2
                status = "Pendente (Falta N3)"
                necessario = 21 - (n1 + n2)
                pred = f"Precisa de {max(0, necessario):.1f} na N3"
            else:
                media = (n1 + n2 + n3) / 3
                if media >= 7: status = "Aprovado"
                elif media >= 4: status = "Prova Final"
                else: status = "Reprovado"
                pred = "Notas completas"
            
            salvar_no_log(msg['turma'], media, status)
            
            resposta = {"media": round(media, 2), "status": status, "predicao": pred}
            conn.sendall(json.dumps(resposta).encode())

        elif msg['tipo'] == 'COORDENADOR':
            relatorio = gerar_relatorio_estatistico()
            conn.sendall(relatorio.encode())
            
    except Exception as e:
        print(f"Erro no cliente {addr}: {e}")
    finally:
        conn.close()

def servico_udp_discovery():
    """Broadcast UDP para descoberta automática (+1 ponto extra)"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('', PORT_UDP))
        while True:
            data, addr = s.recvfrom(1024)
            if data.decode() == "ONDE_ESTA_O_SERVIDOR?":
                s.sendto("EU_SOU_O_SERVIDOR".encode(), addr)

print("=== SERVIDOR ACADÊMICO ATIVO (TCP/UDP) ===")
threading.Thread(target=servico_udp_discovery, daemon=True).start()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT_TCP))
    server.listen()
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_tcp_client, args=(conn, addr)).start()