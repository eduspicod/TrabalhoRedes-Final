if msg['tipo'] == 'ALUNO':
            n1 = msg.get('n1', 0)
            n2 = msg.get('n2', 0)
            n3 = msg.get('n3', 0)
            
            if n3 == 0:
                media = (n1 + n2) / 2
                status = "Pendente (N3 faltante)"
                necessario = 21 - (n1 + n2) 
                pred = f"Precisa de {max(0, necessario):.1f} na N3 para passar sem PF"
            else:
                media = (n1 + n2 + n3) / 3
                if media >= 7: 
                    status = "Aprovado"
                elif media >= 4: 
                    status = "Prova Final"
                else: 
                    status = "Reprovado"
                pred = "Notas completas" 

            salvar_no_log(msg['turma'], media, status)
            
            resposta = {
                "media": round(media, 2), 
                "status": status, 
                "predicao": pred
            }
            conn.sendall(json.dumps(resposta).encode())