# decision_logic.py

class DecisionEngine:
    def __init__(self):
        # No futuro, pode carregar regras de um arquivo ou ter uma base de conhecimento mais complexa
        self.rules = {
            "ssh": [
                {"action": "bruteforce_ssh", "description": "Tentar força bruta SSH com lista de credenciais comuns?", "module": "SSHExploiter", "method": "attempt_bruteforce"},
                {"action": "check_ssh_vulns", "description": "Verificar vulnerabilidades conhecidas para a versão do SSH (se identificada)?", "module": "SSHExploiter", "method": "check_known_vulnerabilities"}
            ],
            "http": [
                {"action": "check_http_common_vulns", "description": "Verificar vulnerabilidades web comuns (XSS, cabeçalhos, etc.)?", "module": "HTTPExploiter", "method": "check_common_vulnerabilities"}
            ],
            "https": [
                {"action": "check_https_common_vulns", "description": "Verificar vulnerabilidades web comuns (XSS, cabeçalhos, etc.) em HTTPS?", "module": "HTTPExploiter", "method": "check_common_vulnerabilities"}
            ]
            # Adicionar mais regras para outros serviços (ftp, smtp, mysql, vnc, etc.)
        }

    def get_suggestions(self, service_name, port, service_details=None):
        """
        Gera sugestões de próximos passos com base no serviço identificado.

        :param service_name: Nome do serviço (ex: 'ssh', 'http').
        :param port: Porta onde o serviço está rodando.
        :param service_details: Dicionário com detalhes do serviço (versão, produto, etc. - vindo do Nmap).
        :return: Lista de dicionários de sugestões.
        """
        suggestions = []
        service_key = service_name.lower()

        if service_key in self.rules:
            for rule in self.rules[service_key]:
                suggestion_text = f"Serviço {service_name.upper()} na porta {port}. {rule['description']}"
                suggestions.append({
                    "text": suggestion_text,
                    "action_details": rule # Contém módulo, método, etc.
                })
        else:
            suggestions.append({
                "text": f"Serviço {service_name.upper()} na porta {port} detectado. Nenhuma ação automatizada pré-definida. Investigar manualmente?",
                "action_details": {"action": "manual_investigation", "description": "Investigação manual"}
            })
        
        return suggestions

if __name__ == '__main__':
    engine = DecisionEngine()
    
    ssh_suggestions = engine.get_suggestions("ssh", 22)
    print("Sugestões para SSH:")
    for s in ssh_suggestions:
        print(f"- {s['text']} (Ação: {s['action_details']['action']})")

    http_suggestions = engine.get_suggestions("http", 80)
    print("\nSugestões para HTTP:")
    for s in http_suggestions:
        print(f"- {s['text']} (Ação: {s['action_details']['action']})")

    ftp_suggestions = engine.get_suggestions("ftp", 21)
    print("\nSugestões para FTP (sem regra definida):")
    for s in ftp_suggestions:
        print(f"- {s['text']} (Ação: {s['action_details']['action']})")

